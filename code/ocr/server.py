from flask import Flask, request, jsonify
import io
import numpy as np
from PIL import Image
import requests
import os

app = Flask(__name__)
ocr_manager = None

def convert_to_numpy(image_stream_or_url):
    if isinstance(image_stream_or_url, str):  # URL
        response = requests.get(image_stream_or_url, timeout=10)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert("RGB")
    else:  
        image = Image.open(image_stream_or_url).convert("RGB")

    return np.array(image)


@app.route("/ocr", methods=["POST"])
def ocr_endpoint():
    print("Received OCR request")
    data = request.get_json(silent=True)
    print(data)
    if not data or "image" not in data:
        return jsonify({"error": "No image URL provided"}), 400

    image_url = data["image"]

    try:
        image_np = convert_to_numpy(image_url)
        # text = None
        text = ocr_manager.get_image_transcription(image_np)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "text": text
    })
    
@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    if os.environ.get("USE_STUB_OCR") == "true":
        from adapters.ocr_stub import StubOCRManager
        ocr_manager = StubOCRManager()
    else:
        from adapters.ocr_paddle import PaddleOCRManager
        ocr_manager = PaddleOCRManager()
    app.run(host="0.0.0.0", port=5000, debug=False)
