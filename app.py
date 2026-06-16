from flask import Flask, request, jsonify, render_template
import urllib.request
import urllib.parse
import json
import re
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
        # YouTube ke search page se direct HTML data nikalna safely
        encoded_search = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_search}"
        
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
        # HTML ke andar se YouTube ka hidden JSON data nikalna regex se
        json_data_match = re.search(r'ytInitialData\s*=\s*({.+?});', html)
        if json_data_match:
            json_str = json_data_match.group(1)
            data = json.loads(json_str)
            
            # JSON parse karke videos nikalna
            contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
            
            count = 0
            for item in contents:
                if 'videoRenderer' in item and count < 6:
                    video = item['videoRenderer']
                    video_id = video.get('videoId')
                    
                    # Fallback check thumbnails ke liye
                    thumb = ""
                    if 'thumbnails' in video.get('thumbnail', {}):
                        thumb = video['thumbnail']['thumbnails'][0]['url']

                    results.append({
                        'id': video_id,
                        'title': video['title']['runs'][0]['text'],
                        'artist': video['ownerText']['runs'][0]['text'] if 'ownerText' in video else 'Unknown Artist',
                        'thumbnail': thumb,
                        'source': f"/api/stream?url=https://www.youtube.com/watch?v={video_id}"
                    })
                    count += 1
    except Exception as e:
        print(f"Bulletproof Search Error: {e}")
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
            return jsonify(stream_url)
    except Exception as e:
        print(f"Streaming error: {e}")
        return jsonify({'error': 'Cannot stream video'}), 500

if __name__ == '__main__':
    app.run(debug=True)
