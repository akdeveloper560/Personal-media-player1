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

# Frontend `/api/search` use kar raha hai, toh route bhi wahi hona chahiye
@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch:5', # Top 5 gaane dhoondega
    }

    results = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        results.append({
                            'id': entry.get('id'),
                            'title': entry.get('title'),
                            'artist': entry.get('uploader', 'Unknown Artist'),
                            'thumbnail': entry.get('thumbnail', ''),
                            'source': entry.get('url') # Naye frontend ke liye 'source' key mapping
                        })
        except Exception as e:
            print(f"yt-dlp error: {e}")
            return jsonify({'error': str(e)}), 500

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
