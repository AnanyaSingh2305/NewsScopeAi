from flask import Blueprint, request, jsonify
import time
from app.models.fake_news_detector import FakeNewsDetector

fake_news_bp = Blueprint('fake_news', __name__)

@fake_news_bp.route('/detect-fake', methods=['POST'])
def detect_fake_news():
    start_time = time.time()
    data = request.get_json(silent=True)
    
    if not data or ('text' not in data and 'url' not in data):
        return jsonify({"error": "Bad Request", "message": "Missing 'text' or 'url'"}), 400
        
    text = data.get('text', '')
    url = data.get('url', '')
    
    if url and not text:
        text = "This is a placeholder for scraped content from: " + url

    try:
        detector = FakeNewsDetector.get_instance()
        result = detector.analyze(text)
        
        processing_time = time.time() - start_time
        
        response = {
            "result": result['label'],
            "confidence": result['confidence'],
            "fake_probability": result['fake_probability'],
            "real_probability": result['real_probability'],
            "explanation": f"The AI model is {result['confidence']*100:.1f}% confident this article is {result['label']}.",
            "processing_time": round(processing_time, 4)
        }
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": "Inference Error", "message": str(e)}), 500
