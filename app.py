from flask import Flask, request, jsonify, send_from_directory
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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

    file.save(filepath)

    print("✅ Saved:", filename, flush=True)

    return jsonify({
        "status": "success",
        "filename": filename
    })


@app.route("/images/<filename>")
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/gallery")
def gallery():

    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".jpg")]
    files = sorted(files, reverse=True)

    if not files:
        return "<h1>No images yet</h1>"

    html = "<h1>Smart Meter Gallery</h1>"

    for file in files:
        html += f"""
        <div style="display:inline-block;margin:10px">
            <img src="/images/{file}" width="300"><br>
            {file}
        </div>
        """

    return html