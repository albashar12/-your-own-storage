import os
import mimetypes
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import sqlite3
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_own_vault_secret_key_999")

# Telegram Bot API Credentials (No API_ID or API_HASH needed anymore!)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

if CHANNEL_ID:
    CHANNEL_ID = int(CHANNEL_ID)

# Database Setup
DB_NAME = "storage_vault.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                sec_question TEXT NOT NULL,
                sec_answer TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS stored_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_id TEXT NOT NULL,
                mime_type TEXT,
                file_size INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()

init_db()

# Telegram HTTP API Storage Helpers (Stateless & Fast)
def upload_to_storage(file_bytes, filename):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (filename, file_bytes)}
    data = {'chat_id': CHANNEL_ID}
    
    try:
        response = requests.post(url, data=data, files=files)
        if response.status_code == 200:
            res_json = response.json()
            # টেলিগ্রাম থেকে ফাইলের ইউনিক telegram file_id রিটার্ন করা হচ্ছে
            doc_file_id = res_json['result']['document']['file_id']
            return doc_file_id
    except Exception as e:
        print(f"Upload error: {e}")
    return None

def download_from_storage(file_id):
    try:
        # ১. টেলিগ্রাম থেকে ফাইলের সার্ভার পাথ ফেচ করা
        get_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
        res = requests.get(get_file_url).json()
        
        if res.get('ok'):
            file_path = res['result']['file_path']
            # ২. টেলিগ্রাম সার্ভার থেকে ফাইল বাইট ডাউনলোড করা
            download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            file_res = requests.get(download_url)
            return BytesIO(file_res.content)
    except Exception as e:
        print(f"Download error: {e}")
        
    return BytesIO()

# Routes

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('is_admin') == 1:
            return redirect(url_for('admin_panel'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        sec_question = request.form['sec_question'].strip()
        sec_answer = request.form['sec_answer'].strip().lower()
        
        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if user:
                flash("Username already exists. Please choose another.", "error")
                return redirect(url_for('register'))
            
            count = conn.execute('SELECT COUNT(*) as cnt FROM users').fetchone()['cnt']
            is_admin = 1 if count == 0 else 0
            
            conn.execute(
                'INSERT INTO users (username, password, sec_question, sec_answer, is_admin) VALUES (?, ?, ?, ?, ?)',
                (username, password, sec_question, sec_answer, is_admin)
            )
            conn.commit()
            
        flash("Vault Account created successfully! Please login.", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = user['is_admin']
                
                if user['is_admin'] == 1:
                    return redirect(url_for('admin_panel'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                flash("Invalid username or password.", "error")
                
    return render_template('login.html')

@app.route('/reset', methods=['GET', 'POST'])
def reset_password():
    user_data = None
    if request.method == 'POST':
        if 'step' in request.form and request.form['step'] == 'find':
            username = request.form['username'].strip()
            with get_db() as conn:
                user_data = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
                if not user_data:
                    flash("Username not found.", "error")
        elif 'step' in request.form and request.form['step'] == 'reset':
            username = request.form['username']
            sec_answer = request.form['sec_answer'].strip().lower()
            new_password = request.form['new_password']
            
            with get_db() as conn:
                user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
                if user and user['sec_answer'] == sec_answer:
                    conn.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user['id']))
                    conn.commit()
                    flash("Password reset successfully. Please login.", "success")
                    return redirect(url_for('login'))
                else:
                    flash("Incorrect security answer.", "error")
                    
    return render_template('reset.html', user=user_data)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    
    if request.method == 'POST':
        uploaded_files = request.files.getlist('file')
        if not uploaded_files or uploaded_files[0].filename == '':
            flash("No file selected.", "error")
            return redirect(url_for('dashboard'))
            
        for file in uploaded_files:
            if file.filename == '':
                continue
                
            filename = file.filename
            mime_type = file.mimetype
            file_bytes = file.read()
            file_size = len(file_bytes)
            
            telegram_file_id = upload_to_storage(file_bytes, filename)
            
            if telegram_file_id:
                with get_db() as conn:
                    conn.execute(
                        'INSERT INTO stored_files (user_id, filename, file_id, mime_type, file_size) VALUES (?, ?, ?, ?, ?)',
                        (user_id, filename, telegram_file_id, mime_type, file_size)
                    )
                    conn.commit()
            
        flash("Files successfully stored via Bot API!", "success")
        return redirect(url_for('dashboard'))

    with get_db() as conn:
        files = conn.execute('SELECT * FROM stored_files WHERE user_id = ? ORDER BY id DESC', (user_id,)).fetchall()
        
    return render_template('dashboard.html', files=files)

@app.route('/view/<int:file_id>')
def view_file(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    with get_db() as conn:
        file_rec = conn.execute('SELECT * FROM stored_files WHERE id = ? AND user_id = ?', (file_id, session['user_id'])).fetchone()
        
    if not file_rec:
        flash("File not found.", "error")
        return redirect(url_for('dashboard'))
        
    try:
        buffer = download_from_storage(file_rec['file_id'])
        
        mime_type = file_rec['mime_type']
        if not mime_type or mime_type == 'application/octet-stream':
            mime_type, _ = mimetypes.guess_type(file_rec['filename'])
            if not mime_type:
                mime_type = 'application/octet-stream'
                
        return send_file(buffer, mimetype=mime_type, download_name=file_rec['filename'])
    except Exception as e:
        print(f"Error viewing file: {e}")
        flash("Could not load file from storage.", "error")
        return redirect(url_for('dashboard'))

@app.route('/download/<int:file_id>')
def download(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    with get_db() as conn:
        file_rec = conn.execute('SELECT * FROM stored_files WHERE id = ? AND user_id = ?', (file_id, session['user_id'])).fetchone()
        
    if not file_rec:
        flash("File not found.", "error")
        return redirect(url_for('dashboard'))
        
    try:
        buffer = download_from_storage(file_rec['file_id'])
        return send_file(buffer, as_attachment=True, download_name=file_rec['filename'])
    except Exception as e:
        print(f"Error downloading file: {e}")
        flash("Could not download file from storage.", "error")
        return redirect(url_for('dashboard'))

@app.route('/admin-vault')
def admin_panel():
    if 'user_id' not in session or session.get('is_admin') != 1:
        flash("Unauthorized access.", "error")
        return redirect(url_for('dashboard'))
        
    with get_db() as conn:
        all_users = conn.execute('SELECT id, username, password, sec_question, sec_answer, is_admin FROM users').fetchall()
        
    return render_template('admin.html', users=all_users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
