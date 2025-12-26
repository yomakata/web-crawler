import { Link } from 'react-router-dom';
import { FiGlobe, FiLink, FiCheckCircle, FiSave, FiAlertCircle, FiClock, FiArrowRight, FiFolder, FiActivity, FiPlay } from 'react-icons/fi';
import { useQuery } from 'react-query';
import crawlAPI from '../services/api';

const Home = () => {
  // Fetch recent history
  const { data: recentHistory = [] } = useQuery(
    'recentHistory',
    () => crawlAPI.getHistory(),
    {
      select: (data) => data.slice(0, 8) // Take first 8 items
    }
  );

  // Fetch saved jobs
  const { data: savedJobs = [] } = useQuery(
    'recentSavedJobs',
    () => crawlAPI.getSavedJobs(),
    {
      select: (data) => data.slice(0, 6) // Take first 6 items
    }
  );

  // Calculate statistics
  const allHistory = useQuery('allHistory', () => crawlAPI.getHistory());
  const stats = {
    total: allHistory.data?.length || 0,
    completed: allHistory.data?.filter(j => j.status === 'completed').length || 0,
    failed: allHistory.data?.filter(j => j.status === 'failed').length || 0,
    savedJobs: savedJobs.length
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-success-100 text-success-700';
      case 'failed': return 'bg-error-100 text-error-700';
      case 'running': return 'bg-warning-100 text-warning-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Bar */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-600 text-white rounded-lg flex items-center justify-center">
                <FiGlobe className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-sm text-gray-500">Web Content Extraction Platform</p>
              </div>
            </div>
            <Link
              to="/crawler"
              className="inline-flex items-center space-x-2 bg-primary-600 text-white px-6 py-2.5 rounded-lg hover:bg-primary-700 transition-all shadow-sm"
            >
              <FiPlay className="w-4 h-4" />
              <span className="font-medium">New Extraction</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Extractions</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
              </div>
              <div className="w-12 h-12 bg-primary-100 text-primary-600 rounded-lg flex items-center justify-center">
                <FiActivity className="w-6 h-6" />
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-4">All time</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Successful</p>
                <p className="text-3xl font-bold text-success-600 mt-2">{stats.completed}</p>
              </div>
              <div className="w-12 h-12 bg-success-100 text-success-600 rounded-lg flex items-center justify-center">
                <FiCheckCircle className="w-6 h-6" />
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-4">
              {stats.total > 0 ? `${Math.round((stats.completed / stats.total) * 100)}% success rate` : 'No data'}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Failed</p>
                <p className="text-3xl font-bold text-error-600 mt-2">{stats.failed}</p>
              </div>
              <div className="w-12 h-12 bg-error-100 text-error-600 rounded-lg flex items-center justify-center">
                <FiAlertCircle className="w-6 h-6" />
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-4">Needs attention</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Saved Jobs</p>
                <p className="text-3xl font-bold text-indigo-600 mt-2">{stats.savedJobs}</p>
              </div>
              <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center">
                <FiSave className="w-6 h-6" />
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-4">Ready to use</p>
          </div>
        </div>

        {/* Top Row - History and Saved Jobs side by side */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* History */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FiClock className="w-5 h-5 text-gray-500" />
                <h2 className="text-lg font-bold text-gray-900">History</h2>
              </div>
              <Link
                to="/history"
                className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center space-x-1"
              >
                <span>View All</span>
                <FiArrowRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="divide-y divide-gray-100">
              {recentHistory.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <FiActivity className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p className="text-sm">No history yet</p>
                  <Link to="/crawler" className="text-sm text-primary-600 hover:text-primary-700 font-medium mt-2 inline-block">
                    Start your first extraction
                  </Link>
                </div>
              ) : (
                recentHistory.map((job) => (
                  <div key={job.job_id} className="px-6 py-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(job.status)}`}>
                            {job.status}
                          </span>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(job.timestamp)}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm">
                          {job.mode === 'content' ? (
                            <FiGlobe className="w-4 h-4 text-gray-400" />
                          ) : (
                            <FiLink className="w-4 h-4 text-gray-400" />
                          )}
                          <span className="text-gray-900 font-medium">
                            {job.mode === 'content' ? 'Content Extraction' : 'Link Extraction'}
                          </span>
                          <span className="text-gray-500">•</span>
                          <span className="text-gray-600">
                            {job.urls_count} URL{job.urls_count > 1 ? 's' : ''}
                          </span>
                        </div>
                        {job.failure_reason && (
                          <p className="text-xs text-error-600 mt-2 flex items-center space-x-1">
                            <FiAlertCircle className="w-3 h-3" />
                            <span className="truncate">{job.failure_reason}</span>
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Saved Jobs */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FiFolder className="w-5 h-5 text-gray-500" />
                <h2 className="text-lg font-bold text-gray-900">Saved Jobs</h2>
              </div>
              <Link
                to="/saved-jobs"
                className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center space-x-1"
              >
                <span>Manage</span>
                <FiArrowRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="divide-y divide-gray-100">
              {savedJobs.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <FiSave className="w-10 h-10 mx-auto mb-2 text-gray-300" />
                  <p className="text-xs">No saved jobs</p>
                  <Link to="/crawler" className="text-xs text-primary-600 hover:text-primary-700 font-medium mt-1 inline-block">
                    Create one
                  </Link>
                </div>
              ) : (
                savedJobs.map((job) => (
                  <div
                    key={job.id}
                    className="px-6 py-3"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-indigo-100 text-indigo-600 rounded flex items-center justify-center flex-shrink-0 mt-0.5">
                        <FiFolder className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-semibold text-gray-900 truncate">{job.name}</h4>
                        <p className="text-xs text-gray-600 mt-0.5">
                          {job.mode === 'content' ? 'Content' : 'Links'}
                          {job.urls?.length > 0 && ` • ${job.urls.length} URL${job.urls.length > 1 ? 's' : ''}`}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;

