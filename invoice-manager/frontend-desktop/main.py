"""Invoice Manager desktop entrypoint."""

from __future__ import annotations

import flet as ft

from services.api import (
    create_account,
    create_invoice,
    create_recurring,
    delete_account,
    delete_invoice,
    delete_recurring,
    get_account_defaults,
    get_accounts,
    get_health,
    get_invoices,
    get_recurring,
    mark_paid,
    pause_recurring,
    start_account_oauth,
    sync_account,
    update_account_filters,
    update_recurring,
)
from ui.gmail_view import build_gmail_account_card
from ui.invoice_dialogs import open_add_invoice_dialog, show_invoice_delete_dialog
from ui.invoice_view import build_invoice_card
from ui.recurring_dialogs import open_recurring_dialog, show_recurring_delete_dialog
from ui.recurring_view import build_recurring_card
from ui.runner import run_app


def main(page: ft.Page):
    """Main application."""
    page.title = "Szamla Kezelo"
    page.window_width = 700
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    api_status = {"ok": False, "version": ""}
    main_view = "invoices"
    invoices: list[dict] = []
    recurring_list: list[dict] = []
    gmail_accounts: list[dict] = []
    gmail_defaults: dict = {}
    gmail_sync_summaries: dict[int, dict] = {}
    active_tab = "unpaid"

    invoice_list_ref = ft.Ref[ft.Column]()
    status_text_ref = ft.Ref[ft.Text]()
    invoices_toolbar_ref = ft.Ref[ft.Row]()
    recurring_toolbar_ref = ft.Ref[ft.Row]()
    gmail_toolbar_ref = ft.Ref[ft.Row]()

    def show_error(msg: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color=ft.colors.WHITE),
            bgcolor=ft.colors.ERROR,
        )
        page.snack_bar.open = True
        page.update()

    def check_backend() -> dict:
        try:
            data = get_health()
            return {"ok": True, "version": data.get("version", "N/A")}
        except Exception:
            return {"ok": False, "version": ""}

    def build_invoice_list():
        if not invoice_list_ref.current:
            return
        invoice_list_ref.current.controls.clear()

        if not api_status["ok"]:
            invoice_list_ref.current.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Inditsd el a backendet: cd backend && python app.py",
                        size=14,
                        color=ft.colors.GREY_600,
                    ),
                    padding=20,
                )
            )
        elif not invoices:
            invoice_list_ref.current.controls.append(
                ft.Container(
                    content=ft.Text("Nincs megjelenitheto szamla", size=14, color=ft.colors.GREY_600),
                    padding=20,
                )
            )
        else:
            for inv in invoices:
                invoice_list_ref.current.controls.append(
                    build_invoice_card(
                        page=page,
                        invoice=inv,
                        on_mark_paid=do_mark_paid,
                        on_delete=confirm_delete,
                        show_error=show_error,
                    )
                )
        page.update()

    def build_recurring_list():
        if not invoice_list_ref.current:
            return
        invoice_list_ref.current.controls.clear()

        if not api_status["ok"]:
            invoice_list_ref.current.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Inditsd el a backendet: cd backend && python app.py",
                        size=14,
                        color=ft.colors.GREY_600,
                    ),
                    padding=20,
                )
            )
        elif not recurring_list:
            invoice_list_ref.current.controls.append(
                ft.Container(
                    content=ft.Text("Nincs ismetlodo szamla", size=14, color=ft.colors.GREY_600),
                    padding=20,
                )
            )
        else:
            for rec in recurring_list:
                invoice_list_ref.current.controls.append(
                    build_recurring_card(
                        rec=rec,
                        on_pause=do_pause_recurring,
                        on_edit=open_edit_recurring_dialog,
                        on_delete=confirm_delete_recurring,
                    )
                )
        page.update()

    def build_gmail_list():
        if not invoice_list_ref.current:
            return
        invoice_list_ref.current.controls.clear()

        if not api_status["ok"]:
            invoice_list_ref.current.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Inditsd el a backendet: cd backend && python app.py",
                        size=14,
                        color=ft.colors.GREY_600,
                    ),
                    padding=20,
                )
            )
        elif not gmail_accounts:
            invoice_list_ref.current.controls.append(
                ft.Container(
                    content=ft.Text("Nincs Gmail fiok beallitva", size=14, color=ft.colors.GREY_600),
                    padding=20,
                )
            )
        else:
            for account in gmail_accounts:
                invoice_list_ref.current.controls.append(
                    build_gmail_account_card(
                        account=account,
                        on_save=save_account_filters,
                        on_toggle_active=toggle_account_active,
                        on_delete=confirm_delete_account,
                        on_connect=connect_account,
                        on_sync=sync_account_preview,
                        sync_summary=gmail_sync_summaries.get(account["id"]),
                    )
                )
        page.update()

    def load_invoices():
        nonlocal invoices
        try:
            status_map = {"unpaid": "unpaid", "paid": "paid", "all": "all"}
            invoices = get_invoices(status_map.get(active_tab, "all")) or []
        except Exception as exc:
            invoices = []
            show_error(str(exc))
        build_invoice_list()

    def load_recurring():
        nonlocal recurring_list
        try:
            recurring_list = get_recurring() or []
        except Exception as exc:
            recurring_list = []
            show_error(str(exc))
        build_recurring_list()

    def load_gmail():
        nonlocal gmail_accounts, gmail_defaults
        try:
            gmail_accounts = get_accounts() or []
            gmail_defaults = get_account_defaults() or {}
        except Exception as exc:
            gmail_accounts = []
            show_error(str(exc))
        build_gmail_list()

    def do_mark_paid(invoice_id: int):
        try:
            mark_paid(invoice_id)
            load_invoices()
        except Exception as exc:
            show_error(str(exc))

    def do_pause_recurring(recurring_id: int):
        try:
            pause_recurring(recurring_id)
            load_recurring()
        except Exception as exc:
            show_error(str(exc))

    def confirm_delete(invoice: dict):
        show_invoice_delete_dialog(
            page=page,
            invoice=invoice,
            on_confirm=lambda: (delete_invoice(invoice["id"]), load_invoices()),
            show_error=show_error,
        )

    def confirm_delete_recurring(rec: dict):
        show_recurring_delete_dialog(
            page=page,
            rec=rec,
            on_confirm=lambda: (delete_recurring(rec["id"]), load_recurring()),
            show_error=show_error,
        )

    def open_add_dialog(_e):
        open_add_invoice_dialog(
            page=page,
            on_submit=lambda data: (create_invoice(data), load_invoices()),
            show_error=show_error,
        )

    def open_add_recurring_dialog(_e):
        open_recurring_dialog(
            page=page,
            rec=None,
            on_submit=submit_recurring,
            show_error=show_error,
        )

    def open_edit_recurring_dialog(rec: dict):
        open_recurring_dialog(
            page=page,
            rec=rec,
            on_submit=submit_recurring,
            show_error=show_error,
        )

    def submit_recurring(data: dict, rec: dict | None):
        if rec:
            update_recurring(rec["id"], data)
        else:
            create_recurring(data)
        load_recurring()

    def open_add_gmail_dialog(_e):
        email_field = ft.TextField(label="Gmail cim", hint_text="pelda@gmail.com", autofocus=True)

        def close_dialog(_ev=None):
            page.dialog.open = False
            page.update()

        def submit(_ev):
            email = (email_field.value or "").strip()
            if not email:
                show_error("Email kotelezo")
                return
            try:
                create_account(
                    {
                        "email": email,
                        "label_name": gmail_defaults.get("default_label_name"),
                        "gmail_query": gmail_defaults.get("default_gmail_query"),
                    }
                )
                close_dialog()
                load_gmail()
            except Exception as exc:
                show_error(str(exc))

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Uj Gmail fiok"),
            content=email_field,
            actions=[
                ft.TextButton("Megse", on_click=close_dialog),
                ft.ElevatedButton("Hozzaadas", on_click=submit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog.open = True
        page.update()

    def save_account_filters(account_id: int, label_name: str, gmail_query: str):
        try:
            update_account_filters(
                account_id,
                {
                    "label_name": label_name,
                    "gmail_query": gmail_query,
                },
            )
            load_gmail()
        except Exception as exc:
            show_error(str(exc))

    def toggle_account_active(account_id: int, is_active: bool):
        try:
            update_account_filters(account_id, {"is_active": is_active})
            load_gmail()
        except Exception as exc:
            show_error(str(exc))

    def confirm_delete_account(account_id: int):
        def close_dialog(_ev=None):
            page.dialog.open = False
            page.update()

        def do_delete(_ev=None):
            try:
                delete_account(account_id)
                close_dialog()
                load_gmail()
            except Exception as exc:
                show_error(str(exc))

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Gmail fiok torlese"),
            content=ft.Text("Biztosan torolni szeretned ezt a Gmail fiokot?"),
            actions=[
                ft.TextButton("Megse", on_click=close_dialog),
                ft.ElevatedButton("Torles", on_click=do_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog.open = True
        page.update()

    def connect_account(account_id: int):
        try:
            start_account_oauth(account_id)
            load_gmail()
        except Exception as exc:
            show_error(str(exc))

    def sync_account_preview(account_id: int):
        try:
            result = sync_account(account_id, max_results=50)
            gmail_sync_summaries[account_id] = result
            load_gmail()
        except Exception as exc:
            show_error(str(exc))

    def on_tab_change(e):
        nonlocal active_tab
        if e.control.selected:
            active_tab = next(iter(e.control.selected), "unpaid")
        load_invoices()

    def on_main_view_change(e):
        nonlocal main_view
        if e.control.selected:
            main_view = next(iter(e.control.selected), "invoices")
        if main_view == "invoices":
            load_invoices()
        elif main_view == "recurring":
            load_recurring()
        else:
            load_gmail()
        if invoices_toolbar_ref.current and recurring_toolbar_ref.current and gmail_toolbar_ref.current:
            invoices_toolbar_ref.current.visible = main_view == "invoices"
            recurring_toolbar_ref.current.visible = main_view == "recurring"
            gmail_toolbar_ref.current.visible = main_view == "gmail"
        page.update()

    def refresh_all(_e):
        nonlocal api_status
        api_status = check_backend()
        if status_text_ref.current:
            if api_status["ok"]:
                status_text_ref.current.value = f"Backend elerheto · v{api_status['version']}"
                status_text_ref.current.color = ft.colors.GREEN_700
            else:
                status_text_ref.current.value = "Backend nem elerheto"
                status_text_ref.current.color = ft.colors.RED_700
        if main_view == "invoices":
            load_invoices()
        elif main_view == "recurring":
            load_recurring()
        else:
            load_gmail()
        page.update()

    api_status = check_backend()

    tab_selector = ft.SegmentedButton(
        selected={"unpaid"},
        on_change=on_tab_change,
        segments=[
            ft.Segment(value="unpaid", label=ft.Text("Fizetetlen")),
            ft.Segment(value="paid", label=ft.Text("Fizetett")),
            ft.Segment(value="all", label=ft.Text("Osszes")),
        ],
    )
    main_view_selector = ft.SegmentedButton(
        selected={"invoices"},
        on_change=on_main_view_change,
        segments=[
            ft.Segment(value="invoices", label=ft.Text("Szamlak")),
            ft.Segment(value="recurring", label=ft.Text("Ismetlodo")),
            ft.Segment(value="gmail", label=ft.Text("Gmail")),
        ],
    )

    invoices_toolbar = ft.Row(
        [ft.ElevatedButton("+ Uj szamla", on_click=open_add_dialog), tab_selector],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        wrap=True,
        ref=invoices_toolbar_ref,
    )
    recurring_toolbar = ft.Row(
        [ft.ElevatedButton("+ Uj ismetlodo", on_click=open_add_recurring_dialog)],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        wrap=True,
        ref=recurring_toolbar_ref,
        visible=False,
    )
    gmail_toolbar = ft.Row(
        [
            ft.ElevatedButton("+ Uj Gmail fiok", on_click=open_add_gmail_dialog),
            ft.Text("Csak szamlas/fizetesi linkes levelek szurese", size=12, color=ft.colors.GREY_700),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        wrap=True,
        ref=gmail_toolbar_ref,
        visible=False,
    )

    page.add(
        ft.AppBar(
            title=ft.Text("Szamla Kezelo"),
            center_title=True,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[ft.IconButton(ft.icons.REFRESH, on_click=refresh_all, tooltip="Frissites")],
        ),
        ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                f"Backend elerheto · v{api_status['version']}"
                                if api_status["ok"]
                                else "Backend nem elerheto",
                                ref=status_text_ref,
                                size=13,
                                color=ft.colors.GREEN_700 if api_status["ok"] else ft.colors.RED_700,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Row([main_view_selector], alignment=ft.MainAxisAlignment.CENTER),
                    invoices_toolbar,
                    recurring_toolbar,
                    gmail_toolbar,
                    ft.Container(
                        content=ft.Column(ref=invoice_list_ref, scroll=ft.ScrollMode.AUTO),
                        expand=True,
                    ),
                ],
                expand=True,
            ),
            padding=16,
            expand=True,
        ),
    )

    tab_selector.selected = {active_tab}
    load_invoices()


if __name__ == "__main__":
    run_app(main)
