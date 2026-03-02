import openai
from config import OPENAI_API_KEY, RECORDING_PATH

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def transcribe():
    """녹음 파일을 텍스트로 변환"""
    try:
        with open(RECORDING_PATH, 'rb') as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="ko"
            )
        return response.text

    except Exception as e:
        print(f"STT 오류: {e}")
        return None
