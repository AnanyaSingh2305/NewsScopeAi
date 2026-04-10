import os
import uuid
import requests
from gtts import gTTS

def generate_speech(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM", lang: str = "en") -> str:
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    file_uuid = str(uuid.uuid4())
    filepath = os.path.join(audio_dir, f"{file_uuid}.mp3")
    rel_path = f"/static/audio/{file_uuid}.mp3"

    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    try:
        if api_key and api_key != "your_elevenlabs_api_key_here":
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            data = {
                "text": text[:5000],
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
            }
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return rel_path
            else:
                print(f"ElevenLabs API error: {response.text}")
    except Exception as e:
        print(f"ElevenLabs connection error: {e}")

    print("Falling back to gTTS (Free tier)")
    tts = gTTS(text=text[:5000], lang=lang)
    tts.save(filepath)
    
    return rel_path
