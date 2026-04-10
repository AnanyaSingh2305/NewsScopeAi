import os
import openai

class Summarizer:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Summarizer()
        return cls._instance

    def __init__(self):
        self.pipeline = None
        self.openai_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_key or self.openai_key == "your_openai_api_key_here":
            self._load_local_model()

    def _load_local_model(self):
        print("[System] Loading Local BART Summarizer...")
        try:
            from transformers import pipeline
            self.pipeline = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=-1)
        except Exception as e:
            print(f"Failed to load local summarizer: {e}")

    def summarize(self, text: str) -> dict:
        original_words = len(text.split())
        have_key = self.openai_key and self.openai_key != "your_openai_api_key_here"
        
        if have_key:
            try:
                openai.api_key = self.openai_key
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Summarize this news article in exactly 3 concise bullet points. Be neutral and factual."},
                        {"role": "user", "content": text[:4000]}
                    ],
                    max_tokens=150
                )
                summary = response.choices[0].message.content
                bullets = [b.lstrip('-*').strip() for b in summary.split('\n') if b.strip()]
            except Exception as e:
                print(f"OpenAI error taking down summary, falling back locally: {e}")
                summary, bullets = self._local_summarize(text)
        else:
            summary, bullets = self._local_summarize(text)
            
        summary_words = sum(len(b.split()) for b in bullets) if len(bullets) > 1 else len(summary.split())
        ratio = 0.0 if original_words == 0 else (1.0 - (summary_words / max(original_words, 1))) * 100
        
        return {
            "summary": summary,
            "bullets": bullets,
            "word_count_original": original_words,
            "word_count_summary": summary_words,
            "compression_ratio": round(ratio, 2)
        }

    def _local_summarize(self, text):
        if not self.pipeline:
            return ("Insufficient data to summarize. Model load failed.", ["Model error fallback."])
        
        try:
            res = self.pipeline(text[:1024], max_length=130, min_length=30, do_sample=False)
            summary = res[0]['summary_text']
            sentences = summary.split('. ')
            bullets = [s.strip() + ('.' if not s.endswith('.') else '') for s in sentences if s.strip()]
            if not bullets: bullets = [summary]
            return summary, bullets
        except Exception as e:
            return ("Summary computation failed.", ["Algorithm error."])
