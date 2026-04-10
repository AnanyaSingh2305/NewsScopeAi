import os
import requests
import uuid

def generate_avatar_video(audio_url: str, source_url: str = None, local_audio_path: str = None) -> str:
    """Generate the video using D-ID if available, or fallback to local MoviePy Synthesis."""
    api_key = os.getenv("D_ID_API_KEY")
    
    # D-ID Backend Flow
    if api_key and api_key != "your_d_id_api_key_here":
        url = "https://api.d-id.com/talks"
        headers = {
            "Authorization": f"Basic {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "script": { "type": "audio", "audio_url": audio_url },
            "source_url": source_url or "https://example.com/default.png",
            "config": { "fluent": True, "pad_audio": 0.0 }
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                return response.json().get("id", "job_error")
        except Exception as e:
            print(f"D-ID Error: {e}")
            
    # Local MoviePy Fallback Synthesis for Demo
    try:
        from moviepy import ImageClip, AudioFileClip
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        # Format the audio URL to absolute system path using the provided local_audio_path or audio_url
        target_path = local_audio_path if local_audio_path else audio_url
        if target_path.startswith('/'):
            target_path = target_path[1:]
        absolute_audio_path = os.path.join(base_dir, target_path.replace('/', os.sep))
        
        avatar_path = os.path.join(base_dir, 'static', 'default-avatar.png')
        if not os.path.exists(avatar_path):
            return "job_error"
            
        audio_clip = AudioFileClip(absolute_audio_path)
        img_clip = ImageClip(avatar_path).with_duration(audio_clip.duration)
        
        import numpy as np
        
        def simulate_lip_sync(gf, t):
            frame = gf(t)
            try:
                a_frame = audio_clip.get_frame(t)
                vol = np.sqrt(np.mean(a_frame**2)) if isinstance(a_frame, np.ndarray) else abs(a_frame)
                
                if vol > 0.02:
                    h, w, _ = frame.shape
                    x1, x2 = int(w * 0.38), int(w * 0.62)
                    y1, y2 = int(h * 0.57), int(h * 0.67)
                    
                    shift = min(int(vol * 20), y2 - y1 - 2)
                    
                    if shift > 0:
                        new_frame = np.copy(frame)
                        # Stretch only the localized lip box vertically
                        new_frame[y1+shift:y2, x1:x2] = frame[y1:y2-shift, x1:x2]
                        for i in range(shift):
                            new_frame[y1+i, x1:x2] = frame[y1, x1:x2]
                        return new_frame
            except Exception:
                pass
            return frame
            
        img_clip = img_clip.transform(simulate_lip_sync)
        
        # Audio assignment syntax in MoviePy 2
        video = img_clip.with_audio(audio_clip)
        
        output_filename = f"avatar_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join(base_dir, 'static', 'video', output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write to file
        video.write_videofile(output_path, fps=24, logger=None)
        
        # Return unique prefix so poller knows it's local
        return f"local_{output_filename}"
        
    except Exception as e:
        print(f"MoviePy Fallback Error: {e}")
        return "job_error"


def check_video_status(job_id: str) -> dict:
    # If the generator successfully created a local video
    if job_id.startswith("local_"):
        filename = job_id[6:] 
        return {
            "status": "done",
            "video_url": f"/static/video/{filename}"
        }
        
    if job_id == "job_error":
        return {"status": "error", "message": "Video generation failed"}
        
    # Standard D-ID Check
    api_key = os.getenv("D_ID_API_KEY")
    if not api_key:
        return {"status": "error", "message": "API key missing"}
        
    url = f"https://api.d-id.com/talks/{job_id}"
    headers = {
        "Authorization": f"Basic {api_key}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            return {
                "status": status,
                "video_url": data.get("result_url", None) if status == "done" else None
            }
        return {"status": "error", "message": f"API returned {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
