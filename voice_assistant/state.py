"""공유 세션(세대·대화)과 세대 무효화 판별."""

from __future__ import annotations

import threading

from .history import load_history

state_lock = threading.Lock()


class State:
    __slots__ = ("generation", "messages")

    def __init__(self) -> None:
        self.messages = load_history()
        self.generation = 0


def stale(state: State, request_gen: int) -> bool:
    """이 요청의 세대가 이미 지났으면 True (새 녹음 버튼으로 무효화됨)."""
    with state_lock:
        return request_gen != state.generation
