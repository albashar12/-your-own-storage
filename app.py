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
    print(f"Restore error (Ignored to prevent crash): {e}")
      
