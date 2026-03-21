import subprocess
from gtts import gTTS
from config import RESPONSE_PATH, ALSA_PLAYBACK_DEVICE

def speak(text):
    """텍스트를 음성으로 변환 후 재생"""
    try:
        tts = gTTS(text=text, lang='ko')
        tts.save(RESPONSE_PATH)
        subprocess.run(['mpg321', '-a', ALSA_PLAYBACK_DEVICE, RESPONSE_PATH])

    except Exception as e:
        print(f"TTS 오류: {e}")
