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

## ReSpeaker 2-Mics Pi HAT V2.0 설치

### 주의사항
- 이 보드는 V2.0으로 칩이 WM8960 → TLV320AIC3104(AC31041)로 변경됨
- V1용 드라이버(seeed-voicecard)는 동작하지 않음

### 설치 방법
git clone https://github.com/Seeed-Studio/seeed-linux-dtoverlays.git
cd seeed-linux-dtoverlays
make overlays/rpi/respeaker-2mic-v2_0-overlay.dtbo
sudo cp overlays/rpi/respeaker-2mic-v2_0-overlay.dtbo \
  /boot/firmware/overlays/respeaker-2mic-v2_0.dtbo
echo "dtoverlay=respeaker-2mic-v2_0" | sudo tee -a /boot/firmware/config.txt
sudo reboot

### 테스트
arecord -D plughw:3,0 -f S16_LE -r 16000 -c 2 -d 5 /tmp/test.wav
aplay -D plughw:3,0 /tmp/test.wav