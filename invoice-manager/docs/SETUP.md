# Setup Guide

Complete setup instructions for Invoice Manager development.

## Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Gmail API Credentials** - See setup below
- **Git** - [Download](https://git-scm.com/)

---

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/invoice-manager.git
cd invoice-manager
```

---

## 2. Gmail API Setup

### 2.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Invoice Manager"
3. Enable Gmail API:
   - Navigate to **APIs & Services > Library**
   - Search for "Gmail API"
   - Click **Enable**

### 2.2 Create OAuth Credentials

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Configure consent screen if prompted:
   - User Type: **External**
   - App name: **Invoice Manager**
   - User support email: Your email
   - Developer contact: Your email
4. Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: **Invoice Manager Desktop**
5. Download credentials JSON file
6. Save as `gmail_credentials.json` (will be used later)

### 2.3 Add Test Users

Since the app is in development mode:
1. Go to **OAuth consent screen**
2. Add test users (your Gmail addresses that you'll connect)

---

## 3. Backend Setup

### 3.1 Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 3.3 Configure Environment

```bash
# Copy example .env file
cp .env.example .env

# Edit .env and add:
# - Gmail Client ID (from Google Cloud Console)
# - Gmail Client Secret (from Google Cloud Console)
# - Generate a random SECRET_KEY
```

Example `.env`:
```env
SECRET_KEY=your-random-secret-key-here
GMAIL_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-abc123def456
DEBUG=True
```

### 3.4 Run Backend

```bash
python app.py
```

You should see:
```
✅ Database tables created
🚀 Starting Invoice Manager API...
📍 Running on http://localhost:5000
```

Test it:
```bash
curl http://localhost:5000/health
```

---

## 4. Web Frontend Setup

### 4.1 Install Dependencies

```bash
cd frontend-web
npm install
```

### 4.2 Run Development Server

```bash
npm run dev
```

You should see:
```
VITE ready in XXX ms
➜  Local:   http://localhost:3000/
```

Open `http://localhost:3000` in your browser.

---

## 5. Desktop Frontend Setup

### 5.1 Install Dependencies

```bash
cd frontend-desktop
pip install -r requirements.txt
```

### 5.2 Run Desktop App

```bash
python main.py
```

The application window will open.

---

## 6. Verify Setup

### Backend
- ✅ Health endpoint: http://localhost:5000/health
- ✅ Root endpoint: http://localhost:5000/
- ✅ Database file created: `backend/invoices.db`

### Web Frontend
- ✅ Opens in browser: http://localhost:3000
- ✅ Shows "Backend elérhető" status
- ✅ Displays API version

### Desktop
- ✅ Window opens
- ✅ Shows backend status
- ✅ Can refresh connection

---

## 7. Development Workflow

### Start Development Session

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py
```

**Terminal 2 - Web Frontend:**
```bash
cd frontend-web
npm run dev
```

**Terminal 3 - Desktop (optional):**
```bash
cd frontend-desktop
python main.py
```

---

## 8. Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'flask'`
- **Solution:** Activate virtual environment and run `pip install -r requirements.txt`

**Problem:** `FileNotFoundError: .env file not found`
- **Solution:** Copy `.env.example` to `.env` and configure

**Problem:** Gmail API errors
- **Solution:** Check credentials in `.env`, ensure Gmail API is enabled

### Frontend Issues

**Problem:** `Cannot connect to backend`
- **Solution:** Ensure backend is running on port 5000

**Problem:** `npm: command not found`
- **Solution:** Install Node.js

**Problem:** CORS errors
- **Solution:** Check backend CORS settings in `config.py`

### Desktop Issues

**Problem:** `ModuleNotFoundError: No module named 'flet'`
- **Solution:** `pip install -r requirements.txt` in frontend-desktop

**Problem:** Backend not starting automatically
- **Solution:** Start backend manually first, then run desktop app

---

## 9. Next Steps

After setup is complete:

1. **Read the documentation:**
   - [agent.md](../agent.md) - Development guidelines
   - [API.md](API.md) - API documentation

2. **Start developing:**
   - Backend: Implement Gmail service
   - Frontend: Build UI components
   - Desktop: Port web UI to Flet

3. **Join development:**
   - Check issues on GitHub
   - Read CONTRIBUTING.md
   - Submit pull requests

---

## 10. Production Deployment (Future)

This guide is for **development only**. Production deployment will require:

- ✅ Environment variable management (no .env files)
- ✅ Database migrations
- ✅ HTTPS/SSL certificates
- ✅ Proper OAuth consent screen verification
- ✅ Error logging and monitoring
- ✅ Backup strategy

---

**Need help?** Open an issue on GitHub or contact the maintainer.
