from voice_assistant.conversation import build_recent_dialog
from voice_assistant.history import load_history, add_message
from voice_assistant.llm import ask_claude
from voice_assistant.memory import update_long_term_memory_from_text
from voice_assistant.recorder import record_while_pressed
from voice_assistant.stt import transcribe
from voice_assistant.tts import speak


def is_enter_pressed():
    """Enter 키가 눌려있는 동안 True 반환 (테스트용)"""
    return False  # record_while_pressed 대신 직접 입력 사용


def main():
    print("🎙️ 음성 어시스턴트 테스트 시작!")
    print("텍스트를 직접 입력해서 테스트합니다.")

    # 오늘의 대화 기록 불러오기
    messages = load_history()

    try:
        while True:
            # 키보드 입력 대기
            text = input("\n💬 입력 (종료: q): ").strip()

            if text.lower() == "q":
                print("종료합니다.")
                break

            if not text:
                continue

            print(f"할머니: {text}")

            # 대화 기록에 추가
            messages = add_message(messages, "user", text)

            # 최근 몇 턴의 대화를 기반으로 장기 기억 후보 추출
            recent_dialog = build_recent_dialog(messages, turns=4)
            update_long_term_memory_from_text(recent_dialog)

            # Claude 호출
            print("Claude 생각 중...")
            response = ask_claude(messages)
            print(f"어시스턴트: {response}")

            # 대화 기록에 추가
            messages = add_message(messages, "assistant", response)

            # TTS로 응답
            speak(response)

    except KeyboardInterrupt:
        print("\n프로그램 종료")


if __name__ == "__main__":
    main()
