from flask import Flask, request, jsonify
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

    print("📸 Image received")

    if 'image' not in request.files:
        print("❌ No image")
        return jsonify({"status": "no image"}), 400

    file = request.files['image']

    filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    print("✅ Saved:", filename)

    return jsonify({
        "status": "success",
        "filename": filename
    })