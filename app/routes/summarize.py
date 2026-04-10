from flask import Blueprint, request, jsonify
import os

summarize_bp = Blueprint('summarize', __name__)

@summarize_bp.route('/summarize', methods=['POST'])
def summarize_text():
    data = request.get_json(silent=True)
    
    if not data or 'text' not in data:
        return jsonify({"error": "Bad Request", "message": "Missing 'text' parameter"}), 400
        
    text = data['text']
    
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            return jsonify({"error": "Configuration Error", "message": "OpenAI API key not configured"}), 500
            
        # TODO: Implement OpenAI ChatCompletion logic here
        
        response = {
            "status": "success",
            "summary": [
                "This is the first bullet point of the summary.",
                "This is the second key point extracted from the text.",
                "This is the final conclusion of the article."
            ]
        }
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": "Summarization Error", "message": str(e)}), 500
