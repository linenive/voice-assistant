import subprocess
import threading
import time
from collections.abc import Callable

from gtts import gTTS

from .config import RESPONSE_PATH, ALSA_PLAYBACK_DEVICE

_play_lock = threading.Lock()
_speak_lock = threading.Lock()
_proc: subprocess.Popen | None = None


def stop_playback() -> bool:
    """재생 중인 mpg321 프로세스를 중단합니다. 실제로 재생을 끊었으면 True (인터럽트)."""
    global _proc
    with _play_lock:
        p = _proc
        _proc = None
    if p is None:
        return False
    if p.poll() is not None:
        return False
    try:
        p.terminate()
        p.wait(timeout=2)
    except Exception:
        try:
            p.kill()
            p.wait(timeout=1)
        except Exception:
            pass
    return True


def speak(text: str, should_stop: Callable[[], bool] | None = None) -> None:
    """텍스트를 음성으로 변환 후 재생. should_stop이 True이면 재생을 끊고 반환합니다."""
    global _proc
    if not (text or "").strip():
        return
    with _speak_lock:
        stop_playback()
        p: subprocess.Popen | None = None
        try:
            tts = gTTS(text=text, lang="ko")
            tts.save(RESPONSE_PATH)
            with _play_lock:
                _proc = subprocess.Popen(
                    ["mpg321", "-a", ALSA_PLAYBACK_DEVICE, RESPONSE_PATH],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                p = _proc
            if p is not None:
                if should_stop is None:
                    p.wait()
                else:
                    while p.poll() is None:
                        if should_stop():
                            try:
                                p.terminate()
                                p.wait(timeout=2)
                            except Exception:
                                try:
                                    p.kill()
                                    p.wait(timeout=1)
                                except Exception:
                                    pass
                            break
                        time.sleep(0.05)
        except Exception as e:
            print(f"TTS 오류: {e}")
        finally:
            with _play_lock:
                if p is not None and _proc is p:
                    _proc = None
