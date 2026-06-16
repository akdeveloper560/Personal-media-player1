from flask import Flask, render_template
import os

# Current directory ka absolute path nikalne ke liye
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=current_dir, 
            static_folder=current_dir, 
            static_url_path='')

@app.route('/')
def index():
    # Yeh aapki index.html file ko browser mein load karega
    return render_template('index.html')

if __name__ == '__main__':
    # Local testing ke liye port 5000 par chalega
    app.run(host='0.0.0.0', port=5000, debug=True)
