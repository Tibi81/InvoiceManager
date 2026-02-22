"""Backend process lifecycle helpers for the desktop app."""

from __future__ import annotations

import os
import subprocess
import sys
import time

import requests

backend_process: subprocess.Popen[str] | None = None


def start_backend() -> bool:
    """Start Flask backend as subprocess and verify health endpoint."""
    global backend_process
    backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
    try:
        print("Starting backend...")
        backend_process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=backend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        time.sleep(3)
        try:
            resp = requests.get("http://localhost:5000/health", timeout=2)
            if resp.status_code == 200:
                print("Backend started successfully")
                return True
        except Exception:
            pass
        print("Backend may not be running properly")
        return False
    except Exception as exc:
        print(f"Failed to start backend: {exc}")
        return False


def stop_backend() -> None:
    """Stop Flask backend if it is running."""
    global backend_process
    if backend_process:
        print("Stopping backend...")
        backend_process.terminate()
        backend_process.wait()
        backend_process = None


def is_backend_running() -> bool:
    """Return True when backend process is alive."""
    return backend_process is not None and backend_process.poll() is None

