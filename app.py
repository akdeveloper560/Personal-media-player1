from flask import Flask, request, jsonify, render_template
import yt_dlp
import os

# Render ke liye exact absolute path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, 
            template_folder=current_dir, 
            static_folder=current_dir, 
            static_url_path='')

@app.route('/')
def index():
    # Yeh aapki HTML file ko serve karega
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def search_songs():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    # yt-dlp configuration direct MP3/Audio link nikalne ke liye
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': False,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Online search matching top 5 results
            search_results = ydl.extract_info(f"ytsearch5:{query}", download=False)
            
            songs = []
            if 'entries' in search_results:
                for entry in search_results['entries']:
                    if not entry:
                        continue
                        
                    # Pure Direct Streaming URL nikalna (Bypasses all iframe blocks)
                    stream_url = entry.get('url')
                    
                    songs.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'artist': entry.get('uploader', 'Unknown Artist'),
                        'thumbnail': entry.get('thumbnail') or f"https://img.youtube.com/vi/{entry.get('id')}/mqdefault.jpg",
                        'source': stream_url # Yeh direct browser audio engine ke liye hai
                    })
            
            return jsonify(songs)
            
    except Exception as e:
        print(f"Error fetching tracks: {e}")
        return jsonify([]), 500


import os

if __name__ == '__main__':
    # Render dynamic port provide karta hai, agar na mile toh default 5000 chalega
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
