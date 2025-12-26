# Frontend Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

### Step 2: Set Up Environment
```bash
# Copy environment file
cp .env.example .env

# Edit .env if needed (default values work with local backend)
# VITE_API_URL=http://localhost:5000/api
```

### Step 3: Start Development Server
```bash
npm run dev
```

Open your browser to **http://localhost:3000** 🎉

---

## 📋 Prerequisites

Before you start, make sure you have:

- ✅ **Node.js 18+** installed (`node --version`)
- ✅ **npm 8+** installed (`npm --version`)
- ✅ **Backend API running** on port 5000

---

## 🎯 Quick Commands

```bash
# Install dependencies
npm install

# Start dev server (with hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

---

## 🐳 Docker Quick Start

### Option 1: Docker Compose (Recommended)
```bash
# From project root
docker-compose up -d

# Access frontend at http://localhost:3000
# Access backend at http://localhost:5000
```

### Option 2: Docker Only
```bash
# Build image
cd frontend
docker build -t web-crawler-frontend .

# Run container
docker run -p 3000:3000 web-crawler-frontend
```

---

## 🧪 Test the Frontend

### 1. Start Both Backend and Frontend
```bash
# Terminal 1: Start backend
cd backend
python -m flask --app api.app run

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### 2. Try These Features

**Test Content Mode:**
1. Go to http://localhost:3000/crawler
2. Select "Content Mode"
3. Enter URL: `https://example.com`
4. Select formats: txt, md
5. Click "Start Crawling"
6. Watch progress bar
7. View results in modal
8. Download files

**Test Link Mode:**
1. Select "Link Mode"
2. Enter URL: `https://example.com`
3. Select format: json
4. Choose link type: all
5. Click "Start Crawling"
6. View extracted links

**Test Bulk Upload:**
1. Click "Bulk CSV" button
2. Drag & drop example_urls.csv
3. Click "Start Crawling"
4. Monitor bulk progress

**View History:**
1. Go to http://localhost:3000/history
2. See past crawl jobs
3. Click "View Results" on completed jobs
4. Delete old jobs

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in frontend directory:

```env
# API Base URL (required)
VITE_API_URL=http://localhost:5000/api
```

### Vite Configuration

Edit `vite.config.js` for custom settings:

```javascript
export default defineConfig({
  server: {
    port: 3000,        // Change dev server port
    host: true,        // Expose to network
    proxy: {
      '/api': {        // Proxy API requests
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
})
```

### Tailwind Configuration

Customize colors in `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: { /* your colors */ },
      success: { /* your colors */ },
      // ...
    }
  }
}
```

---

## 🐛 Troubleshooting

### Port 3000 already in use
```bash
# Option 1: Use different port
npm run dev -- --port 3001

# Option 2: Kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

### API Connection Failed
```bash
# Check backend is running
curl http://localhost:5000/health

# Check CORS settings in backend/.env
CORS_ORIGINS=http://localhost:3000

# Verify API URL in frontend/.env
VITE_API_URL=http://localhost:5000/api
```

### Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

### Module Not Found
```bash
# Make sure you're in frontend directory
cd frontend

# Reinstall dependencies
npm install
```

---

## 📂 Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable React components
│   ├── pages/          # Page components (routes)
│   ├── services/       # API client
│   ├── App.jsx         # Main app component
│   └── main.jsx        # Entry point
├── public/             # Static assets
├── package.json        # Dependencies
├── vite.config.js      # Vite config
└── tailwind.config.js  # Tailwind config
```

---

## 🎨 Features Overview

### Pages
- **Home** (`/`) - Landing page with features
- **Crawler** (`/crawler`) - Main crawling interface
- **History** (`/history`) - View past crawls

### Components
- **ModeSelector** - Content/Link mode selection
- **URLInput** - URL input with validation
- **CSVUpload** - Drag-and-drop file upload
- **ProgressBar** - Real-time progress indicator
- **ResultsModal** - Results display with downloads
- **CrawlForm** - Complete crawl configuration

---

## 📱 Responsive Design

The frontend works on:
- 💻 Desktop (1920px+)
- 💻 Laptop (1024px - 1920px)
- 📱 Tablet (768px - 1024px)
- 📱 Mobile (320px - 768px)

Test responsive design:
1. Open browser DevTools (F12)
2. Click device toolbar icon
3. Select device or custom size

---

## 🔗 Useful Links

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api
- **API Health**: http://localhost:5000/health
- **Vite Docs**: https://vitejs.dev
- **Tailwind Docs**: https://tailwindcss.com
- **React Docs**: https://react.dev

---

## 📚 Next Steps

1. ✅ Run `npm install` to install dependencies
2. ✅ Start dev server with `npm run dev`
3. ✅ Test features in browser
4. ✅ Check the full README.md for detailed docs
5. ✅ Build for production with `npm run build`
6. ✅ Deploy with Docker

---

## 💡 Pro Tips

1. **Hot Reload**: Changes auto-refresh in dev mode
2. **React DevTools**: Install browser extension for debugging
3. **Network Tab**: Monitor API calls in browser DevTools
4. **Console**: Check for errors in browser console
5. **Linting**: Run `npm run lint` to check code quality

---

## 🎉 You're All Set!

Frontend is ready to use. Start crawling web pages with a beautiful UI!

Need help? Check:
- `frontend/README.md` - Full documentation
- `GETTING_STARTED.md` - Complete setup guide
- `TROUBLESHOOTING.md` - Common issues
