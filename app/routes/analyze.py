from flask import Blueprint, request, jsonify
import concurrent.futures
import time

from app.models.fake_news_detector import FakeNewsDetector
from app.models.bias_detector import BiasDetector
from app.models.summarizer import Summarizer

from app.utils.tts_generator import generate_speech
from deep_translator import GoogleTranslator

analyze_bp = Blueprint('analyze', __name__)

@analyze_bp.route('/analyze', methods=['POST'])
def analyze_article():
    start_time = time.time()
    data = request.get_json(silent=True)
    
    if not data or 'text' not in data:
        return jsonify({"error": "Bad Request", "message": "Missing 'text' field"}), 400
        
    original_text = data['text']
    target_lang = data.get('target_lang', 'en')
    
    if len(original_text) < 20:
        return jsonify({"error": "Bad Request", "message": "Text is too short to analyze."}), 400
        
    # Translate to English for ML inference
    analysis_text = original_text
    try:
        if target_lang != 'en':
             analysis_text = GoogleTranslator(source='auto', target='en').translate(original_text)
    except Exception:
        pass # fallback
            
    try:
        fake = FakeNewsDetector.get_instance()
        bias = BiasDetector.get_instance()
        summarizer = Summarizer.get_instance()
        
        results = {}
        
        def run_fake(): return fake.analyze(analysis_text)
        def run_bias(): return bias.analyze(analysis_text)
        def run_summary(): return summarizer.summarize(analysis_text)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_fake = executor.submit(run_fake)
            future_bias = executor.submit(run_bias)
            future_summ = executor.submit(run_summary)
            
            results['fake_news'] = future_fake.result()
            results['bias'] = future_bias.result()
            results['summarization'] = future_summ.result()
            
        # Translate the generated summary back to the target language
        translated_summary_bullets = []
        try:
            for b in results['summarization'].get('bullets', [results['summarization'].get('summary', '')]):
                 translated_summary_bullets.append(GoogleTranslator(source='en', target=target_lang).translate(b))
        except Exception:
            translated_summary_bullets = results['summarization'].get('bullets', [results['summarization'].get('summary', '')])
            
        results['summarization']['bullets'] = translated_summary_bullets
            
        summary_txt = " ".join(translated_summary_bullets)
        results['audio_url'] = generate_speech(summary_txt, lang=target_lang)
        results['total_processing_time'] = round(time.time() - start_time, 4)
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": "Analysis Pipeline Error", "message": str(e)}), 500
