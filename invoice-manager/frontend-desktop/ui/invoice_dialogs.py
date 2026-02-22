"""Dialogs related to manual invoice operations."""

from __future__ import annotations

from datetime import datetime
from typing import Callable

import flet as ft


def show_invoice_delete_dialog(
    page: ft.Page,
    invoice: dict,
    on_confirm: Callable[[], None],
    show_error: Callable[[str], None],
) -> None:
    """Show invoice delete confirmation dialog."""

    def close_dialog(_e):
        dialog.open = False
        page.update()

    def do_delete(_e):
        try:
            on_confirm()
            close_dialog(None)
        except Exception as exc:
            show_error(str(exc))

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Szamla torlese"),
        content=ft.Text(f"Biztosan torolni szeretned: {invoice['name']}?"),
        actions=[
            ft.TextButton("Megse", on_click=close_dialog),
            ft.ElevatedButton("Torles", on_click=do_delete, bgcolor=ft.colors.RED_700),
        ],
    )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def open_add_invoice_dialog(
    page: ft.Page,
    on_submit: Callable[[dict], None],
    show_error: Callable[[str], None],
) -> None:
    """Open add invoice dialog."""
    today = datetime.now().strftime("%Y-%m-%d")
    name_field = ft.TextField(label="Szamla neve *", autofocus=True)
    amount_field = ft.TextField(label="Osszeg (Ft) *", keyboard_type=ft.KeyboardType.NUMBER)
    due_field = ft.TextField(
        label="Esedekesseg (YYYY-MM-DD) *",
        hint_text="2026-02-20",
        value=today,
    )
    iban_field = ft.TextField(label="IBAN (QR kodhoz)", hint_text="HU42...")
    link_field = ft.TextField(label="Fizetesi link", hint_text="https://...")

    def close_dialog(_e):
        dialog.open = False
        page.update()

    def submit_add(_e):
        try:
            name = (name_field.value or "").strip()
            amount = float(amount_field.value or 0)
            due = (due_field.value or "").strip()
            if not name:
                show_error("A nev megadasa kotelezo")
                return
            if amount <= 0:
                show_error("Az osszeg pozitiv szam kell legyen")
                return
            if not due:
                show_error("Az esedekesseg megadasa kotelezo")
                return
            data = {
                "name": name,
                "amount": amount,
                "due_date": due,
                "iban": (iban_field.value or "").strip() or None,
                "payment_link": (link_field.value or "").strip() or None,
            }
            on_submit(data)
            close_dialog(None)
        except Exception as exc:
            show_error(str(exc))

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Uj szamla"),
        content=ft.Column(
            [name_field, amount_field, due_field, iban_field, link_field],
            height=320,
            scroll=ft.ScrollMode.AUTO,
        ),
        actions=[
            ft.TextButton("Megse", on_click=close_dialog),
            ft.ElevatedButton("Hozzaadas", on_click=submit_add),
        ],
    )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()

