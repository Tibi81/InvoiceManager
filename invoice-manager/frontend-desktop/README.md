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
├── components/       # Flet UI components (to be added)
├── services/         # API service layer (to be added)
├── assets/           # Icons and images
│   ├── icon.ico
│   └── icon.png
├── flet.yaml         # Build configuration
└── requirements.txt
```

## Development Notes

- Backend connection: `http://localhost:5000`
- Backend can be started automatically from the app
- Material Design components
- Cross-platform (Windows, macOS, Linux)

## Next Steps

1. Create reusable UI components (`components/`)
2. Implement API service layer (`services/api.py`)
3. Build main screens (Dashboard, Settings, etc.)
4. Add system tray integration
5. Add desktop notifications
6. Create app icon
7. Set up build pipeline

## Features to Implement

- [ ] Invoice list view
- [ ] Invoice details modal
- [ ] QR code display
- [ ] Gmail account management
- [ ] Recurring invoices form
- [ ] System tray icon
- [ ] Desktop notifications
- [ ] Auto-start with Windows
