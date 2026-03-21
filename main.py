import os
import queue
import shutil
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from button import cleanup, is_pressed, setup
from config import RECORDING_PATH
from conversation import build_recent_dialog
from gui_client import show_gui
from history import add_message, load_history
from llm import ask_claude
from memory import update_long_term_memory_from_text
from recorder import record_while_pressed
from stt import transcribe
from tts import speak, stop_playback


class _State:
    __slots__ = ("generation", "messages")

    def __init__(self) -> None:
        self.messages = load_history()
        self.generation = 0


state_lock = threading.Lock()

def _llm_worker(state: _State, request_gen: int, messages_snapshot: list) -> None:
    """백그라운드에서 LLM 호출. 세대가 바뀌면 응답·TTS·기록 저장을 모두 건너뜁니다."""
    try:
        response = ask_claude(messages_snapshot)
    except Exception as e:
        print(f"LLM 워커 오류: {e}")
        response = "죄송해요, 잠시 문제가 생겼어요. 다시 말씀해주세요."

    with state_lock:
        if request_gen != state.generation:
            return

    print(f"어시스턴트: {response}")
    show_gui(f'저: "{response}"', partition=2)

    with state_lock:
        if request_gen != state.generation:
            return

    def _tts_cancelled() -> bool:
        with state_lock:
            return state.generation != request_gen

    speak(response, should_stop=_tts_cancelled)

    with state_lock:
        if request_gen != state.generation:
            return
        state.messages = add_message(state.messages, "assistant", response)


def _recording_queue_worker(
    state: _State,
    executor: ThreadPoolExecutor,
    pending: queue.Queue[str | None],
) -> None:
    """녹음 파일 큐 FIFO: STT → user 반영은 즉시, LLM은 풀에 제출만(대기하지 않음)."""
    while True:
        item = pending.get()
        if item is None:
            break

        text = transcribe(item)
        try:
            os.unlink(item)
        except OSError:
            pass

        if not text:
            speak("잘 못 들었어요, 다시 말씀해주세요.")
            continue

        print(f"할머니: {text}")
        show_gui(f'당신: "{text}"', partition=1)

        with state_lock:
            state.messages = add_message(state.messages, "user", text)

        recent_dialog = build_recent_dialog(state.messages, turns=3)
        update_long_term_memory_from_text(recent_dialog)

        with state_lock:
            state.generation += 1
            request_gen = state.generation
            messages_snapshot = [dict(m) for m in state.messages]

        executor.submit(_llm_worker, state, request_gen, messages_snapshot)

        if not pending.empty():
            show_gui("음성 처리 중...", partition=1)


def main() -> None:
    print("🎙️ 음성 어시스턴트 시작!")
    print("버튼을 누르고 말씀해주세요.")

    setup()
    state = _State()
    executor = ThreadPoolExecutor(max_workers=1)
    pending: queue.Queue[str | None] = queue.Queue()

    worker = threading.Thread(
        target=_recording_queue_worker,
        args=(state, executor, pending),
        daemon=True,
    )
    worker.start()

    show_gui("버튼을 눌러 이야기해주세요.")
    try:
        while True:
            if not is_pressed():
                time.sleep(0.05)
                continue

            stop_playback()
            # 새 녹음 시작 시 진행 중인 LLM/응답 TTS를 세대로 무효화 (재생 중이면 위에서 이미 끊김)
            with state_lock:
                state.generation += 1

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
                    pending.put(unique)
                    show_gui("다 들었어요...")
            else:
                show_gui("쉬는 중이에요.")

            while is_pressed():
                time.sleep(0.1)

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n프로그램 종료")

    finally:
        pending.put(None)
        stop_playback()
        executor.shutdown(wait=True, cancel_futures=False)
        cleanup()


if __name__ == "__main__":
    main()
