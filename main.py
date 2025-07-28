from flask import Flask, request, render_template
import requests
import os
import uuid

app = Flask(__name__)

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")  # from Render env vars
DISCORD_CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-video', methods=['POST'])
def upload_video():
    video = request.files['video']
    filename = f"{uuid.uuid4()}.webm"
    
    # Send to Discord
    files = {'file': (filename, video, 'video/webm')}
    headers = {
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}'
    }
    r = requests.post(
        f'https://discord.com/api/v9/channels/{DISCORD_CHANNEL_ID}/messages',
        headers=headers,
        files=files
    )
    if r.status_code == 200 or r.status_code == 204:
        return "Uploaded to Discord!", 200
    else:
        return f"Failed: {r.status_code} - {r.text}", 500

if __name__ == '__main__':
    app.run(debug=True)
