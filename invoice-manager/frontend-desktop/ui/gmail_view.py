"""Gmail account view builders for desktop UI."""

from __future__ import annotations

from typing import Any, Callable

import flet as ft


def build_gmail_account_card(
    account: dict[str, Any],
    on_save: Callable[[int, str, str], None],
    on_toggle_active: Callable[[int, bool], None],
    on_delete: Callable[[int], None],
    on_connect: Callable[[int], None],
    on_sync: Callable[[int], None],
    sync_summary: dict[str, Any] | None = None,
) -> ft.Card:
    """Build a Gmail account settings card."""
    label_field = ft.TextField(
        label="Gmail cimke neve",
        value=str(account.get("label_name") or "InvoiceManager"),
    )
    query_field = ft.TextField(
        label="Kiegeszito Gmail query",
        value=str(account.get("gmail_query") or ""),
        multiline=True,
        min_lines=2,
        max_lines=4,
    )

    status_chip = ft.Container(
        content=ft.Text(
            "Aktiv" if account.get("is_active") else "Inaktiv",
            size=11,
            color=ft.colors.GREEN_800 if account.get("is_active") else ft.colors.ORANGE_800,
        ),
        bgcolor=ft.colors.GREEN_50 if account.get("is_active") else ft.colors.ORANGE_50,
        border_radius=4,
        padding=ft.padding.symmetric(4, 8),
    )
    oauth_chip = ft.Container(
        content=ft.Text(
            "Google kapcsolva" if account.get("oauth_connected") else "Nincs kapcsolva",
            size=11,
            color=ft.colors.BLUE_800 if account.get("oauth_connected") else ft.colors.RED_700,
        ),
        bgcolor=ft.colors.BLUE_50 if account.get("oauth_connected") else ft.colors.RED_50,
        border_radius=4,
        padding=ft.padding.symmetric(4, 8),
    )

    summary_block: ft.Control
    if sync_summary:
        sample_controls: list[ft.Control] = []
        for msg in (sync_summary.get("sample_messages") or [])[:20]:
            flags: list[str] = []
            if msg.get("has_payment_link"):
                flags.append("Fizetesi link gyanus")
            if msg.get("has_invoice_hint"):
                flags.append("Szamla kulcsszo gyanus")

            sample_controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(str(msg.get("subject") or "(Nincs targy)"), size=12, weight=ft.FontWeight.W_600),
                            ft.Text(str(msg.get("from") or ""), size=11, color=ft.colors.GREY_700),
                            ft.Text(str(msg.get("snippet") or "(Nincs kivonat)"), size=11, color=ft.colors.GREY_800),
                            ft.Text(
                                "Osszeg becsles: {amount} {currency}".format(
                                    amount=msg.get("amount_guess") if msg.get("amount_guess") is not None else "-",
                                    currency=msg.get("currency_guess") or "",
                                ),
                                size=11,
                                color=ft.colors.GREY_800,
                            ),
                            ft.Text(
                                "Link becsles: {link}".format(link=msg.get("payment_link_guess")),
                                size=11,
                                color=ft.colors.BLUE_700,
                            )
                            if msg.get("payment_link_guess")
                            else ft.Container(height=0),
                            ft.Text(" | ".join(flags), size=10, color=ft.colors.BLUE_700) if flags else ft.Container(height=0),
                        ],
                        spacing=2,
                    ),
                    bgcolor=ft.colors.WHITE,
                    border=ft.border.all(1, ft.colors.BLUE_GREY_100),
                    border_radius=6,
                    padding=8,
                )
            )

        summary_block = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Utolso szinkron: {synced}\nTalalt levelek: {scanned} | Fizetesi link gyanus: {links} | "
                        "Szamla kulcsszo gyanus: {hints}\n"
                        "Importalt szamlak: {imported} | Kihagyva (nincs osszeg): {no_amount} | "
                        "Kihagyva (duplikalt): {duplicates}".format(
                            synced=sync_summary.get("synced_at", "-"),
                            scanned=sync_summary.get("scanned_messages", 0),
                            links=sync_summary.get("payment_link_hits", 0),
                            hints=sync_summary.get("invoice_hint_hits", 0),
                            imported=sync_summary.get("imported_invoices", 0),
                            no_amount=sync_summary.get("skipped_no_amount", 0),
                            duplicates=sync_summary.get("skipped_duplicates", 0),
                        ),
                        size=12,
                        color=ft.colors.GREY_800,
                    ),
                    ft.Column(sample_controls, spacing=6) if sample_controls else ft.Container(height=0),
                ],
                spacing=8,
            ),
            bgcolor=ft.colors.BLUE_GREY_50,
            border_radius=6,
            padding=10,
        )
    else:
        summary_block = ft.Container(height=0)

    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(str(account.get("email", "")), size=16, weight=ft.FontWeight.W_600),
                            status_chip,
                            oauth_chip,
                        ],
                        wrap=True,
                    ),
                    ft.Text(
                        "Tipp: Gmail-ben cimkezd a relevans (szamla/fizetesi link) leveleket erre a cimkere.",
                        size=12,
                        color=ft.colors.GREY_700,
                    ),
                    label_field,
                    query_field,
                    ft.Row(
                        [
                            ft.OutlinedButton(
                                "Google csatlakozas" if not account.get("oauth_connected") else "Ujracsatlakozas",
                                on_click=lambda _e, i=account["id"]: on_connect(i),
                            ),
                            ft.OutlinedButton(
                                "Szinkron",
                                on_click=lambda _e, i=account["id"]: on_sync(i),
                                disabled=not account.get("oauth_connected"),
                            ),
                            ft.ElevatedButton(
                                "Mentes",
                                on_click=lambda _e, i=account["id"]: on_save(
                                    i,
                                    label_field.value or "",
                                    query_field.value or "",
                                ),
                            ),
                            ft.OutlinedButton(
                                "Inaktivalas" if account.get("is_active") else "Aktivalas",
                                on_click=lambda _e, i=account["id"], a=bool(account.get("is_active")): on_toggle_active(
                                    i, not a
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE_OUTLINE,
                                icon_color=ft.colors.RED_400,
                                on_click=lambda _e, i=account["id"]: on_delete(i),
                            ),
                        ],
                        wrap=True,
                        spacing=8,
                    ),
                    summary_block,
                ],
                spacing=8,
            ),
            padding=16,
        ),
    )
