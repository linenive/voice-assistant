import os
import sounddevice as sd
from dotenv import load_dotenv

load_dotenv()

# API 키
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def _portaudio_device_index(slot: int, env_var: str) -> int | None:
    """slot 0=입력, 1=출력. env_var에 정수를 주면 그 인덱스로 고정."""
    raw = os.getenv(env_var)
    if raw is not None and raw.strip() != "":
        return int(raw)
    idx = sd.default.device[slot]
    return None if idx is None else int(idx)


# 오디오 설정
SAMPLE_RATE = 16000
CHANNELS = 1
RECORDING_PATH = "/tmp/recording.wav"
RESPONSE_PATH = "/tmp/response.mp3"
INPUT_DEVICE = _portaudio_device_index(0, "VOICE_INPUT_DEVICE")
OUTPUT_DEVICE = _portaudio_device_index(1, "VOICE_OUTPUT_DEVICE")

# mpg321: ALSA "pulse" → PipeWire/Pulse 기본 sink(유튜브·BT 등과 동일). "default"는 3.5mm로만 잡히는 경우가 많음.
ALSA_PLAYBACK_DEVICE = os.getenv("VOICE_ALSA_OUTPUT", "pulse")

# 버튼 GPIO 핀 번호
BUTTON_PIN = 17

# Claude 설정
MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 1024
MEMORY_MODEL = "claude-sonnet-4-6"
SYSTEM_PROMPT = """당신은 친절한 AI 음성 어시스턴트입니다.
당신은 할머니와 대화하므로 존댓말을 사용하고,
짧고 명확하게 답변해주세요.
tts이므로 이모지나 기호 사용은 피해주세요.
따뜻하고 친근한 말투로 대화해주세요."""

# 대화 기록 설정
HISTORY_PATH = "/home/jan/Develop/voice-assistant/history"
MAX_HISTORY = 20  # 최대 대화 기록 수
