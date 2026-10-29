import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import io

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super_secret_key_vault")

# Telegram Bot Credentials
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

DB_NAME = "storage_vault.db"

# --- TELEGRAM AUTO-BACKUP & RESTORE FUNCTIONS ---
def restore_db_from_telegram():
    if not BOT_TOKEN or not CHANNEL_ID:
        return
    try:
        url = f"{TELEGRAM_API_URL}/getUpdates"
        res = requests.get(url, timeout=10).json()
        
        latest_file_id = None
        if res.get("ok"):
            for result in res.get("result", []):
                message = result.get("message", {}) or result.get("channel_post", {})
                document = message.get("document")
                if document and document.get("file_name") == DB_NAME:
                    latest_file_id = document.get("file_id")
        
        if latest_file_id:
            file_info_url = f"{TELEGRAM_API_URL}/getFile?file_id={latest_file_id}"
            file_info = requests.get(file_info_url, timeout=10).json()
            if file_info.get("ok"):
                file_path = file_info["result"]["file_path"]
                download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                db_data = requests.get(download_url, timeout=15).content
                with open(DB_NAME, "wb") as f:
                    f.write(db_data)
                print("Database successfully restored from Telegram!")
    except Exception as e:
        print(f"Restore error (Ignored): {e}")

def backup_db_to_telegram():
    if not BOT_TOKEN or not CHANNEL_ID or not os.path.exists(DB_NAME):
        return
    try:
        url = f"{TELEGRAM_API_URL}/sendDocument"
        with open(DB_NAME, "rb") as f:
            files = {"document": (DB_NAME, f)}
            data = {"chat_id": CHANNEL_ID, "caption": "Auto-Backup of Vault Database"}
            requests.post(url, data=data, files=files, timeout=15)
    except Exception as e:
        print(f"Backup error: {e}")

# --- DATABASE INITIALIZATION ---
def init_db():
    try:
        restore_db_from_telegram()
    except Exception as e:
        print(f"Skipping restore due to: {e}")
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT NOT NULL,
            telegram_file_id TEXT NOT NULL,
            mime_type TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            backup_db_to_telegram()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists!"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('dashboard'))
        return "Invalid credentials!"
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        uploaded_files = request.files.getlist('file')
        for file in uploaded_files:
            if file.filename:
                file_bytes = file.read()
                mime_type = file.mimetype
                
                tg_url = f"{TELEGRAM_API_URL}/sendDocument"
                files_payload = {'document': (file.filename, io.BytesIO(file_bytes), mime_type)}
                data_payload = {'chat_id': CHANNEL_ID, 'caption': f'User ID: {user_id}'}
                
                res = requests.post(tg_url, data=data_payload, files=files_payload).json()
                if res.get('ok'):
                    telegram_file_id = res['result']['document']['file_id']
                    
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO files (user_id, filename, telegram_file_id, mime_type) VALUES (?, ?, ?, ?)",
                                   (user_id, file.filename, telegram_file_id, mime_type))
                    conn.commit()
                    conn.close()
        
        backup_db_to_telegram()
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, mime_type FROM files WHERE user_id = ?", (user_id,))
    files = [{'id': row[0], 'filename': row[1], 'mime_type': row[2]} for row in cursor.fetchall()]
    conn.close()
    
    return render_template('dashboard.html', files=files)

@app.route('/view/<int:file_id>')
def view_file(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_file_id, filename, mime_type FROM files WHERE id = ? AND user_id = ?", (file_id, session['user_id']))
    file_data = cursor.fetchone()
    conn.close()
    
    if not file_data:
        return "File not found", 404
        
    telegram_file_id, filename, mime_type = file_data
    
    file_info_url = f"{TELEGRAM_API_URL}/getFile?file_id={telegram_file_id}"
    info_res = requests.get(file_info_url).json()
    if info_res.get('ok'):
        file_path = info_res['result']['file_path']
        download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        file_content = requests.get(download_url).content
        return send_file(io.BytesIO(file_content), mimetype=mime_type, download_name=filename)
    
    return "Could not fetch file", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
