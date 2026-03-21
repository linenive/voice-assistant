"""녹음 파일 큐 워커 스레드: STT → 대화·기억 → LLM 예약."""

from __future__ import annotations

import os
import queue

from ..conversation import build_recent_dialog
from ..gui_client import show_gui
from ..history import add_message
from ..memory import update_long_term_memory_from_text
from ..partitions import PARTITION_USER
from ..state import State, state_lock
from ..stt import transcribe
from ..tts import speak

from .llm_thread import schedule_llm


def recording_queue_worker(
    state: State,
    pending: queue.Queue[tuple[str, int] | None],
) -> None:
    """녹음 파일 큐 FIFO: STT → user 반영은 즉시, LLM은 슬롯에 예약만(블로킹 없음)."""
    while True:
        item = pending.get()
        if item is None:
            break

        show_gui("음성 처리 중...", partition=PARTITION_USER)
        path, utterance_gen = item
        text = transcribe(path)
        try:
            os.unlink(path)
        except OSError:
            pass

        if not text:
            speak("잘 못 들었어요, 다시 말씀해주세요.")
            continue

        print(f"할머니: {text}")
        show_gui(f'당신: "{text}"', partition=PARTITION_USER)

        with state_lock:
            state.messages = add_message(state.messages, "user", text)
            messages_snapshot = [dict(m) for m in state.messages]

        recent_dialog = build_recent_dialog(state.messages, turns=3)
        update_long_term_memory_from_text(recent_dialog)

        schedule_llm((state, utterance_gen, messages_snapshot))
