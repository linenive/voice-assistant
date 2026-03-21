# Voice Assistant for Grandmother
할머니를 위한 AI 음성 어시스턴트

## 하드웨어
- Raspberry Pi 4 (4GB)
- ReSpeaker 2-Mic HAT
- 아케이드 버튼 60mm
- 스피커 (3.5mm)

## 프로젝트 구성
voice-assistant/
  ├── main.py                 # 루트 엔트리 → `voice_assistant.app`
  ├── voice_assistant/        # 애플리케이션 패키지
  │   ├── app.py              # 스레드 기동·메인 루프
  │   ├── config.py
  │   ├── state.py / partitions.py
  │   ├── gui_client.py       # cli-gui (선택)
  │   ├── stt.py / llm.py / tts.py / …
  │   └── threads/          # 버튼 루프·녹음 큐·LLM 스케줄러
  ├── tests/                # 스크립트형 테스트
  ├── history/              # 대화·장기기억 JSON
  └── README.md

## 자주 쓰는 명령어

### 가상환경 활성화
source .venv/bin/activate

### 프로그램 실행
python3 main.py
# 또는
python3 -m voice_assistant

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

## 화면 표시 (선택, [cli-gui](../cli-gui))
- 같은 레벨의 `cli-gui/src/cli_gui/`를 `PYTHONPATH`에 붙여 **`python -m cli_gui`** 로 띄웁니다. PyQt6는 [cli-gui `pyproject.toml`](../cli-gui/pyproject.toml)에 있으므로 **같은 venv에서** `pip install -e ../cli-gui` 후 **`python main.py`** 로 실행합니다.
- SSH에서 `DISPLAY`가 비면 자식에 `DISPLAY=:0`, `~/.Xauthority`(있을 때)를 넣습니다.
- `show_gui(..., partition=n)` → cli-gui `show -p n`과 동일. `partition` 0=상, 1=중, 2=하(기본 0).
- 로그: `/tmp/voice_assistant_gui_client.log`

## 오디오 (선택)
기본은 PortAudio 기본 입·출력 + TTS는 ALSA `pulse`(PipeWire 기본과 동일). 필요 시 환경 변수로 고정:
- `VOICE_INPUT_DEVICE`, `VOICE_OUTPUT_DEVICE`: 장치 인덱스(정수)
- `VOICE_ALSA_OUTPUT`: `mpg321 -a`에 넘길 ALSA 이름(기본 `pulse`)

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