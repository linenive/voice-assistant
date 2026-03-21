"""LLM 예약 슬롯 + 단일 daemon 스레드에서 순차 실행."""

from __future__ import annotations

import threading

from ..gui_client import show_gui
from ..history import add_message
from ..llm import ask_claude
from ..partitions import PARTITION_ASSISTANT
from ..state import State, state_lock, stale
from ..tts import speak

LlmJob = tuple[State, int, list]

_llm_sched = threading.Condition()
_llm_pending: LlmJob | None = None
_llm_scheduler_stop = False


def schedule_llm(job: LlmJob) -> None:
    """다음에 돌릴 LLM 작업만 남김(대기 중이던 예전 예약은 폐기)."""
    global _llm_pending
    with _llm_sched:
        _llm_pending = job
        _llm_sched.notify()


def llm_scheduler_loop() -> None:
    """단일 daemon 스레드: 예약된 LLM을 순서대로 하나씩 실행."""
    global _llm_pending
    while True:
        with _llm_sched:
            while _llm_pending is None and not _llm_scheduler_stop:
                _llm_sched.wait()
            if _llm_scheduler_stop and _llm_pending is None:
                break
            job = _llm_pending
            _llm_pending = None
        if job is None:
            continue
        state, request_gen, messages_snapshot = job
        _llm_worker(state, request_gen, messages_snapshot)


def shutdown_llm_scheduler() -> None:
    """종료 시 스케줄러 루프를 깨움."""
    global _llm_scheduler_stop, _llm_pending
    with _llm_sched:
        _llm_scheduler_stop = True
        _llm_pending = None
        _llm_sched.notify()


def _llm_worker(state: State, request_gen: int, messages_snapshot: list) -> None:
    """백그라운드에서 LLM 호출. 세대가 바뀌면 응답·기록·TTS를 모두 건너뜁니다. 기록은 TTS보다 먼저 반영."""
    try:
        response = ask_claude(messages_snapshot)
    except Exception as e:
        print(f"LLM 워커 오류: {e}")
        response = "죄송해요, 잠시 문제가 생겼어요. 다시 말씀해주세요."

    if stale(state, request_gen):
        return

    print(f"어시스턴트: {response}")
    show_gui(f'저: "{response}"', partition=PARTITION_ASSISTANT)

    if stale(state, request_gen):
        return

    # 기록은 TTS보다 먼저; 세대는 락 안에서 다시 확인(API~저장 사이에 버튼이 들어올 수 있음)
    with state_lock:
        if request_gen != state.generation:
            return
        state.messages = add_message(state.messages, "assistant", response)

    speak(response, should_stop=lambda: stale(state, request_gen))
