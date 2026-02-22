"""
Invoice Manager - Desktop Application
Built with Flet (Python)
"""
import flet as ft
import requests
import subprocess
import sys
import os
import time
from datetime import datetime

from services.api import (
    get_health,
    get_invoices,
    create_invoice,
    mark_paid,
    delete_invoice,
    get_qr_url,
)

# Backend process
backend_process = None


def start_backend():
    """Start Flask backend as subprocess."""
    global backend_process
    backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
    try:
        print("🚀 Starting backend...")
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
                print("✅ Backend started successfully")
                return True
        except Exception:
            pass
        print("⚠️  Backend may not be running properly")
        return False
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False


def stop_backend():
    """Stop Flask backend."""
    global backend_process
    if backend_process:
        print("🛑 Stopping backend...")
        backend_process.terminate()
        backend_process.wait()


def format_date(date_str: str) -> str:
    """Format date for Hungarian locale."""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y. %b %d.").replace("Jan", "jan").replace("Feb", "feb")
    except Exception:
        return date_str


def format_amount(amount: float, currency: str = "HUF") -> str:
    """Format amount with thousand separators."""
    return f"{amount:,.0f}".replace(",", " ") + " " + currency


def main(page: ft.Page):
    """Main application."""
    page.title = "Számla Kezelő"
    page.window_width = 700
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    # State
    api_status = {"ok": False, "version": ""}
    invoices = []
    active_tab = "unpaid"
    marking_paid_id = None
    error_message = None

    # Refs for dynamic content
    invoice_list_ref = ft.Ref[ft.Column]()
    status_text_ref = ft.Ref[ft.Text]()
    error_banner_ref = ft.Ref[ft.Container]()

    def show_error(msg: str):
        """Display error in snackbar."""
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color=ft.colors.WHITE),
            bgcolor=ft.colors.ERROR,
        )
        page.snack_bar.open = True
        page.update()

    def check_backend():
        """Check if backend is available."""
        try:
            data = get_health()
            return {"ok": True, "version": data.get("version", "N/A")}
        except Exception:
            return {"ok": False, "version": ""}

    def load_invoices():
        """Load invoices based on active tab."""
        nonlocal invoices
        try:
            status_map = {"unpaid": "unpaid", "paid": "paid", "all": "all"}
            invoices = get_invoices(status_map.get(active_tab, "all")) or []
        except Exception as e:
            invoices = []
            show_error(str(e))
        build_invoice_list()

    def build_invoice_list():
        """Rebuild the invoice list UI."""
        if not invoice_list_ref.current:
            return
        invoice_list_ref.current.controls.clear()

        if not api_status["ok"]:
            invoice_list_ref.current.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Indítsd el a backendet: cd backend && python app.py",
                        size=14,
                        color=ft.colors.GREY_600,
                    ),
                    padding=20,
                )
            )
        elif not invoices:
            invoice_list_ref.current.controls.append(
                ft.Container(
                    content=ft.Text("Nincs megjeleníthető számla", size=14, color=ft.colors.GREY_600),
                    padding=20,
                )
            )
        else:
            for inv in invoices:
                card = build_invoice_card(inv)
                invoice_list_ref.current.controls.append(card)

        page.update()

    def build_invoice_card(invoice: dict) -> ft.Card:
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

        def make_toggle_qr(container):
            def toggle(e):
                container.visible = not container.visible
                page.update()
            return toggle

        # Actions row
        actions = []
        if not invoice.get("paid"):
            actions.append(
                ft.ElevatedButton(
                    "Fizetve",
                    on_click=lambda e, i=invoice: do_mark_paid(i["id"]),
                    style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_700),
                )
            )
        if invoice.get("has_payment_link"):
            actions.append(
                ft.OutlinedButton(
                    "Fizetési link",
                    on_click=lambda e, url=invoice.get("payment_link", ""): (
                        page.launch_url(url) if url else None
                    ),
                )
            )

        def on_qr_click(e):
            if invoice.get("has_qr"):
                make_toggle_qr(qr_container)(e)
            else:
                show_error("Nincs IBAN megadva ehhez a számlához")

        actions.append(
            ft.OutlinedButton(
                "QR kód",
                on_click=on_qr_click,
            )
        )
        actions.append(
            ft.IconButton(
                icon=ft.icons.DELETE_OUTLINE,
                icon_color=ft.colors.RED_400,
                on_click=lambda e, i=invoice: confirm_delete(i),
            )
        )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(invoice["name"], size=16, weight=ft.FontWeight.W_600),
                                *([ft.Container(
                                    content=ft.Text("Ismétlődő", size=11, color=ft.colors.BLUE_700),
                                    bgcolor=ft.colors.BLUE_50,
                                    padding=ft.padding.symmetric(4, 8),
                                    border_radius=4,
                                )] if invoice.get("is_recurring") else []),
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
                            f"Esedékesség: {format_date(invoice['due_date'])}",
                            size=13,
                            color=ft.colors.GREY_700,
                        ),
                        ft.Row(actions, wrap=True, spacing=8),
                        qr_container,
                    ],
                    spacing=6,
                ),
                padding=16,
            ),
        )

    def do_mark_paid(invoice_id: int):
        """Mark invoice as paid."""
        nonlocal marking_paid_id
        marking_paid_id = invoice_id
        page.update()
        try:
            mark_paid(invoice_id)
            load_invoices()
        except Exception as e:
            show_error(str(e))
        finally:
            marking_paid_id = None
            page.update()

    def confirm_delete(invoice: dict):
        """Show delete confirmation dialog."""

        def close_dialog(e):
            dialog.open = False
            page.update()

        def do_delete(e):
            try:
                delete_invoice(invoice["id"])
                load_invoices()
                close_dialog(e)
            except Exception as err:
                show_error(str(err))

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Számla törlése"),
            content=ft.Text(f"Biztosan törölni szeretnéd: {invoice['name']}?"),
            actions=[
                ft.TextButton("Mégse", on_click=close_dialog),
                ft.ElevatedButton("Törlés", on_click=do_delete, bgcolor=ft.colors.RED_700),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def open_add_dialog(e):
        """Open add invoice dialog."""
        today = datetime.now().strftime("%Y-%m-%d")
        name_field = ft.TextField(label="Számla neve *", autofocus=True)
        amount_field = ft.TextField(label="Összeg (Ft) *", keyboard_type=ft.KeyboardType.NUMBER)
        due_field = ft.TextField(
            label="Esedékesség (ÉÉÉÉ-HH-NN) *",
            hint_text="2026-02-20",
            value=today,
        )
        iban_field = ft.TextField(label="IBAN (QR kódhoz)", hint_text="HU42...")
        link_field = ft.TextField(label="Fizetési link", hint_text="https://...")

        def close_dialog(e):
            add_dialog.open = False
            page.update()

        def submit_add(e):
            try:
                name = name_field.value.strip()
                amount = float(amount_field.value or 0)
                due = due_field.value.strip()
                if not name:
                    show_error("A név megadása kötelező")
                    return
                if amount <= 0:
                    show_error("Az összeg pozitív szám kell legyen")
                    return
                if not due:
                    show_error("Az esedékesség megadása kötelező")
                    return
                data = {
                    "name": name,
                    "amount": amount,
                    "due_date": due,
                    "iban": iban_field.value.strip() or None,
                    "payment_link": link_field.value.strip() or None,
                }
                create_invoice(data)
                load_invoices()
                close_dialog(e)
            except Exception as err:
                show_error(str(err))

        add_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Új számla"),
            content=ft.Column(
                [name_field, amount_field, due_field, iban_field, link_field],
                height=320,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Mégse", on_click=close_dialog),
                ft.ElevatedButton("Hozzáadás", on_click=submit_add),
            ],
        )
        page.overlay.append(add_dialog)
        add_dialog.open = True
        page.update()

    def on_tab_change(e):
        """Handle tab selection change."""
        nonlocal active_tab
        if e.control.selected:
            active_tab = next(iter(e.control.selected), "unpaid")
        load_invoices()

    def refresh_all(e):
        """Refresh backend status and invoices."""
        nonlocal api_status
        api_status = check_backend()
        if status_text_ref.current:
            if api_status["ok"]:
                status_text_ref.current.value = f"✅ Backend elérhető · v{api_status['version']}"
                status_text_ref.current.color = ft.colors.GREEN_700
            else:
                status_text_ref.current.value = "❌ Backend nem elérhető"
                status_text_ref.current.color = ft.colors.RED_700
        load_invoices()
        page.update()

    # Initial backend check
    api_status = check_backend()

    # Tab selector
    tab_selector = ft.SegmentedButton(
        selected={"unpaid"},
        on_change=on_tab_change,
        segments=[
            ft.Segment(value="unpaid", label=ft.Text("Fizetetlen")),
            ft.Segment(value="paid", label=ft.Text("Fizetett")),
            ft.Segment(value="all", label=ft.Text("Összes")),
        ],
    )

    # Main layout
    page.add(
        ft.AppBar(
            title=ft.Text("📧 Számla Kezelő"),
            center_title=True,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.IconButton(ft.icons.REFRESH, on_click=refresh_all, tooltip="Frissítés"),
            ],
        ),
        ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                f"✅ Backend elérhető · v{api_status['version']}" if api_status["ok"] else "❌ Backend nem elérhető",
                                ref=status_text_ref,
                                size=13,
                                color=ft.colors.GREEN_700 if api_status["ok"] else ft.colors.RED_700,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton("+ Új számla", on_click=open_add_dialog),
                            tab_selector,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        wrap=True,
                    ),
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

    # Set initial tab
    tab_selector.selected = {active_tab}
    load_invoices()


if __name__ == "__main__":
    print("=" * 50)
    print("📧 Invoice Manager - Desktop App")
    print("=" * 50)
    print("\n⚠️  Backend szükséges a működéshez!")
    print("Opciók:")
    print("1. Backend már fut → nyomd meg ENTER-t")
    print("2. Backend automatikus indítása → írd be: 'start'")

    choice = input("\nVálasztás: ").strip().lower()

    if choice == "start":
        if not start_backend():
            print("\n❌ Backend indítása sikertelen!")
            print("Kézileg indítsd el: cd backend && python app.py")
            sys.exit(1)

    try:
        ft.app(target=main)
    finally:
        if backend_process:
            stop_backend()
