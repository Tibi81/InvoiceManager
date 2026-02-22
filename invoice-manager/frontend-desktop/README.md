# Frontend Desktop - Flet Application

Invoice Manager desktop application built with Flet (Python).

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the application
```bash
python main.py
```

The application will open in a native window.

**Note:** Backend must be running on `http://localhost:5000` for the app to work.

## Building Executable

### Build for Windows
```bash
flet build windows --icon assets/icon.ico
```

The executable will be created in the `build/` directory.

### Build for other platforms
```bash
# macOS
flet build macos --icon assets/icon.icns

# Linux
flet build linux
```

## Project Structure

```
frontend-desktop/
├── main.py           # Main application entry point
├── services/
│   └── api.py        # API client
├── assets/            # Icons and images
│   ├── icon.ico
│   └── icon.png
├── flet.yaml          # Build configuration
└── requirements.txt
```

## Features

- [x] Invoice list with tabs (Fizetetlen / Fizetett / Összes)
- [x] Invoice cards: name, amount, due date
- [x] Mark as paid
- [x] QR code display (EPC)
- [x] Payment link (opens in browser)
- [x] Add new invoice (dialog form)
- [x] Delete invoice (with confirmation)

## Development Notes

- Backend connection: `http://localhost:5000`
- Backend can be started automatically from the app (type `start` when prompted)
- Material Design components (Flet)
- Cross-platform (Windows, macOS, Linux)

## Next Steps

- [ ] Gmail account management
- [ ] Recurring invoices form
- [ ] System tray icon
- [ ] Desktop notifications
