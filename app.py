from flask import Flask, request, jsonify, render_template
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

    # BYPASS OPTIONS: Isse YouTube server par error nahi dega
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch:5',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }

    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        results.append({
                            'id': entry.get('id'),
                            'title': entry.get('title'),
                            'artist': entry.get('uploader', 'Unknown Artist'),
                            'thumbnail': entry.get('thumbnail', ''),
                            'source': entry.get('url')
                        })
    except Exception as e:
        print(f"yt-dlp major error: {e}")
        # Agar block ho jaye toh khali list bhejenge taaki frontend crash na ho
        return jsonify([])

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
