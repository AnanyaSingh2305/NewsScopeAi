class BiasDetector:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = BiasDetector()
        return cls._instance

    def __init__(self):
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        print("[System] Loading Bias Detection Pipeline...")
        try:
            from transformers import pipeline
            self.pipeline = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli", device=-1)
        except Exception as e:
            print(f"Failed to load Bias model: {e}")

    def get_bias_explanation(self, text, label):
        flag_words = ['extremist', 'radical', 'socialist', 'communist', 'fascist', 'libtard', 'snowflake', 'woke', 'destroy', 'agenda', 'propaganda']
        found = [word for word in flag_words if word in text.lower()]
        return list(set(found))

    def analyze(self, text: str) -> dict:
        if not self.pipeline:
            return {"bias_label": "CENTER", "confidence": 0.5, "explanation": "Fallback active: Model not loaded", "bias_indicators": []}

        try:
            result = self.pipeline(text[:1500], candidate_labels=['left-wing', 'right-wing', 'neutral'])
            best_label = result['labels'][0].upper()
            confidence = float(result['scores'][0])
            
            mapped_label = best_label.replace('-WING', '')
            if mapped_label == 'NEUTRAL':
                mapped_label = 'CENTER'
                
            indicators = self.get_bias_explanation(text, mapped_label)
            
            return {
                "bias_label": mapped_label,
                "confidence": confidence,
                "explanation": f"Detected {mapped_label} orientation with {confidence*100:.1f}% confidence.",
                "bias_indicators": indicators
            }
        except Exception as e:
            print(f"Bias Inference Error: {e}")
            return {"bias_label": "CENTER", "confidence": 0.0, "explanation": "Error analyzing bias.", "bias_indicators": []}
