import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { FiHome, FiZap, FiClock, FiBookmark } from 'react-icons/fi';
import Home from './pages/Home';
import Crawler from './pages/Crawler';
import History from './pages/History';
import SavedJobs from './pages/SavedJobs';

// Custom logger that suppresses mutation errors
const queryClientLogger = {
  log: console.log,
  warn: console.warn,
  error: () => {}, // Suppress error logs
};

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
    mutations: {
      // Suppress console errors for mutations that handle their own errors
      onError: () => {},
    },
  },
  logger: queryClientLogger,
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen flex flex-col">
          {/* Navigation */}
          <nav className="bg-white shadow-md sticky top-0 z-50">
            <div className="container mx-auto px-4">
              <div className="flex items-center justify-between h-16">
                <Link to="/" className="flex items-center space-x-2 text-xl font-bold text-primary-600">
                  <FiZap className="w-6 h-6" />
                  <span>Web Crawler</span>
                </Link>
                
                <div className="flex items-center space-x-1">
                  <Link
                    to="/"
                    className="flex items-center space-x-2 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    <FiHome className="w-5 h-5" />
                    <span className="hidden sm:inline">Home</span>
                  </Link>
                  <Link
                    to="/crawler"
                    className="flex items-center space-x-2 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    <FiZap className="w-5 h-5" />
                    <span className="hidden sm:inline">Crawler</span>
                  </Link>
                  <Link
                    to="/saved-jobs"
                    className="flex items-center space-x-2 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    <FiBookmark className="w-5 h-5" />
                    <span className="hidden sm:inline">Saved Jobs</span>
                  </Link>
                  <Link
                    to="/history"
                    className="flex items-center space-x-2 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    <FiClock className="w-5 h-5" />
                    <span className="hidden sm:inline">History</span>
                  </Link>
                </div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/crawler" element={<Crawler />} />
              <Route path="/saved-jobs" element={<SavedJobs />} />
              <Route path="/history" element={<History />} />
            </Routes>
          </main>

          {/* Footer */}
          <footer className="bg-gray-900 text-gray-300 py-8">
            <div className="container mx-auto px-4 text-center">
              <p className="text-sm">
                © {new Date().getFullYear()} Web Crawler. Built with React & Tailwind CSS.
              </p>
            </div>
          </footer>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
