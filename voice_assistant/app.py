"""
앱 엔트리: 스레드 기동·메인 루프·정리.

- 메인 스레드: `threads.button_loop` — GPIO·버튼·녹음, 완료 파일은 녹음 큐로.
- `threads.recording_thread`: WAV 큐에서 STT → 대화/기억 → `schedule_llm`.
- `threads.llm_thread`: 슬롯 하나로 LLM 예약, daemon 스레드가 순차 실행.
- 세대·`(path, utterance_gen)` 규칙: `state`, `threads` 모듈 참고.

HTTP `ask_claude()`는 끊을 수 없어, 실행 중 호출은 끝날 때까지 이어지나 세대로 결과는 버림.
"""

from __future__ import annotations

import queue
import threading

from .button import cleanup, setup
from .gui_client import show_gui
from .state import State
from .threads.button_loop import run_button_loop
from .threads.llm_thread import llm_scheduler_loop, shutdown_llm_scheduler
from .threads.recording_thread import recording_queue_worker
from .tts import stop_playback


def main() -> None:
    print("🎙️ 음성 어시스턴트 시작!")
    print("버튼을 누르고 말씀해주세요.")

    setup()
    state = State()
    pending: queue.Queue[tuple[str, int] | None] = queue.Queue()

    threading.Thread(
        target=llm_scheduler_loop,
        name="llm-scheduler",
        daemon=True,
    ).start()

    threading.Thread(
        target=recording_queue_worker,
        args=(state, pending),
        name="recording-queue",
        daemon=True,
    ).start()

    show_gui("버튼을 눌러 이야기해주세요.")
    try:
        run_button_loop(state, pending)
    except KeyboardInterrupt:
        print("\n프로그램 종료")
    finally:
        pending.put(None)
        shutdown_llm_scheduler()
        stop_playback()
        cleanup()
