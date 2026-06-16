from flask import Flask, request, jsonify, render_template
import urllib.request
import urllib.parse
import json
import re
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
        encoded_search = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_search}"
        
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
        json_data_match = re.search(r'ytInitialData\s*=\s*({.+?});', html)
        if json_data_match:
            json_str = json_data_match.group(1)
            data = json.loads(json_str)
            
            contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
            
            count = 0
            for item in contents:
                if 'videoRenderer' in item and count < 6:
                    video = item['videoRenderer']
                    video_id = video.get('videoId')
                    
                    thumb = ""
                    if 'thumbnails' in video.get('thumbnail', {}):
                        thumb = video['thumbnail']['thumbnails'][0]['url']

                    results.append({
                        'id': video_id,
                        'title': video['title']['runs'][0]['text'],
                        'artist': video['ownerText']['runs'][0]['text'] if 'ownerText' in video else 'Unknown Artist',
                        'thumbnail': thumb,
                        'source': video_id  # Ab hum sirf Video ID bhejenge frontend ko
                    })
                    count += 1
    except Exception as e:
        print(f"Search Error: {e}")
        return jsonify([])

    return jsonify(results)

# Bulletproof Stream Engine: YouTube Server se bachne ke liye Public API Engine
@app.route('/api/stream')
def stream_audio():
    video_id = request.args.get('id', '')
    if not video_id:
        return jsonify({'error': 'No Video ID provided'}), 400

    # Invidious public instances ki list jo direct audio URLs deti hain bina kisi bot check ke
    instances = [
        f"https://invidious.projectsegfau.lt/api/v1/videos/{video_id}",
        f"https://yewtu.be/api/v1/videos/{video_id}",
        f"https://inv.nadeko.net/api/v1/videos/{video_id}"
    ]

    for api_url in instances:
        try:
            req = urllib.request.Request(
                api_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                if 'adaptiveFormats' in data:
                    # Sirf audio stream dhoondna jiska resolution na ho (pure audio)
                    for fmt in data['adaptiveFormats']:
                        if 'audio' in fmt.get('type', '') or fmt.get('audioQuality'):
                            return jsonify(fmt.get('url'))
        except Exception as e:
            print(f"Instance failed, trying next: {e}")
            continue

    # Ulti-fallback agar sab instances down hon, toh direct YouTube audio stream bypass link return karenge client-side playback ke liye
    return jsonify(f"https://www.youtube.com/watch?v={video_id}")

if __name__ == '__main__':
    app.run(debug=True)
