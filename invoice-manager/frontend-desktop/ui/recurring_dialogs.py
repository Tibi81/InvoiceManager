"""Dialogs related to recurring invoice operations."""

from __future__ import annotations

from typing import Callable

import flet as ft


def show_recurring_delete_dialog(
    page: ft.Page,
    rec: dict,
    on_confirm: Callable[[], None],
    show_error: Callable[[str], None],
) -> None:
    """Show recurring delete confirmation dialog."""

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
        title=ft.Text("Ismetlodo szamla torlese"),
        content=ft.Text(f"Biztosan torolni szeretned: {rec['name']}?"),
        actions=[
            ft.TextButton("Megse", on_click=close_dialog),
            ft.ElevatedButton("Torles", on_click=do_delete, bgcolor=ft.colors.RED_700),
        ],
    )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def open_recurring_dialog(
    page: ft.Page,
    rec: dict | None,
    on_submit: Callable[[dict, dict | None], None],
    show_error: Callable[[str], None],
) -> None:
    """Open add/edit recurring dialog."""
    name_field = ft.TextField(label="Nev *", value=rec["name"] if rec else "", autofocus=True)
    amount_field = ft.TextField(
        label="Osszeg (Ft) *",
        value=str(rec["amount"]) if rec else "",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    day_field = ft.Dropdown(
        label="Honap napja *",
        value=str(rec["day_of_month"]) if rec else "15",
        options=[ft.dropdown.Option(key=str(i), text=f"{i}. nap") for i in range(1, 32)],
    )

    def close_dialog(_e):
        dialog.open = False
        page.update()

    def submit(_e):
        try:
            name = (name_field.value or "").strip()
            amount = float(amount_field.value or 0)
            day = int(day_field.value or 15)
            if not name:
                show_error("A nev megadasa kotelezo")
                return
            if amount <= 0:
                show_error("Az osszeg pozitiv szam kell legyen")
                return
            if not 1 <= day <= 31:
                show_error("A nap 1-31 kozott kell legyen")
                return
            data = {"name": name, "amount": amount, "day_of_month": day}
            on_submit(data, rec)
            close_dialog(None)
        except Exception as exc:
            show_error(str(exc))

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Szerkesztes" if rec else "Uj ismetlodo szamla"),
        content=ft.Column(
            [name_field, amount_field, day_field],
            height=200,
            scroll=ft.ScrollMode.AUTO,
        ),
        actions=[
            ft.TextButton("Megse", on_click=close_dialog),
            ft.ElevatedButton("Mentes" if rec else "Hozzaadas", on_click=submit),
        ],
    )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()

