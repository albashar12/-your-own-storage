<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Own Vault - Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: linear-gradient(135deg, #0f172a, #1e1b4b, #09090b); color: #f8fafc; min-height: 100vh; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); padding: 20px 30px; border-radius: 16px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); margin-bottom: 30px; }
        h2 { font-size: 24px; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .logout-btn { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #f87171; padding: 8px 18px; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s ease; }
        .logout-btn:hover { background: rgba(239, 68, 68, 0.3); box-shadow: 0 0 15px rgba(239, 68, 68, 0.4); }
        
        .card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); padding: 25px; border-radius: 16px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); margin-bottom: 30px; }
        .card h3 { margin-bottom: 15px; font-size: 18px; color: #38bdf8; }
        
        .input-group { margin-bottom: 15px; }
        input[type="file"], input[type="text"], textarea { width: 100%; padding: 12px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; color: white; font-size: 14px; }
        textarea { resize: vertical; height: 90px; }
        input:focus, textarea:focus { outline: none; border-color: #38bdf8; box-shadow: 0 0 10px rgba(56, 189, 248, 0.3); }
        
        button[type="submit"] { background: linear-gradient(135deg, #0284c7, #4f46e5); color: white; border: none; padding: 10px 24px; font-size: 15px; font-weight: 600; border-radius: 8px; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 0 20px rgba(56, 189, 248, 0.3); }
        button[type="submit"]:hover { transform: translateY(-2px); box-shadow: 0 0 25px rgba(99, 102, 241, 0.6); }
        
        .progress-container { display: none; margin-top: 15px; width: 100%; background: rgba(15, 23, 42, 0.8); border-radius: 8px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.1); }
        .progress-bar { width: 0%; height: 20px; background: linear-gradient(90deg, #0284c7, #38bdf8); text-align: center; color: white; font-size: 11px; font-weight: 600; line-height: 20px; transition: width 0.2s ease; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 15px; margin-top: 15px; }
        .item-card { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); padding: 16px; border-radius: 12px; display: flex; flex-direction: column; justify-content: space-between; }
        .thumb-container { width: 100%; height: 130px; margin-bottom: 10px; border-radius: 8px; overflow: hidden; background: rgba(0, 0, 0, 0.2); display: flex; align-items: center; justify-content: center; }
        .thumb-img { width: 100%; height: 100%; object-fit: cover; }
        .item-title { font-size: 15px; font-weight: 600; margin-bottom: 8px; color: #f8fafc; word-break: break-all; }
        .item-content { font-size: 13px; color: #cbd5e1; margin-bottom: 12px; word-break: break-all; white-space: pre-wrap; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 6px; }
        
        .btn-link { display: block; text-align: center; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.3); color: #38bdf8; padding: 7px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 13px; transition: 0.3s; }
        .btn-link:hover { background: rgba(56, 189, 248, 0.3); }
        .btn-danger { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #f87171; }
        .btn-danger:hover { background: rgba(239, 68, 68, 0.3); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h2>🛡️ Your Own Vault</h2>
            <a href="/logout" class="logout-btn">Logout</a>
        </header>
        
        <!-- File Upload Section -->
        <div class="card">
            <h3>📁 Upload Files</h3>
            <form id="uploadForm" action="/dashboard" method="POST" enctype="multipart/form-data">
                <input type="hidden" name="action" value="upload">
                <div class="input-group">
                    <input type="file" name="file" id="fileInput" multiple required>
                </div>
                <button type="submit" id="uploadBtn">Upload Files</button>
            </form>
            <div class="progress-container" id="progressContainer">
                <div class="progress-bar" id="progressBar">0%</div>
            </div>
        </div>

        <!-- Secure Notes & Information Section -->
        <div class="card">
            <h3>🔐 Add Information, Birthdays & Notes</h3>
            <form action="/dashboard" method="POST">
                <input type="hidden" name="action" value="add_note">
                <div class="input-group">
                    <input type="text" name="title" placeholder="Title (e.g., Friends Birthdays, Passwords)..." required>
                </div>
                <div class="input-group">
                    <textarea name="content" placeholder="Write details here..." required></textarea>
                </div>
                <button type="submit">Save Info / Note</button>
            </form>
        </div>
        
        <!-- Stored Notes Section -->
        <div class="card">
            <h3>📝 Saved Information & Birthdays</h3>
            <div class="grid">
                {% for note in notes %}
                <div class="item-card">
                    <div>
                        <div class="item-title">📌 {{ note.title }}</div>
                        <div class="item-content">{{ note.content }}</div>
                    </div>
                    <a href="/delete_note/{{ note.id }}" class="btn-link btn-danger" onclick="return confirm('Delete this note?')">Delete Note</a>
                </div>
                {% else %}
                <p style="color: #64748b; font-size: 14px;">No notes or birthdays saved yet.</p>
                {% endfor %}
            </div>
        </div>

        <!-- Stored Files Section -->
        <div class="card">
            <h3>📂 Stored Files</h3>
            <div class="grid">
                {% for file in files %}
                <div class="item-card">
                    {% if file.mime_type and file.mime_type.startswith('image/') %}
                    <div class="thumb-container">
                        <img src="/view/{{ file.id }}" alt="{{ file.filename }}" class="thumb-img">
                    </div>
                    {% endif %}
                    <div class="item-title" style="font-size: 14px;">{{ file.filename }}</div>
                    <a href="/view/{{ file.id }}" target="_blank" class="btn-link">View / Download</a>
                </div>
                {% else %}
                <p style="color: #64748b; font-size: 14px;">No files uploaded yet.</p>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('uploadForm');
        const progressContainer = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');
        const uploadBtn = document.getElementById('uploadBtn');

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('fileInput');
            if (fileInput.files.length === 0) return;

            const formData = new FormData(form);
            const xhr = new XMLHttpRequest();

            xhr.open('POST', '/dashboard', true);

            xhr.upload.addEventListener('progress', function(e) {
                if (e.lengthComputable) {
                    const percentComplete = Math.round((e.loaded / e.total) * 100);
                    progressContainer.style.display = 'block';
                    progressBar.style.width = percentComplete + '%';
                    progressBar.innerHTML = percentComplete + '% Uploading...';
                    uploadBtn.disabled = true;
                    uploadBtn.style.opacity = '0.6';
                }
            });

            xhr.onload = function() {
                if (xhr.status === 200) {
                    progressBar.innerHTML = 'Upload Complete!';
                    setTimeout(() => {
                        window.location.reload();
                    }, 500);
                } else {
                    alert('Upload failed. Please try again.');
                    uploadBtn.disabled = false;
                    uploadBtn.style.opacity = '1';
                }
            };

            xhr.onerror = function() {
                alert('An error occurred during upload.');
                uploadBtn.disabled = false;
                uploadBtn.style.opacity = '1';
            };

            xhr.send(formData);
        });
    </script>
</body>
</html>
