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
    return send_from_directory("uploads", filename)

@app.route("/gallery")
def gallery():

    files = os.listdir("uploads")

    html = ""
    for file in files:
        html += f'<img src="/images/{file}" width="300"><br><br>'
#https://smart-meter-render.onrender.com/gallery

    return html