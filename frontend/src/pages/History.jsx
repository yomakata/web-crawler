import { useState } from 'react';
import { useQuery } from 'react-query';
import { FiTrash2, FiClock, FiCheckCircle, FiXCircle, FiExternalLink, FiAlertCircle } from 'react-icons/fi';
import { crawlAPI } from '../services/api';
import ResultsModal from '../components/ResultsModal';

const History = () => {
  const [selectedJob, setSelectedJob] = useState(null);
  const [showResults, setShowResults] = useState(false);

  const { data: history, isLoading, refetch } = useQuery(
    'history',
    () => crawlAPI.getHistory(),
    {
      refetchInterval: 5000, // Refresh every 5 seconds
    }
  );

  const handleViewResults = async (jobId) => {
    try {
      const results = await crawlAPI.getJobResults(jobId);
      setSelectedJob({ jobId, results: results.results });
      setShowResults(true);
    } catch (error) {
      console.error('Error fetching results:', error);
    }
  };

  const handleDeleteJob = async (jobId) => {
    if (!window.confirm('Are you sure you want to delete this job and its outputs?')) {
      return;
    }

    try {
      await crawlAPI.deleteJob(jobId);
      refetch();
    } catch (error) {
      console.error('Error deleting job:', error);
      alert('Failed to delete job');
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      completed: { bg: 'bg-success-100', text: 'text-success-700', icon: FiCheckCircle },
      failed: { bg: 'bg-error-100', text: 'text-error-700', icon: FiXCircle },
      running: { bg: 'bg-primary-100', text: 'text-primary-700', icon: FiClock },
    };
    const badge = badges[status] || badges.running;
    const Icon = badge.icon;

    return (
      <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium ${badge.bg} ${badge.text}`}>
        <Icon className="w-4 h-4" />
        <span className="capitalize">{status}</span>
      </span>
    );
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading history...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Crawl History</h1>
          <p className="text-gray-600">View and manage your past crawling jobs</p>
        </div>

        {/* History List */}
        {!history || history.length === 0 ? (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <FiClock className="mx-auto h-16 w-16 text-gray-300 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No History Yet</h3>
            <p className="text-gray-600">Your crawling history will appear here</p>
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((job) => (
              <div key={job.job_id} className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow p-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                  <div className="flex-1 mb-4 md:mb-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {job.job_id.substring(0, 8)}...
                      </h3>
                      {getStatusBadge(job.status)}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-sm text-gray-600">
                      <div>
                        <span className="font-medium">Type:</span>{' '}
                        {job.crawl_type === 'bulk' ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                            Bulk
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                            Single
                          </span>
                        )}
                      </div>
                      <div>
                        <span className="font-medium">Mode:</span>{' '}
                        <span className="capitalize">{job.mode || 'content'}</span>
                      </div>
                      <div>
                        <span className="font-medium">URLs:</span> {job.urls_count || 1}
                      </div>
                      <div>
                        <span className="font-medium">Time:</span> {formatDate(job.timestamp)}
                      </div>
                    </div>
                    
                    {/* CSV Filename for Bulk Crawls */}
                    {job.crawl_type === 'bulk' && job.csv_filename && (
                      <div className="mt-2 text-sm text-gray-600">
                        <span className="font-medium">CSV File:</span>{' '}
                        <span className="text-gray-800">{job.csv_filename}</span>
                      </div>
                    )}
                    
                    {/* Failure Reason Display */}
                    {job.status === 'failed' && job.failure_reason && (
                      <div className="mt-3 p-3 bg-error-50 border border-error-200 rounded-lg">
                        <div className="flex items-start space-x-2">
                          <FiAlertCircle className="w-4 h-4 text-error-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1">
                            <p className="text-sm font-medium text-error-900">Extraction Failed</p>
                            <p className="text-xs text-error-700 mt-1">{job.failure_reason}</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    {job.status === 'completed' && (
                      <button
                        onClick={() => handleViewResults(job.job_id)}
                        className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium cursor-pointer"
                      >
                        <FiExternalLink className="w-4 h-4" />
                        <span>View Results</span>
                      </button>
                    )}
                    <button
                      onClick={() => handleDeleteJob(job.job_id)}
                      className="p-2 text-gray-400 hover:text-error-600 transition-colors cursor-pointer"
                      title="Delete job"
                    >
                      <FiTrash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Results Modal */}
        {showResults && selectedJob && (
          <ResultsModal
            isOpen={showResults}
            onClose={() => {
              setShowResults(false);
              setSelectedJob(null);
            }}
            jobId={selectedJob.jobId}
            results={selectedJob.results}
          />
        )}
      </div>
    </div>
  );
};

export default History;
