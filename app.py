from flask import Flask, render_template, request, send_file, jsonify
import os
from youtube_down_python import download_transcripts, get_video_ids_from_playlist
import threading
import queue

app = Flask(__name__)

# Kolejka do przechowywania statusów pobierania
download_status = queue.Queue()

def process_download(url):
    try:
        video_ids = get_video_ids_from_playlist(url)
        download_status.put({"status": "start", "total": len(video_ids)})
        
        # Zmiana katalogu roboczego na /app/downloads przed pobieraniem
        os.chdir('/app/downloads')
        download_transcripts(video_ids)
        download_status.put({"status": "complete"})
    except Exception as e:
        download_status.put({"status": "error", "message": str(e)})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return jsonify({"error": "Brak URL"}), 400
    
    # Rozpocznij pobieranie w osobnym wątku
    threading.Thread(target=process_download, args=(url,)).start()
    return jsonify({"message": "Rozpoczęto pobieranie"})

@app.route('/status')
def status():
    try:
        status = download_status.get_nowait()
        return jsonify(status)
    except queue.Empty:
        return jsonify({"status": "waiting"})

@app.route('/downloads')
def list_downloads():
    files = []
    downloads_dir = '/app/downloads'
    for file in os.listdir(downloads_dir):
        if file.endswith(('.txt', '.srt')):
            files.append(file)
    return jsonify({"files": files})

@app.route('/download_file/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join('/app/downloads', filename),
            as_attachment=True
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    os.makedirs('/app/downloads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000) 