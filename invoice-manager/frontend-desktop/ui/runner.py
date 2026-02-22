"""Runtime launcher helpers for desktop app."""

from __future__ import annotations

import sys
from typing import Callable

import flet as ft

from ui.backend_runtime import is_backend_running, start_backend, stop_backend


def run_app(target: Callable[[ft.Page], None]) -> None:
    """Run desktop app with optional backend auto-start flow."""
    print("=" * 50)
    print("Invoice Manager - Desktop App")
    print("=" * 50)
    print("\nBackend szukseges a mukodeshez.")
    print("Opcio:")
    print("1. Backend mar fut -> nyomd meg ENTER-t")
    print("2. Backend automatikus inditasa -> ird be: 'start'")

    choice = input("\nValasztas: ").strip().lower()
    if choice == "start" and not start_backend():
        print("\nBackend inditasa sikertelen!")
        print("Kezileg inditsd el: cd backend && python app.py")
        sys.exit(1)

    try:
        ft.app(target=target)
    finally:
        if is_backend_running():
            stop_backend()

