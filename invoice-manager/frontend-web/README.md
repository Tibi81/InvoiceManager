# Frontend Web - React Application

Invoice Manager web interface built with React and Vite.

## Setup

### 1. Install dependencies
```bash
npm install
```

### 2. Run development server
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### 3. Build for production
```bash
npm run build
```

## Project Structure

```
frontend-web/
├── src/
│   ├── components/      # React components (to be added)
│   ├── pages/          # Page components (to be added)
│   ├── services/       # API services (to be added)
│   │   └── api.js
│   ├── App.jsx         # Main App component
│   ├── App.css
│   ├── main.jsx        # Entry point
│   └── index.css
├── public/             # Static assets
├── index.html
├── package.json
└── vite.config.js
```

## Development Notes

- Backend API: `http://localhost:5000`
- Vite proxy configured for `/api` requests
- Hot module replacement (HMR) enabled
- ESLint configured for code quality

## Next Steps

1. Create page components (Dashboard, Settings, etc.)
2. Implement API service layer (`services/api.js`)
3. Build reusable components (InvoiceCard, etc.)
4. Add routing with React Router
5. Implement state management (Context API or Zustand)
