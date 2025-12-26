import { FiLoader } from 'react-icons/fi';

const ProgressBar = ({ progress, status, message, currentUrl }) => {
  // Debug log
  console.log('ProgressBar props:', { progress, status, message, currentUrl });
  
  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-success-500';
      case 'failed':
        return 'bg-error-500';
      case 'running':
        return 'bg-primary-500';
      default:
        return 'bg-gray-300';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'running':
        return 'In Progress';
      default:
        return 'Pending';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          {status === 'running' && (
            <FiLoader className="h-5 w-5 text-primary-500 animate-spin" />
          )}
          <h3 className="text-lg font-semibold text-gray-900">Crawling Status</h3>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
          status === 'completed' ? 'bg-success-100 text-success-700' :
          status === 'failed' ? 'bg-error-100 text-error-700' :
          status === 'running' ? 'bg-primary-100 text-primary-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {getStatusText()}
        </span>
      </div>

      <div className="mb-3">
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${getStatusColor()}`}
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm mb-2">
        <span className="text-gray-600">{message || 'Preparing to crawl...'}</span>
        <span className="font-semibold text-gray-900">{progress}%</span>
      </div>

      {/* Display current URL being processed */}
      {currentUrl && status === 'running' && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="flex items-start space-x-2">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider flex-shrink-0 mt-0.5">
              Processing:
            </span>
            <span className="text-sm text-primary-600 break-all font-mono">
              {currentUrl}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
