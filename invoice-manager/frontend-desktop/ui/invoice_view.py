"""Invoice view builders for desktop UI."""

from __future__ import annotations

from typing import Callable

import flet as ft

from services.api import get_qr_url
from ui.formatters import format_amount, format_date, get_days_until_due, get_due_status_text


def build_invoice_card(
    page: ft.Page,
    invoice: dict,
    on_mark_paid: Callable[[int], None],
    on_delete: Callable[[dict], None],
    show_error: Callable[[str], None],
) -> ft.Card:
    """Build a single invoice card."""
    qr_container = ft.Container(
        content=ft.Image(
            src=get_qr_url(invoice["id"]),
            width=200,
            height=200,
            fit=ft.ImageFit.CONTAIN,
        ),
        visible=False,
        padding=ft.padding.only(top=10),
    )

    def toggle_qr(_e):
        if invoice.get("has_qr"):
            qr_container.visible = not qr_container.visible
            page.update()
        else:
            show_error("Nincs IBAN megadva ehhez a szamlahoz")

    actions: list[ft.Control] = []
    if not invoice.get("paid"):
        actions.append(
            ft.ElevatedButton(
                "Fizetve",
                on_click=lambda _e, i=invoice: on_mark_paid(i["id"]),
                style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_700),
            )
        )
    if invoice.get("has_payment_link"):
        actions.append(
            ft.OutlinedButton(
                "Fizetesi link",
                on_click=lambda _e, url=invoice.get("payment_link", ""): (
                    page.launch_url(url) if url else None
                ),
            )
        )
    actions.append(ft.OutlinedButton("QR kod", on_click=toggle_qr))
    actions.append(
        ft.IconButton(
            icon=ft.icons.DELETE_OUTLINE,
            icon_color=ft.colors.RED_400,
            on_click=lambda _e, i=invoice: on_delete(i),
        )
    )

    paid = invoice.get("paid", False)
    due_status = get_due_status_text(invoice.get("due_date", ""), paid)
    overdue = due_status and get_days_until_due(invoice.get("due_date", "")) < 0

    recurring_badge: list[ft.Control] = []
    if invoice.get("is_recurring"):
        recurring_badge.append(
            ft.Container(
                content=ft.Text("Ismetlodo", size=11, color=ft.colors.BLUE_700),
                bgcolor=ft.colors.BLUE_50,
                padding=ft.padding.symmetric(4, 8),
                border_radius=4,
            )
        )

    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(invoice["name"], size=16, weight=ft.FontWeight.W_600),
                            ft.Container(
                                content=ft.Text(
                                    "Fizetve" if paid else "Fizetetlen",
                                    size=11,
                                    color=ft.colors.GREEN_800 if paid else ft.colors.ORANGE_800,
                                ),
                                bgcolor=ft.colors.GREEN_50 if paid else ft.colors.ORANGE_50,
                                padding=ft.padding.symmetric(4, 8),
                                border_radius=4,
                            ),
                            *recurring_badge,
                        ],
                        wrap=True,
                    ),
                    ft.Text(
                        format_amount(invoice["amount"], invoice.get("currency", "HUF")),
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.GREEN_800,
                    ),
                    ft.Text(
                        f"Esedekesseg: {format_date(invoice['due_date'])}",
                        size=13,
                        color=ft.colors.GREY_700,
                    ),
                    ft.Text(
                        due_status,
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=ft.colors.RED_700 if overdue else ft.colors.BLUE_700,
                    )
                    if due_status
                    else ft.Container(height=0),
                    ft.Row(actions, wrap=True, spacing=8),
                    qr_container,
                ],
                spacing=6,
            ),
            padding=16,
        ),
    )

