import openai
from dotenv import load_dotenv
import os

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("/tmp/test.wav", "rb") as f:
    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=f,
        language="ko"
    )

print(f"인식된 텍스트: {response.text}")