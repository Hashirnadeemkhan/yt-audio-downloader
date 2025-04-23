import os
from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp
from flask_cors import CORS  # CORS ke liye import

# Flask app ko initialize karte hain
app = Flask(__name__)
CORS(app)  # CORS ko enable karte hain

# Directory aur ffmpeg paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
FFMPEG_BIN = os.path.join(BASE_DIR, 'ffmpeg-2025-04-21-git-9e1162bdf1-essentials_build', 'bin', 'ffmpeg.exe')
FFPROBE_BIN = os.path.join(BASE_DIR, 'ffmpeg-2025-04-21-git-9e1162bdf1-essentials_build', 'bin', 'ffprobe.exe')

# Download directory banate hain agar nahi hai
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET'])
def home():
    # Ye HTML page ko return karta hai
    return render_template('index.html')

@app.route('/download_audio', methods=['POST'])
def download_audio():
    url = request.json.get('url')  # Frontend se URL lene ka tarika
    if not url:
        return jsonify({"error": "No URL provided"}), 400  # Agar URL nahi diya gaya to error

    # yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',  # Best audio format chahiye
        'ffmpeg_location': FFMPEG_BIN,  # FFMPEG ka sahi path
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Audio ko extract karna
            'preferredcodec': 'mp3',  # MP3 format mein convert karna
            'preferredquality': '192',  # Audio quality 192kbps
        }],
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),  # Download location
    }

    try:
        # yt-dlp ko call karte hain aur download karte hain
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as e:
        return jsonify({"error": f"Download Error: {e}"}), 500  # Agar download mein koi error aata hai to

    # Downloaded file ka naam set karte hain
    filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
    if not os.path.exists(filename):  # Agar file nahi mili to error
        return jsonify({"error": "Downloaded file not found"}), 500

    # File ko frontend pe bhejte hain
    return send_file(
        filename,
        as_attachment=True,
        download_name=os.path.basename(filename),
        mimetype='audio/mp3'
    )

# Flask app ko run karte hain
if __name__ == '__main__':
    app.run(debug=True)
