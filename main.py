import time
import RPi.GPIO as GPIO
from button import setup, is_pressed, cleanup
from recorder import record_while_pressed
from stt import transcribe
from llm import ask_claude
from tts import speak
from history import load_history, add_message

def main():
    print("🎙️ 음성 어시스턴트 시작!")
    print("버튼을 누르고 말씀해주세요.")
    
    # GPIO 초기화
    setup()
    
    # 오늘의 대화 기록 불러오기
    messages = load_history()
    
    try:
        while True:
            # 버튼 누를 때까지 대기
            if is_pressed():
                speak("네, 말씀하세요.")
                
                # 버튼 누르는 동안 녹음
                success = record_while_pressed(is_pressed)
                
                if success:
                    # STT
                    text = transcribe()
                    
                    if text:
                        print(f"할머니: {text}")
                        
                        # 대화 기록에 추가
                        messages = add_message(messages, "user", text)
                        
                        # Claude 호출
                        response = ask_claude(messages)
                        print(f"어시스턴트: {response}")
                        
                        # 대화 기록에 추가
                        messages = add_message(messages, "assistant", response)
                        
                        # TTS로 응답
                        speak(response)
                    else:
                        speak("잘 못 들었어요, 다시 말씀해주세요.")
                
                # 버튼 떼기 기다리기
                while is_pressed():
                    time.sleep(0.1)
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n프로그램 종료")
    
    finally:
        cleanup()

if __name__ == "__main__":
    main()