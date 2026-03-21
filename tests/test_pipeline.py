import sounddevice as sd
import scipy.io.wavfile as wav

from voice_assistant.config import SAMPLE_RATE, CHANNELS, RECORDING_PATH, INPUT_DEVICE
from voice_assistant.history import load_history, add_message
from voice_assistant.llm import ask_claude
from voice_assistant.stt import transcribe
from voice_assistant.tts import speak


def record_seconds(seconds=5):
    """몇 초 동안 녹음"""
    print(f"🎙️ {seconds}초 동안 녹음합니다. 말씀하세요!")
    audio = sd.rec(
        int(seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        device=INPUT_DEVICE,
    )
    sd.wait()
    wav.write(RECORDING_PATH, SAMPLE_RATE, audio)
    print("녹음 완료!")


def main():
    print("🎙️ 전체 파이프라인 테스트!")
    messages = load_history()

    try:
        while True:
            input("\nEnter 누르면 5초 녹음 시작...")
            record_seconds(5)

            print("STT 변환 중...")
            text = transcribe()

            if not text:
                print("인식 실패, 다시 시도해주세요.")
                continue

            print(f"인식된 텍스트: {text}")
            messages = add_message(messages, "user", text)

            print("Claude 응답 중...")
            response = ask_claude(messages)
            print(f"Claude: {response}")
            messages = add_message(messages, "assistant", response)

            speak(response)

    except KeyboardInterrupt:
        print("\n종료!")


if __name__ == "__main__":
    main()
