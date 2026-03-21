"""메인 스레드: 버튼 폴링·녹음·파일 큐 적재."""

from __future__ import annotations

import queue
import shutil
import time
import uuid

from ..button import is_pressed
from ..config import RECORDING_PATH
from ..gui_client import show_gui
from ..recorder import record_while_pressed
from ..state import State, state_lock
from ..tts import stop_playback


def run_button_loop(state: State, pending: queue.Queue[tuple[str, int] | None]) -> None:
    """버튼이 눌릴 때까지 폴링하고, 눌리면 녹음 후 큐에 (경로, utterance_gen)을 넣음."""
    while True:
        if not is_pressed():
            time.sleep(0.05)
            continue

        stop_playback()
        # 새 녹음 시작 → 진행 중 LLM/응답 TTS 무효화 (재생은 위에서 이미 중단)
        with state_lock:
            state.generation += 1
            utterance_gen = state.generation

        show_gui("듣고 있어요...")

        success = record_while_pressed(is_pressed)

        if success:
            unique = f"/tmp/va_rec_{uuid.uuid4().hex}.wav"
            try:
                shutil.copy2(RECORDING_PATH, unique)
            except OSError as e:
                print(f"녹음 복사 실패: {e}")
                show_gui("녹음 복사에 실패했어요.")
            else:
                pending.put((unique, utterance_gen))
                show_gui("다 들었어요...")
        else:
            show_gui("쉬는 중이에요.")

        while is_pressed():
            time.sleep(0.1)

        time.sleep(0.05)
