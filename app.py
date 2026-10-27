import os
import asyncio
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import sqlite3
from telethon import TelegramClient
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_own_vault_secret_key_999")

# Environment Variables for Storage Engine
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
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

# Async Storage Helpers
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

async def upload_to_storage(file_bytes, filename):
    client = TelegramClient('bot_session', int(API_ID), API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    message = await client.send_file(
        CHANNEL_ID,
        file_bytes,
        caption=filename,
        force_document=True  # 100% original quality loss-less storage
    )
    await client.disconnect()
    return message.id

async def download_from_storage(message_id):
    client = TelegramClient('bot_session', int(API_ID), API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    buffer = BytesIO()
    await client.download_media(message_id, buffer)
    await client.disconnect()
    buffer.seek(0)
    return buffer

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
            
            # First account created in the system automatically becomes the stealth admin
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
                
                # Dynamic Redirect Logic based on User Privileges
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
        if 'file' not in request.files:
            flash("No file selected.", "error")
            return redirect(url_for('dashboard'))
            
        file = request.files['file']
        if file.filename == '':
            flash("No file selected.", "error")
            return redirect(url_for('dashboard'))
            
        filename = file.filename
        file_bytes = file.read()
        file_size = len(file_bytes)
        
        message_id = run_async(upload_to_storage(file_bytes, filename))
        
        with get_db() as conn:
            conn.execute(
                'INSERT INTO stored_files (user_id, filename, file_id, file_size) VALUES (?, ?, ?, ?)',
                (user_id, filename, str(message_id), file_size)
            )
            conn.commit()
            
        flash("File securely stored in original quality!", "success")
        return redirect(url_for('dashboard'))

    with get_db() as conn:
        files = conn.execute('SELECT * FROM stored_files WHERE user_id = ? ORDER BY id DESC', (user_id,)).fetchall()
        
    return render_template('dashboard.html', files=files)

@app.route('/download/<int:file_id>')
def download(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    with get_db() as conn:
        file_rec = conn.execute('SELECT * FROM stored_files WHERE id = ? AND user_id = ?', (file_id, session['user_id'])).fetchone()
        
    if not file_rec:
        flash("File not found.", "error")
        return redirect(url_for('dashboard'))
        
    buffer = run_async(download_from_storage(int(file_rec['file_id'])))
    return send_file(buffer, as_attachment=True, download_name=file_rec['filename'])

# Admin Dashboard (Accessed directly after Admin login)
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