"""옆 폴더 cli-gui 소스를 PYTHONPATH에 넣어 `python -m cli_gui show …` 로 창에 문구 표시."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

_LOG = "/tmp/voice_assistant_gui_client.log"
_VALID_PARTITIONS = frozenset({0, 1, 2})


def _cli_src() -> Path | None:
    # voice_assistant 패키지의 부모(프로젝트 루트) 옆의 cli-gui
    _repo = Path(__file__).resolve().parent.parent
    p = _repo.parent / "cli-gui" / "src"
    return p if (p / "cli_gui").is_dir() else None


def _touch_log() -> None:
    try:
        if not os.path.exists(_LOG):
            with open(_LOG, "w", encoding="utf-8") as f:
                f.write(f"# gui_client {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    except OSError:
        pass


_touch_log()


def show_gui(text: str, *, partition: int = 0) -> None:
    """`cli-gui show -p …`; partition은 표시 파티션(0=상, 1=중, 2=하). 기본 0."""
    if not text:
        return

    if partition not in _VALID_PARTITIONS:
        partition = 0

    # 항상 main.py 와 동일 인터프리터 (PATH 의 cli-gui 가 다른 python 을 쓰는 문제 방지)
    if importlib.util.find_spec("PyQt6") is None:
        msg = (
            "PyQt6 가 이 인터프리터에 없습니다: "
            f"{sys.executable}\n"
            "  pip install -e ../cli-gui\n"
        )
        try:
            with open(_LOG, "a", encoding="utf-8") as f:
                f.write(f"\n--- {time.strftime('%H:%M:%S')} [gui_client] {msg}\n")
        except OSError:
            pass
        return

    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    # SSH 세션에는 DISPLAY 가 비어 있는 경우가 많음 → 로컬 X11(보통 Pi 모니터)
    if not (env.get("DISPLAY") or "").strip():
        env["DISPLAY"] = ":0"
    if not (env.get("XAUTHORITY") or "").strip():
        xa = os.path.expanduser("~/.Xauthority")
        if os.path.isfile(xa):
            env["XAUTHORITY"] = xa
    src = _cli_src()
    if src is not None:
        pp = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{src}{os.pathsep}{pp}" if pp else str(src)

    argv = [sys.executable, "-m", "cli_gui", "show", "-p", str(partition), text]
    line = f"\n--- {time.strftime('%H:%M:%S')} {argv!r}\n"
    try:
        with open(_LOG, "a", encoding="utf-8", buffering=1) as logf:
            logf.write(line)
            subprocess.Popen(
                argv,
                stdin=subprocess.DEVNULL,
                stdout=logf,
                stderr=subprocess.STDOUT,
                env=env,
                text=True,
            )
    except OSError as e:
        try:
            with open(_LOG, "a", encoding="utf-8") as f:
                f.write(f"Popen 실패: {e}\n")
        except OSError:
            pass
