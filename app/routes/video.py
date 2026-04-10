from flask import Blueprint, request, jsonify
from app.utils.tts_generator import generate_speech
from app.utils.video_generator import generate_avatar_video, check_video_status

video_bp = Blueprint('video', __name__)

_job_queue = {}

@video_bp.route('/generate-video', methods=['POST'])
def generate_video():
    data = request.get_json(silent=True)
    if not data or 'text' not in data:
        return jsonify({"error": "Bad Request", "message": "Missing 'text'"}), 400
        
    text = data['text']
    target_lang = data.get('target_lang', 'en')
    
    try:
        audio_path = generate_speech(text, lang=target_lang)
        public_audio_url = f"https://example.com{audio_path}" 
        
        job_id = generate_avatar_video(audio_url=public_audio_url, local_audio_path=audio_path)
        _job_queue[job_id] = {"status": "processing"}
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "message": "Video generation started."
        }), 202
        
    except Exception as e:
        return jsonify({"error": "Pipeline Error", "message": str(e)}), 500

@video_bp.route('/video-status/<job_id>', methods=['GET'])
def video_status(job_id):
    try:
        status_data = check_video_status(job_id)
        if status_data.get('status') == "done":
            _job_queue[job_id] = status_data
            
        return jsonify({
            "job_id": job_id,
            "status": status_data.get('status', 'processing'),
            "video_url": status_data.get('video_url', None)
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Status Check Error", "message": str(e)}), 500

@video_bp.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.get_json(silent=True)
    if not data or 'text' not in data:
        return jsonify({"error": "Bad Request", "message": "Missing 'text'"}), 400
        
    text = data['text']
    try:
        audio_path = generate_speech(text)
        return jsonify({
            "status": "success",
            "audio_url": audio_path,
            "message": "Audio generation complete."
        }), 200
    except Exception as e:
        return jsonify({"error": "TTS Error", "message": str(e)}), 500

