import openai
from .config import OPENAI_API_KEY, RECORDING_PATH

client = openai.OpenAI(api_key=OPENAI_API_KEY)


def transcribe(recording_path: str | None = None):
    """녹음 파일을 텍스트로 변환. 경로를 주지 않으면 기본 RECORDING_PATH."""
    path = recording_path if recording_path is not None else RECORDING_PATH
    try:
        with open(path, "rb") as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="ko"
            )
        return response.text

    except Exception as e:
        print(f"STT 오류: {e}")
        return None
