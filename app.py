from flask import Flask, request, jsonify, send_from_directory
import os
from datetime import datetime
import requests
import base64

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ⭐ ใส่ URL Google Apps Script ของคุณ
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw6q1hE_TAtxzH4XXAa2z3u4PrsaEaD7Bie4yW5j4Zi7SwIoiGkf19_0I0z4eNBVl5_/exec"


@app.route("/")
def home():
    return "ESP32-CAM Upload Server Running"


@app.route("/upload", methods=["POST"])
def upload_image():

    print("📸 Image received", flush=True)

    if 'image' not in request.files:
        print("❌ No image", flush=True)
        return jsonify({"status": "no image"}), 400

    file = request.files['image']

    filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # ⭐ บันทึกใน server
    file.save(filepath)

    print("✅ Saved:", filename, flush=True)

    # ⭐ ส่งไป Google Drive
    try:
        with open(filepath, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()

        requests.post(
            GOOGLE_SCRIPT_URL,
            data={
                "image": encoded,
                "filename": filename
            },
            timeout=10
        )

        print("☁️ Uploaded to Google Drive", flush=True)

    except Exception as e:
        print("⚠️ Google Drive upload failed:", e, flush=True)

    return jsonify({
        "status": "success",
        "filename": filename
    })


@app.route("/images/<filename>")
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/gallery")
def gallery():

    files = [f for f in os.listdir(UPLOAD_FOLDER)
             if f.lower().endswith((".jpg",".jpeg",".png"))]

    files = sorted(files, reverse=True)

    html = """
    <html>
    <head>
    <title>Smart Meter Gallery</title>

    <meta http-equiv="refresh" content="7">

    <style>
    body{
        font-family: Arial;
        background:#111;
        color:white;
        text-align:center;
    }

    .grid{
        display:flex;
        flex-wrap:wrap;
        justify-content:center;
    }

    .card{
        background:#222;
        padding:10px;
        margin:10px;
        border-radius:10px;
    }

    img{
        border-radius:8px;
    }

    </style>
    </head>
    <body>

    <h1>📷 Smart Meter Gallery</h1>

    <div class="grid">
    """

    if not files:
        html += "<h2>No images yet</h2>"

    for file in files:

        timestamp = file.replace(".jpg","")

        html += f"""
        <div class="card">
            <img src="/images/{file}" width="300"><br><br>
            {timestamp}
        </div>
        """

    html += """
    </div>
    </body>
    </html>
    """

    return html


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)