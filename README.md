# 📧 Invoice Manager

> Automated invoice management from Gmail with web and desktop interfaces

[![Status](https://img.shields.io/badge/status-under%20development-yellow)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

Personal invoice management system that automatically processes invoices from Gmail and manages recurring bills.

---

## ✨ Features

### MVP (v1.0.0)

✅ **Email-based Invoice Processing**
- Gmail API integration (up to 2 accounts)
- Automatic PDF invoice parsing
- Payment link detection
- Extract amount, due date, IBAN automatically

✅ **Manual Recurring Invoices**
- Create templates for monthly bills (Netflix, rent, etc.)
- Automatic invoice generation on due dates
- Edit/pause/delete recurring invoices

✅ **Invoice Management**
- List view with filters: Unpaid / Paid / All
- Mark invoices as paid
- QR code generation for bank transfers (EPC standard)
- Payment link quick access

### Platforms
- 🌐 **Web UI** - React-based web application
- 💻 **Desktop App** - Native Windows application (Flet)

---

## 🏗️ Architecture

```
Backend (Flask REST API)
    ↓
┌───────────┬────────────┐
│  React    │    Flet    │
│  Web UI   │  Desktop   │
└───────────┴────────────┘
```

**Tech Stack:**
- Backend: Flask (Python 3.11+)
- Web: React + Vite
- Desktop: Flet
- Database: SQLite
- APIs: Gmail API, PDF parsing

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Gmail API credentials ([setup guide](docs/SETUP.md))

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Add your Gmail credentials
python app.py             # Runs on http://localhost:5000
```

### Web Frontend
```bash
cd frontend-web
npm install
npm run dev               # Runs on http://localhost:3000
```

### Desktop App
```bash
cd frontend-desktop
pip install -r requirements.txt
python main.py            # Opens desktop window
```

📖 **Detailed setup:** See [docs/SETUP.md](docs/SETUP.md)

---

## 📦 Project Status

### Backend
- [ ] Flask API setup
- [ ] Database models
- [ ] Gmail API integration
- [ ] PDF parsing
- [ ] QR code generation
- [ ] Recurring invoice logic
- [ ] API endpoints (CRUD)

### Web Frontend
- [ ] React setup
- [ ] Gmail account management
- [ ] Invoice list (3 views)
- [ ] Invoice details modal
- [ ] Recurring invoices form
- [ ] QR code display

### Desktop
- [ ] Flet setup
- [ ] UI components
- [ ] Backend integration
- [ ] System tray
- [ ] Build pipeline

[View detailed roadmap →](https://github.com/yourusername/invoice-manager/projects)

---

## 📁 Project Structure

```
invoice-manager/
├── backend/              # Flask REST API
│   ├── app.py
│   ├── models/
│   ├── services/
│   └── api/
│
├── frontend-web/         # React application
│   ├── src/
│   ├── public/
│   └── package.json
│
├── frontend-desktop/     # Flet desktop app
│   ├── main.py
│   ├── components/
│   └── assets/
│
├── docs/
│   ├── SETUP.md
│   └── API.md
│
└── agent.md             # AI development guide
```

---

## 🤝 Contributing

This is currently a personal project, but suggestions and bug reports are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [agent.md](agent.md) for coding guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🗺️ Roadmap

### v1.0.0 - MVP (Current)
- Email invoice processing
- Recurring invoices
- Basic invoice management
- Web + Desktop interfaces

### v1.1.0 - Enhanced Features
- Statistics dashboard
- Category/tag system
- CSV export
- Email notifications

### v1.2.0 - Advanced
- Multi-currency support
- Advanced filtering
- Bulk operations
- API webhooks

### v2.0.0 - Platform Expansion
- Mobile app (React Native)
- Multi-user support
- Cloud sync option
- Payment integrations

---

## ⚠️ Note

This project is in **early development**. Features may change, and the codebase is not production-ready yet.

**Current focus:** Backend API (MVP features)

---

## 📞 Support

- 📧 Email: kisss.tibi@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/invoice-manager/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/invoice-manager/discussions)

---

**Built with ❤️ for personal finance management**
