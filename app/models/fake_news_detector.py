import os
import time

class FakeNewsDetector:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = FakeNewsDetector()
        return cls._instance

    def __init__(self):
        self.model_path = "./models/fake_news_model"
        self.pipeline = None
        self._load_model()
        
    def _load_model(self):
        print("[System] Loading Fake News Pipeline...")
        try:
            from transformers import pipeline
            if os.path.exists(self.model_path):
                self.pipeline = pipeline("text-classification", model=self.model_path, tokenizer=self.model_path, device=-1)
                print("[System] Custom trained model loaded.")
            else:
                print("[System] Custom model not found in /models. Falling back to base HuggingFace Model for stub.")
                self.pipeline = pipeline("text-classification", model="hamzab/roberta-fake-news-classification", device=-1)
        except Exception as e:
            print(f"Failed to load Fake News model: {e}")
            
    def analyze(self, text: str) -> dict:
        if not self.pipeline:
            return {"label": "REAL", "confidence": 0.55, "fake_probability": 0.45, "real_probability": 0.55}
            
        try:
            truncated_text = text[:1500] 
            result = self.pipeline(truncated_text)[0]
            
            label_text = result['label'].lower()
            confidence = float(result['score'])
            
            is_fake = "fake" in label_text or "false" in label_text or "label_0" in label_text
            final_label = "FAKE" if is_fake else "REAL"
            
            fake_prob = confidence if is_fake else (1.0 - confidence)
            real_prob = confidence if not is_fake else (1.0 - confidence)
            
            # --- Live Fact-Checking Override (Official APIs -> DDGS Fallback) ---
            try:
                import requests
                factcheck_key = os.getenv("FACTCHECK_API_KEY")
                newsapi_key = os.getenv("NEWSAPI_KEY")
                api_override_applied = False
                
                # 1. Google Fact Check Tools API (Official Debunking)
                if factcheck_key and factcheck_key != "your_factcheck_api_key_here":
                    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={text[:100]}&key={factcheck_key}"
                    res = requests.get(url, timeout=5)
                    if res.status_code == 200:
                        data = res.json()
                        claims = data.get("claims", [])
                        for claim in claims:
                            review = claim.get("claimReview", [{}])[0]
                            rating = review.get("textualRating", "").lower()
                            if any(w in rating for w in ["false", "fake", "incorrect", "pants on fire", "hoax"]):
                                final_label = "FAKE"
                                confidence = 0.98
                                fake_prob = 0.98
                                real_prob = 0.02
                                api_override_applied = True
                                break
                                
                # 2. NewsAPI (Global News Verification)
                if not api_override_applied and newsapi_key and newsapi_key != "your_newsapi_key_here":
                    # For a breaking claim, does official news report it?
                    search_query = text[:50]
                    url = f"https://newsapi.org/v2/everything?q={search_query}&apiKey={newsapi_key}&language=en"
                    res = requests.get(url, timeout=5)
                    if res.status_code == 200:
                        data = res.json()
                        total_results = data.get("totalResults", 0)
                        # If zero trusted news outlets are reporting a massive claim:
                        if total_results == 0:
                            final_label = "FAKE"
                            confidence = max(0.88, confidence)
                            fake_prob = confidence
                            real_prob = 1.0 - confidence
                            api_override_applied = True

                # 3. DuckDuckGo Fallback (for free-tier users)
                if not api_override_applied:
                    from duckduckgo_search import DDGS
                    with DDGS() as ddgs:
                        # Search the web for the input claim
                        results = list(ddgs.text(text[:300], max_results=3))
                        if results:
                            combined_snippets = " ".join([r.get('body', '').lower() for r in results])
                            
                            # Fact-Check Domain Heuristic
                            suspicious_kw = ["fake", "hoax", "false", "misleading", "fact check", "debunk", "untrue", "rumor"]
                            if any(kw in combined_snippets for kw in suspicious_kw):
                                final_label = "FAKE"
                                confidence = max(0.92, confidence)
                                fake_prob = confidence
                                real_prob = 1.0 - confidence
                                
                            # Entity Discrepancy Heuristic
                            proper_nouns = [w.strip() for w in text.split() if w.strip() and w[0].isupper() and len(w) > 3]
                            if proper_nouns:
                                missing = [w for w in proper_nouns if w.lower() not in combined_snippets]
                                if len(missing) / len(proper_nouns) >= 0.5:
                                    final_label = "FAKE"
                                    confidence = max(0.89, confidence)
                                    fake_prob = confidence
                                    real_prob = 1.0 - confidence
            except Exception as e:
                print(f"Fact-Check Override skipped: {e}")
            # --------------------------------------------------------------------
            
            return {
                "label": final_label,
                "confidence": confidence,
                "fake_probability": round(fake_prob, 3),
                "real_probability": round(real_prob, 3)
            }
        except Exception as e:
            print(f"FakeNews Inference Error: {e}")
            return {"label": "REAL", "confidence": 0.5, "fake_probability": 0.5, "real_probability": 0.5}
