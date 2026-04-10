from flask import Blueprint, request, jsonify
from app.models.ml_loaders import get_bias_model

bias_bp = Blueprint('bias', __name__)

@bias_bp.route('/detect-bias', methods=['POST'])
def detect_bias():
    data = request.get_json(silent=True)
    
    if not data or 'text' not in data:
        return jsonify({"error": "Bad Request", "message": "Missing 'text' parameter"}), 400
        
    text = data['text']
    
    try:
        # Lazy load bias model
        model = get_bias_model()
        
        response = {
            "status": "success",
            "bias_score": 0.34,
            "political_leaning": "Neutral",
            "message": "Model inference setup required."
        }
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": "Inference Error", "message": str(e)}), 500
