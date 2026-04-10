"""
Lazy loading module for heavy Machine Learning models.
This prevents the Flask application from hanging during startup by only 
loading the models into RAM when the specific route is requested for the first time.
"""

_models = {
    'fake_news_model': None,
    'bias_model': None
}

def get_fake_news_model():
    """Lazily load the Fake News Detection model (e.g., HuggingFace RoBERTa)."""
    global _models
    if _models['fake_news_model'] is None:
        print("[System] Loading Fake News Classification Model into memory...")
        # Import transformers only when needed
        # from transformers import pipeline
        # _models['fake_news_model'] = pipeline("text-classification", model="roberta-base")
        _models['fake_news_model'] = "mock_fake_news_model_loaded"
        
    return _models['fake_news_model']

def get_bias_model():
    """Lazily load the Bias Detection model."""
    global _models
    if _models['bias_model'] is None:
        print("[System] Loading Media Bias Detection Model into memory...")
        _models['bias_model'] = "mock_bias_model_loaded"
        
    return _models['bias_model']
