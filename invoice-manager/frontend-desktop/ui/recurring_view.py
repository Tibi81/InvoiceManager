"""Recurring invoice view builders for desktop UI."""

from __future__ import annotations

from typing import Callable

import flet as ft

from ui.formatters import format_amount


def build_recurring_card(
    rec: dict,
    on_pause: Callable[[int], None],
    on_edit: Callable[[dict], None],
    on_delete: Callable[[dict], None],
) -> ft.Card:
    """Build a single recurring invoice card."""
    paused_badge: list[ft.Control] = []
    if not rec.get("is_active"):
        paused_badge.append(
            ft.Container(
                content=ft.Text("Szuneteltetve", size=11, color=ft.colors.ORANGE_800),
                bgcolor=ft.colors.ORANGE_50,
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
                            ft.Text(rec["name"], size=16, weight=ft.FontWeight.W_600),
                            *paused_badge,
                        ],
                        wrap=True,
                    ),
                    ft.Text(
                        format_amount(rec["amount"], rec.get("currency", "HUF")),
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.GREEN_800,
                    ),
                    ft.Text(f"Honap {rec['day_of_month']}. napjan", size=13, color=ft.colors.GREY_700),
                    ft.Row(
                        [
                            ft.OutlinedButton(
                                "Szuneteltetes" if rec.get("is_active") else "Folytatas",
                                on_click=lambda _e, r=rec: on_pause(r["id"]),
                            ),
                            ft.OutlinedButton(
                                "Szerkesztes",
                                on_click=lambda _e, r=rec: on_edit(r),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE_OUTLINE,
                                icon_color=ft.colors.RED_400,
                                on_click=lambda _e, r=rec: on_delete(r),
                            ),
                        ],
                        wrap=True,
                        spacing=8,
                    ),
                ],
                spacing=6,
            ),
            padding=16,
        ),
    )

