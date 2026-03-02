import os
from dotenv import load_dotenv

load_dotenv()

# API 키
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 오디오 설정
SAMPLE_RATE = 16000
CHANNELS = 1
RECORDING_PATH = "/tmp/recording.wav"
RESPONSE_PATH = "/tmp/response.mp3"

# 버튼 GPIO 핀 번호
BUTTON_PIN = 17

# Claude 설정
MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 1024
SYSTEM_PROMPT = """당신은 친절한 AI 음성 어시스턴트입니다.
할머니와 대화하므로 존댓말을 사용하고,
짧고 명확하게 답변해주세요.
tts이므로 이모지나 기호 사용은 피해주세요.
따뜻하고 친근한 말투로 대화해주세요."""

# 대화 기록 설정
HISTORY_PATH = "/home/jan/Develop/voice-assistant/history"
MAX_HISTORY = 20  # 최대 대화 기록 수