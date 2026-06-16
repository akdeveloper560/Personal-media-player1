from flask import Flask
import os

app = Flask(__name__)

# Root directory ka path jahan saari files hain
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    with open(os.path.join(BASE_DIR, 'index.html'), 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/script.js')
def script():
    with open(os.path.join(BASE_DIR, 'script.js'), 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'application/javascript'}

@app.route('/style.css')
def style():
    with open(os.path.join(BASE_DIR, 'style.css'), 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'text/css'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
