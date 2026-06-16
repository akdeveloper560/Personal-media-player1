from flask import Flask, request, jsonify, render_template
import urllib.request
import urllib.parse
import json
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
        # JioSaavn Saavn-API bypass system (100% stable aur free)
        encoded_query = urllib.parse.quote(query)
        url = f"https://saavn.dev/api/search/songs?query={encoded_query}"
        
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        if data.get('success') and 'data' in data and 'results' in data['data']:
            songs_data = data['data']['results']
            
            for song in songs_data[:10]:  # Top 10 results nikalenge
                # Sabse high quality audio stream (320kbps ya 128kbps) dhoondna
                download_urls = song.get('downloadUrl', [])
                stream_url = download_urls[-1].get('url') if download_urls else ""
                
                # High quality image dhoondna
                images = song.get('image', [])
                thumb = images[-1].get('url') if images else ""

                results.append({
                    'id': song.get('id'),
                    'title': song.get('name'),
                    'artist': song.get('primaryArtists', 'Unknown Artist'),
                    'thumbnail': thumb,
                    'source': stream_url  # Direct playing MP3 link bina kisi bot check ke
                })
    except Exception as e:
        print(f"Saavn Search Error: {e}")
        return jsonify([])

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
