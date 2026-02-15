"""
Invoice Manager - Desktop Application
Built with Flet (Python)
"""
import flet as ft
import requests
import subprocess
import time
import sys
import os


# Backend process
backend_process = None


def start_backend():
    """Start Flask backend as subprocess."""
    global backend_process
    
    # Path to backend directory
    backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
    
    try:
        print("🚀 Starting backend...")
        backend_process = subprocess.Popen(
            [sys.executable, 'app.py'],
            cwd=backend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for backend to start
        time.sleep(3)
        
        # Check if backend is running
        try:
            response = requests.get('http://localhost:5000/health', timeout=2)
            if response.status_code == 200:
                print("✅ Backend started successfully")
                return True
        except:
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


def main(page: ft.Page):
    """Main application."""
    page.title = "Számla Kezelő"
    page.window_width = 800
    page.window_height = 600
    page.window_icon = "assets/icon.png"  # Will add icon later
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Check backend status
    def check_backend():
        try:
            response = requests.get('http://localhost:5000/health', timeout=1)
            data = response.json()
            return data
        except:
            return None
    
    # UI Components
    status_text = ft.Text("Kapcsolódás a backend-hez...", size=16)
    version_text = ft.Text("", size=14, color=ft.colors.GREY_700)
    
    def update_status():
        backend_data = check_backend()
        if backend_data:
            status_text.value = "✅ Backend elérhető"
            status_text.color = ft.colors.GREEN
            version_text.value = f"Verzió: {backend_data.get('version', 'N/A')}"
        else:
            status_text.value = "❌ Backend nem elérhető"
            status_text.color = ft.colors.RED
            version_text.value = "Indítsd el a Flask API-t!"
        page.update()
    
    refresh_button = ft.ElevatedButton(
        "Frissítés",
        icon=ft.icons.REFRESH,
        on_click=lambda _: update_status()
    )
    
    # Layout
    page.add(
        ft.AppBar(
            title=ft.Text("📧 Számla Kezelő"),
            center_title=True,
            bgcolor=ft.colors.SURFACE_VARIANT,
        ),
        ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=20),
                    ft.Text(
                        "Fejlesztés alatt",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Backend Állapot", size=18, weight=ft.FontWeight.BOLD),
                                ft.Divider(),
                                status_text,
                                version_text,
                                ft.Container(height=10),
                                refresh_button
                            ]),
                            padding=20
                        )
                    ),
                    ft.Container(height=20),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("🚧 MVP Fejlesztés", size=18, weight=ft.FontWeight.BOLD),
                                ft.Divider(),
                                ft.Text("• Backend API alapok ✅", size=14),
                                ft.Text("• Gmail integráció ⏳", size=14),
                                ft.Text("• PDF feldolgozás ⏳", size=14),
                                ft.Text("• Desktop UI ⏳", size=14),
                            ]),
                            padding=20
                        )
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            expand=True
        )
    )
    
    # Initial status check
    update_status()


if __name__ == '__main__':
    print("=" * 50)
    print("📧 Invoice Manager - Desktop App")
    print("=" * 50)
    
    # Ask user if they want to start backend
    print("\n⚠️  Backend szükséges a működéshez!")
    print("Opciók:")
    print("1. Backend már fut → nyomd meg ENTER-t")
    print("2. Backend automatikus indítása → írd be: 'start'")
    
    choice = input("\nVálasztás: ").strip().lower()
    
    if choice == 'start':
        if not start_backend():
            print("\n❌ Backend indítása sikertelen!")
            print("Kézileg indítsd el: cd backend && python app.py")
            sys.exit(1)
    
    # Start Flet app
    try:
        ft.app(target=main)
    finally:
        if backend_process:
            stop_backend()
