# Web Crawler Frontend

Modern React frontend for the Web Crawler application, built with Vite, Tailwind CSS, and React Query.

## Features

- 🎨 Modern, responsive UI with Tailwind CSS
- ⚡ Fast development with Vite
- 🔄 Real-time progress tracking
- 📊 Visual statistics and metadata display
- 📱 Mobile-responsive design
- 🎯 Dual mode support (Content & Link extraction)
- 📁 CSV bulk upload with drag-and-drop
- 📈 Results visualization with charts
- 🔍 Extraction history with filtering
- ⬇️ Direct file downloads

## Tech Stack

- **React 18+** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **React Query** - Data fetching and caching
- **Axios** - HTTP client
- **React Dropzone** - File upload component
- **React Icons** - Icon library
- **Recharts** - Data visualization (ready for integration)

## Getting Started

### Prerequisites

- Node.js 18+ (or 16+)
- npm 8+ or yarn 1.22+

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at http://localhost:3000

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
# API URL
VITE_API_URL=http://localhost:5000/api
```

## Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Project Structure

```
frontend/
├── public/
│   ├── vite.svg           # App icon
│   └── index.html         # HTML template
├── src/
│   ├── components/        # React components
│   │   ├── ModeSelector.jsx       # Content/Link mode selection
│   │   ├── URLInput.jsx           # URL input field
│   │   ├── CSVUpload.jsx          # CSV file upload
│   │   ├── ProgressBar.jsx        # Crawling progress indicator
│   │   ├── ResultsModal.jsx       # Results display modal
│   │   └── CrawlForm.jsx          # Main crawl form
│   ├── pages/             # Page components
│   │   ├── Home.jsx               # Landing page
│   │   ├── Crawler.jsx            # Main crawler interface
│   │   └── History.jsx            # Extraction history
│   ├── services/          # API services
│   │   └── api.js                 # API client
│   ├── App.jsx            # Main app component
│   ├── main.jsx           # App entry point
│   └── index.css          # Global styles
├── package.json           # Dependencies
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind configuration
├── postcss.config.js      # PostCSS configuration
├── Dockerfile             # Docker build file
├── nginx.conf             # Nginx configuration
└── README.md              # This file
```

## Components

### ModeSelector
Mode selection UI for Content/Link extraction modes with feature descriptions.

### URLInput
URL input field with validation and error display.

### CSVUpload
Drag-and-drop CSV file upload component with file preview.

### ProgressBar
Real-time progress indicator showing crawling status.

### ResultsModal
Comprehensive results display with:
- Visual statistics cards
- File download buttons
- Extraction metadata
- Image download status
- Errors and warnings

### CrawlForm
Main form component combining all options:
- Input method (single URL or CSV bulk)
- Mode selection (content/link)
- Format selection (txt, md, html, json)
- Content scoping options
- Image download toggle
- Link filtering options

## Pages

### Home (`/`)
Landing page with features overview and call-to-action.

### Crawler (`/crawler`)
Main crawling interface with form and results display.

### History (`/history`)
View and manage past crawling jobs with filtering options.

## API Integration

The frontend communicates with the backend API at `/api`:

- `POST /api/crawl/single` - Start single URL crawl
- `POST /api/crawl/bulk` - Upload CSV for bulk crawl
- `GET /api/job/{id}/status` - Poll job status
- `GET /api/job/{id}/results` - Get job results
- `GET /api/download/{id}/{file}` - Download output file
- `GET /api/history` - Get crawl history
- `DELETE /api/job/{id}` - Delete job

## Styling

The app uses Tailwind CSS with a custom color palette:

- **Primary**: Blue tones for main actions
- **Success**: Green for successful operations
- **Warning**: Orange for warnings
- **Error**: Red for errors and failures

Custom theme configuration in `tailwind.config.js`.

## Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t web-crawler-frontend .

# Run container
docker run -p 3000:3000 web-crawler-frontend
```

Or use docker-compose from the project root:

```bash
docker-compose up frontend
```

## Development Tips

### Hot Module Replacement (HMR)
Vite provides instant HMR - changes appear immediately without full page reload.

### API Proxy
Development server proxies API requests to avoid CORS issues:

```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true,
  }
}
```

### React Query DevTools
Add React Query DevTools for debugging:

```bash
npm install @tanstack/react-query-devtools
```

### Debugging
- Use React DevTools browser extension
- Check browser console for errors
- Monitor network requests in DevTools

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Code splitting with React Router
- Lazy loading of components
- Optimized bundle size with Vite
- Image optimization
- Gzip compression in production

## Accessibility

- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Focus visible indicators
- Screen reader friendly

## Future Enhancements

- [ ] Add charts for statistics visualization with Recharts
- [ ] Implement dark mode toggle
- [ ] Add export to PDF functionality
- [ ] Implement advanced filtering in history
- [ ] Add user preferences/settings
- [ ] WebSocket for real-time updates
- [ ] Progressive Web App (PWA) support
- [ ] Internationalization (i18n)

## Troubleshooting

### Port already in use
```bash
# Change port in package.json or run with custom port
npm run dev -- --port 3001
```

### Build errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### API connection issues
- Check backend is running on port 5000
- Verify VITE_API_URL in .env file
- Check CORS settings in backend

## License

This project is part of the Web Crawler application.

## Contributing

1. Follow the existing code style
2. Write meaningful commit messages
3. Test changes thoroughly
4. Update documentation as needed
