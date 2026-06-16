from flask import Flask, request, jsonify, render_template
from youtubesearchpython import VideosSearch
import yt_dlp
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, 
            template_folder=current_dir, 
            static_folder=current_dir, 
            static_url_path='')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    results = []
    try:
        # Yeh library bina kisi bot error ke data nikalegi
        videos_search = VideosSearch(query, limit=5)
        search_result = videos_search.result()

        if 'result' in search_result:
            for video in search_result['result']:
                # Har video ka direct play stream link nikalne ke liye yt-dlp backup use karenge
                video_url = video.get('link')
                
                results.append({
                    'id': video.get('id'),
                    'title': video.get('title'),
                    'artist': video.get('channel', {}).get('name', 'Unknown Artist'),
                    'thumbnail': video.get('thumbnails', [{}])[0].get('url', ''),
                    'source': f"/api/stream?url={video_url}" # Direct route to stream audio safely
                })
    except Exception as e:
        print(f"Search Extraction Error: {e}")
        return jsonify([])

    return jsonify(results)

@app.route('/api/stream')
def stream_audio():
    video_url = request.args.get('url', '')
    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            # Redirect browser direct to audio stream link
            return jsonify(stream_url) 
    except Exception as e:
        print(f"Streaming error: {e}")
        return jsonify({'error': 'Cannot stream video'}), 500

if __name__ == '__main__':
    app.run(debug=True)
