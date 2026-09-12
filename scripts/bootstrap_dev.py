from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _venv_python() -> str:
    if os.name == "nt":
        return os.path.join(".venv", "Scripts", "python.exe")
    return os.path.join(".venv", "bin", "python")


def _candidate_pythons() -> list[list[str]]:
    home = Path.home()
    uv_312 = home / "AppData/Roaming/uv/python/cpython-3.12.13-windows-x86_64-none/python.exe"
    candidates: list[list[str]] = []
    if uv_312.exists():
        candidates.append([str(uv_312), "-m", "venv", ".venv"])
    candidates.extend(
        (
            ["py", "-3.12", "-m", "venv", ".venv"],
            [sys.executable, "-m", "venv", ".venv"],
        )
    )
    return candidates


def main() -> int:
    created = False
    for cmd in _candidate_pythons():
        try:
            print(">>>", " ".join(cmd))
            subprocess.check_call(cmd)
            created = True
            break
        except (OSError, subprocess.CalledProcessError) as exc:
            print(f">>> skip ({exc})")
    if not created:
        print("ERROR: could not create .venv", file=sys.stderr)
        return 1

    py = _venv_python()
    subprocess.check_call([py, "-m", "pip", "install", "-U", "pip", "setuptools", "wheel"])
    subprocess.check_call([py, "-m", "pip", "install", "-e", ".[dev]"])
    ver = subprocess.check_output([py, "--version"], text=True).strip()
    print(">>> Installed OK ->", py, f"({ver})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
