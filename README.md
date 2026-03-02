# Voice Assistant for Grandmother
할머니를 위한 AI 음성 어시스턴트

## 하드웨어
- Raspberry Pi 4 (4GB)
- ReSpeaker 2-Mic HAT
- 아케이드 버튼 60mm
- 스피커 (3.5mm)

## 프로젝트 구성
voice-assistant/
  ├── main.py          # 메인 루프
  ├── stt.py           # 음성 → 텍스트 (Whisper)
  ├── llm.py           # Claude API 호출
  ├── tts.py           # 텍스트 → 음성 (gTTS)
  ├── button.py        # 버튼 제어 (GPIO)
  ├── history.py       # 대화 기록 관리
  ├── config.py
  └── README.md

## 자주 쓰는 명령어

### 가상환경 활성화
source venv/bin/activate

### 프로그램 실행
python3 main.py

### Pi 재부팅
sudo reboot

### 온도 확인
vcgencmd measure_temp
- ~50°C 정상
- 70°C 조금 뜨거움
- 80°C 이상은 위험

### Pi 보드 핀 배치도
pinout

### IP 확인
hostname -I

## 라이브러리
- anthropic: Claude API 호출
- openai: Whisper STT
- sounddevice: 마이크 녹음
- scipy: 녹음 파일 저장
- gtts: 텍스트 → 음성 변환
- pygame: 음성 파일 재생
