import { useState, useEffect } from 'react';
import { useQuery, useMutation } from 'react-query';
import { useLocation } from 'react-router-dom';
import CrawlForm from '../components/CrawlForm';
import ProgressBar from '../components/ProgressBar';
import ResultsModal from '../components/ResultsModal';
import PreviewModal from '../components/PreviewModal';
import { crawlAPI } from '../services/api';

const Crawler = () => {
  const location = useLocation();
  const [isLoading, setIsLoading] = useState(false);
  const [currentJobId, setCurrentJobId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('pending');
  const [statusMessage, setStatusMessage] = useState('');
  const [currentUrl, setCurrentUrl] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [results, setResults] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [pendingFormData, setPendingFormData] = useState(null);
  const [savedJobData, setSavedJobData] = useState(null);
  const [errorAlert, setErrorAlert] = useState(null);

  // Load saved job from navigation state
  useEffect(() => {
    if (location.state?.savedJob) {
      setSavedJobData(location.state.savedJob);
    }
  }, [location.state]);

  // Poll job status
  useQuery(
    ['jobStatus', currentJobId],
    () => crawlAPI.getJobStatus(currentJobId),
    {
      enabled: !!currentJobId && status === 'running',
      refetchInterval: 1000, // Poll every second
      onSuccess: (data) => {
        console.log('Job status received:', data);  // Debug log
        setStatus(data.status);
        setProgress(data.progress || 0);
        setStatusMessage(data.message || '');
        setCurrentUrl(data.current_url || null);
        console.log('Current URL set to:', data.current_url);  // Debug log

        if (data.status === 'completed' || data.status === 'failed') {
          // Fetch full results
          crawlAPI.getJobResults(currentJobId)
            .then((resultsData) => {
              setResults(resultsData);
              setIsLoading(false);
              setShowResults(true);
            })
            .catch((error) => {
              console.error('Error fetching results:', error);
              setIsLoading(false);
            });
        }
      },
    }
  );

  const handleSubmit = async (formData) => {
    setIsLoading(true);
    setProgress(0);
    setStatus('running');
    setStatusMessage('Starting crawl...');
    setCurrentUrl(null);  // Clear previous URL
    setShowResults(false);
    setErrorAlert(null);  // Clear previous errors

    try {
      let response;

      if (formData.inputMethod === 'single') {
        const requestData = {
          url: formData.url,
          mode: formData.mode,
          formats: formData.formats,
          scope_class: formData.scopeClass,
          scope_id: formData.scopeId,
          download_images: formData.downloadImages,
          link_type: formData.linkType,
          cookies: formData.cookies,
          auth_headers: formData.auth_headers,
          basic_auth_username: formData.basic_auth_username,
          basic_auth_password: formData.basic_auth_password,
        };
        response = await crawlAPI.crawlSingle(requestData);
      } else {
        // Prepare bulk authentication data
        let authData = null;
        if (formData.bulkGlobalAuth) {
          authData = {
            global_auth_enabled: true,
            auth_method: formData.authMethod,
            cookies: formData.cookies,
            auth_headers: formData.auth_headers,
            basic_auth_username: formData.basic_auth_username,
            basic_auth_password: formData.basic_auth_password,
          };
        }
        response = await crawlAPI.crawlBulk(formData.file, authData, formData.combineResults);
      }

      setCurrentJobId(response.job_id);
    } catch (error) {
      console.error('Error starting crawl:', error);
      setIsLoading(false);
      setStatus('failed');

      const errorMessage = error.response?.data?.error || 'Failed to start crawl';
      setStatusMessage(errorMessage);

      // Set error alert with detailed information
      setErrorAlert({
        message: errorMessage,
        details: error.response?.data?.details || null,
        type: 'error'
      });
    }
  };

  const handlePreview = async (formData) => {
    setIsLoading(true);
    setPendingFormData(formData);

    try {
      const previewRequest = {
        url: formData.url,
        scope_class: formData.scope_class,
        scope_id: formData.scope_id,
        cookies: formData.cookies,
        auth_headers: formData.auth_headers,
        basic_auth_username: formData.basic_auth_username,
        basic_auth_password: formData.basic_auth_password,
      };
      
      const preview = await crawlAPI.previewPage(previewRequest);
      setPreviewData(preview);
      setShowPreview(true);
      setIsLoading(false);
    } catch (error) {
      console.error('Error previewing page:', error);
      setPreviewData({
        success: false,
        error: error.response?.data?.error || 'Failed to load preview'
      });
      setShowPreview(true);
      setIsLoading(false);
    }
  };

  const handleContinueFromPreview = () => {
    setShowPreview(false);
    if (pendingFormData) {
      handleSubmit(pendingFormData);
    }
  };

  const handleCloseResults = () => {
    setShowResults(false);
    setCurrentJobId(null);
    setStatus('pending');
    setProgress(0);
    setStatusMessage('');
    setCurrentUrl(null);
    setErrorAlert(null);
  };

  // Save job configuration
  const saveJobMutation = useMutation(
    (jobData) => {
      console.log('saveJobMutation called with:', jobData);
      return crawlAPI.savedJobs.create(jobData);
    },
    {
      onSuccess: (response) => {
        console.log('Save job success:', response);
        // Modal handles user feedback, no need for alert
      },
      onError: (error) => {
        // Only log and alert for non-duplicate errors (duplicate is expected and handled by modal)
        if (error.response?.data?.error !== 'duplicate_name') {
          console.error('Save job error:', error);
          alert('Failed to save job: ' + (error.response?.data?.error || error.message));
        }
      },
    }
  );

  const handleSaveJob = async (jobData) => {
    console.log('handleSaveJob called in Crawler.jsx with:', jobData);
    try {
      const result = await saveJobMutation.mutateAsync(jobData);
      console.log('Save job completed:', result);
      return result;
    } catch (error) {
      // Only log non-duplicate errors (duplicate is expected and handled by modal)
      if (error.response?.data?.error !== 'duplicate_name') {
        console.error('Save job exception:', error);
      }
      // Re-throw to let modal handle it
      throw error;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Web Crawler</h1>
          <p className="text-gray-600">Extract content or links from any webpage</p>
        </div>

        {/* Crawl Form */}
        <div className="mb-8">
          <CrawlForm
            onSubmit={handleSubmit}
            onPreview={handlePreview}
            onSaveJob={handleSaveJob}
            isLoading={isLoading}
            savedJob={savedJobData}
          />
        </div>

        {/* Error Alert */}
        {errorAlert && (
          <div className="mb-8 bg-red-50 border-l-4 border-red-500 rounded-lg p-6 shadow-md animate-fade-in">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div className="ml-4 flex-1">
                <h3 className="text-lg font-semibold text-red-800 mb-2">
                  Cannot Start Crawl
                </h3>
                <p className="text-red-700 mb-3">
                  {errorAlert.message}
                </p>
                {errorAlert.message.includes('Too many URLs') && (
                  <div className="bg-red-100 rounded-lg p-4 mb-3">
                    <p className="text-sm text-red-800 font-medium mb-2">
                      💡 How to fix this:
                    </p>
                    <ul className="text-sm text-red-700 space-y-1 list-disc list-inside">
                      <li>Reduce the number of URLs in your CSV file</li>
                      <li>Or ask your administrator to increase the MAX_URLS_PER_CSV limit in the .env file</li>
                    </ul>
                  </div>
                )}
                {errorAlert.message.includes('File must be a CSV') && (
                  <div className="bg-red-100 rounded-lg p-4 mb-3">
                    <p className="text-sm text-red-800 font-medium mb-2">
                      💡 How to fix this:
                    </p>
                    <p className="text-sm text-red-700">
                      Please upload a valid CSV file with .csv extension
                    </p>
                  </div>
                )}
                {errorAlert.message.includes('empty') && (
                  <div className="bg-red-100 rounded-lg p-4 mb-3">
                    <p className="text-sm text-red-800 font-medium mb-2">
                      💡 How to fix this:
                    </p>
                    <p className="text-sm text-red-700">
                      Make sure your CSV file contains at least one URL
                    </p>
                  </div>
                )}
                <button
                  onClick={() => setErrorAlert(null)}
                  className="inline-flex items-center px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Progress Bar */}
        {(isLoading || status === 'running' || status === 'completed') && (
          <div className="mb-8">
            <ProgressBar
              progress={progress}
              status={status}
              message={statusMessage}
              currentUrl={currentUrl}
            />
          </div>
        )}

        {/* Preview Modal */}
        {showPreview && (
          <PreviewModal
            preview={previewData}
            onClose={() => setShowPreview(false)}
            onContinue={handleContinueFromPreview}
          />
        )}

        {/* Results Modal */}
        <ResultsModal
          isOpen={showResults}
          onClose={handleCloseResults}
          jobId={currentJobId}
          results={results?.results}
        />
      </div>
    </div>
  );
};

export default Crawler;
