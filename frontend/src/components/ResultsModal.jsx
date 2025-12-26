import { Fragment } from 'react';
import { FiX, FiDownload, FiFileText, FiImage, FiClock, FiCheckCircle, FiAlertTriangle, FiChevronDown, FiChevronUp, FiAlertCircle, FiRefreshCw } from 'react-icons/fi';
import { useState } from 'react';
import { crawlAPI } from '../services/api';

const ResultsModal = ({ isOpen, onClose, jobId, results }) => {
  const [expandedSections, setExpandedSections] = useState({});

  if (!isOpen) return null;

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleDownload = (filename) => {
    const url = crawlAPI.getDownloadUrl(jobId, filename);
    window.open(url, '_blank');
  };

  const handleDownloadZip = () => {
    const url = crawlAPI.getZipDownloadUrl(jobId);
    window.open(url, '_blank');
  };

  const getStatusBadge = (status) => {
    const badges = {
      success: 'bg-success-100 text-success-700',
      warning: 'bg-warning-100 text-warning-700',
      error: 'bg-error-100 text-error-700',
    };
    return badges[status] || badges.success;
  };

  // Check if it's bulk crawl (multiple results) or single crawl
  const isBulkCrawl = results && results.length > 1;

  if (!results || results.length === 0) return null;

  // For bulk crawl, show list view. For single crawl, show detailed view
  if (isBulkCrawl) {
    // Separate combined results from regular URL results
    const combinedResult = results.find(r => r.url && r.url.startsWith('📦 Combined Results'));
    const urlResults = results.filter(r => !r.url || !r.url.startsWith('📦 Combined Results'));

    const successCount = urlResults.filter(r => r.status === 'success').length;
    const failedCount = urlResults.filter(r => r.status === 'failed').length;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 p-6 text-white">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-2xl font-bold">Bulk Crawl Results</h2>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <FiX className="h-6 w-6" />
              </button>
            </div>
            <div className="flex items-center space-x-4 text-sm">
              <span className="text-primary-100">Total: {urlResults.length}</span>
              <span className="text-success-200">✓ Success: {successCount}</span>
              {failedCount > 0 && <span className="text-error-200">✗ Failed: {failedCount}</span>}
            </div>
          </div>

          {/* Content - List of Results */}
          <div className="flex-1 overflow-y-auto p-6">
            <div className="space-y-4">
              {urlResults.map((result, index) => (
                <div key={index} className={`rounded-lg border-2 p-4 ${
                  result.status === 'success' ? 'bg-success-50 border-success-200' : 'bg-error-50 border-error-200'
                }`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1 mr-4">
                      <div className="flex items-center space-x-2 mb-2">
                        {result.status === 'success' ? (
                          <FiCheckCircle className="h-5 w-5 text-success-600 flex-shrink-0" />
                        ) : (
                          <FiAlertTriangle className="h-5 w-5 text-error-600 flex-shrink-0" />
                        )}
                        <span className={`text-sm font-semibold ${
                          result.status === 'success' ? 'text-success-900' : 'text-error-900'
                        }`}>
                          URL {index + 1}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 break-all mb-2">{result.url}</p>
                      
                      {result.status === 'failed' && (
                        <p className="text-xs text-error-700 mt-1">
                          {result.failure_info?.failure_reason || result.error || 'Extraction failed'}
                        </p>
                      )}
                      
                      {result.status === 'success' && result.statistics && (
                        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-600">
                          {result.statistics.word_count && (
                            <span>📝 {result.statistics.word_count} words</span>
                          )}
                          {result.statistics.image_count > 0 && (
                            <span>
                              {result.metadata?.images?.successful > 0 ? (
                                `🖼️ ${result.metadata.images.successful}/${result.statistics.image_count} images`
                              ) : (
                                `⚠️ ${result.statistics.image_count} images (failed)`
                              )}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex flex-col space-y-2">
                      {result.status === 'success' && result.output_folder && (
                        <button
                          onClick={() => {
                            // Extract folder name from path and download as ZIP
                            const folderName = result.output_folder.split(/[/\\]/).pop();
                            window.open(`http://localhost:5000/api/download/${jobId}/${folderName}/zip`, '_blank');
                          }}
                          className="flex items-center space-x-2 px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-xs font-medium whitespace-nowrap"
                        >
                          <FiDownload className="h-4 w-4" />
                          <span>Download ZIP</span>
                        </button>
                      )}
                      
                      {result.status === 'failed' && result.debug_html_url && (
                        <div className="flex flex-col space-y-1">
                          <a
                            href={`http://localhost:5000/api/output/${result.debug_html_url}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center space-x-1 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-xs font-medium whitespace-nowrap"
                          >
                            <span>🌐</span>
                            <span>Preview</span>
                          </a>
                          <a
                            href={`http://localhost:5000/api/output/${result.debug_html_url}?raw=true`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center space-x-1 px-3 py-1.5 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-xs font-medium whitespace-nowrap"
                          >
                            <span>📄</span>
                            <span>Source</span>
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 p-4 bg-gray-50 space-y-3">
            {/* Combined Results Section */}
            {combinedResult && (
              <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border-2 border-amber-300 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0 w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                      <span className="text-2xl">📦</span>
                    </div>
                    <div>
                      <p className="text-sm font-bold text-gray-900">{combinedResult.url}</p>
                      <p className="text-xs text-gray-600">All successful results merged into one file</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      // Use the actual filename from output_files array
                      const filename = combinedResult.output_files[0];
                      if (filename) {
                        window.open(`http://localhost:5000/api/download/${jobId}/${filename}`, '_blank');
                      }
                    }}
                    className="flex items-center space-x-2 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors text-sm font-medium shadow-md hover:shadow-lg whitespace-nowrap"
                  >
                    <FiDownload className="h-4 w-4" />
                    <span>Download Combined</span>
                  </button>
                </div>
              </div>
            )}

            {/* Download All ZIP Button */}
            <button
              onClick={handleDownloadZip}
              className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              <FiDownload className="h-5 w-5" />
              <span>Download All Results (ZIP)</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Single crawl - show detailed view
  const result = results[0];
  const metadata = result.metadata || {};
  const stats = metadata.content_statistics || metadata.link_statistics || {};
  const images = metadata.images || {};
  const params = metadata.extraction_parameters || {};

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-2xl font-bold">Extraction Results</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <FiX className="h-6 w-6" />
            </button>
          </div>
          <p className="text-primary-100 text-sm truncate">{result.url}</p>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Status Banner */}
          <div className={`rounded-lg p-4 mb-6 ${
            result.status === 'success' ? 'bg-success-50 border border-success-200' :
            result.status === 'failed' ? 'bg-error-50 border border-error-200' :
            'bg-warning-50 border border-warning-200'
          }`}>
            <div className="flex items-center space-x-3">
              {result.status === 'success' ? (
                <FiCheckCircle className="h-6 w-6 text-success-600" />
              ) : (
                <FiAlertTriangle className="h-6 w-6 text-error-600" />
              )}
              <div className="flex-1">
                <p className={`font-semibold ${
                  result.status === 'success' ? 'text-success-900' : 'text-error-900'
                }`}>
                  {result.status === 'success' ? 'Extraction Successful!' : 'Extraction Failed'}
                </p>
                {result.status === 'success' && metadata.execution_time && (
                  <p className="text-sm text-success-700">
                    Completed in {metadata.execution_time.toFixed(2)}s
                  </p>
                )}
                {result.status === 'failed' && (
                  <>
                    <p className="text-sm text-error-700 mt-1 font-medium">
                      {result.failure_info?.failure_reason || result.error || 'An unknown error occurred'}
                    </p>
                    {result.failure_info?.error_type && (
                      <span className="inline-block mt-2 px-2 py-1 text-xs font-medium rounded-md bg-error-100 text-error-800">
                        {result.failure_info.error_type.replace('_', ' ').toUpperCase()}
                      </span>
                    )}
                  </>
                )}
              </div>
            </div>
            
            {/* Failure Details */}
            {result.status === 'failed' && (result.failure_info || result.error) && (
              <div className="mt-4 pt-4 border-t border-error-200">
                {/* Suggestions */}
                {result.failure_info?.suggestions && result.failure_info.suggestions.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-medium text-error-900 mb-2">Suggested Actions:</p>
                    <ul className="space-y-1">
                      {result.failure_info.suggestions.map((suggestion, idx) => (
                        <li key={idx} className="text-sm text-error-700 flex items-start">
                          <span className="mr-2">•</span>
                          <span>{suggestion}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Action Buttons */}
                <div className="flex items-center space-x-3 mt-3">
                  {(result.failure_info?.retry_possible || !result.failure_info) && (
                    <button
                      onClick={() => window.location.reload()}
                      className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
                    >
                      <FiRefreshCw className="h-4 w-4" />
                      <span>Retry Extraction</span>
                    </button>
                  )}
                  {result.debug_html_url && (
                    <>
                      <a
                        href={`http://localhost:5000/api/output/${result.debug_html_url}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                      >
                        <span>🌐</span>
                        <span>Preview Mode</span>
                      </a>
                      <a
                        href={`http://localhost:5000/api/output/${result.debug_html_url}?raw=true`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm font-medium"
                      >
                        <span>📄</span>
                        <span>HTML Source</span>
                      </a>
                    </>
                  )}
                  <button
                    onClick={() => toggleSection('troubleshooting')}
                    className="px-4 py-2 bg-white border border-error-300 text-error-700 rounded-lg hover:bg-error-50 transition-colors text-sm font-medium"
                  >
                    View Troubleshooting Tips
                  </button>
                </div>
                
                {/* Troubleshooting Section */}
                {expandedSections.troubleshooting && (
                  <div className="mt-4 p-4 bg-white rounded-lg border border-error-200">
                    <h4 className="font-semibold text-gray-900 mb-2">Troubleshooting Guide</h4>
                    <div className="space-y-2 text-sm text-gray-700">
                      <p><strong>Error Code:</strong> {result.failure_info?.error_code || 'N/A'}</p>
                      <p><strong>Error Type:</strong> {result.failure_info?.error_type || 'Unknown'}</p>
                      <p><strong>Can Retry:</strong> {result.failure_info?.retry_possible ? 'Yes - This error may be temporary' : 'No - This requires fixing the input or configuration'}</p>
                      
                      <div className="mt-3 p-3 bg-gray-50 rounded">
                        <p className="font-medium mb-1">Need More Help?</p>
                        <p className="text-xs text-gray-600">
                          Check the URL is accessible in a browser, verify your input parameters, 
                          and consult the documentation for more information.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {stats.word_count !== undefined && (
              <div className="bg-primary-50 rounded-lg p-4 border border-primary-200">
                <FiFileText className="h-8 w-8 text-primary-600 mb-2" />
                <p className="text-2xl font-bold text-gray-900">{stats.word_count?.toLocaleString() || 0}</p>
                <p className="text-sm text-gray-600">Words</p>
              </div>
            )}
            {stats.character_count !== undefined && (
              <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <FiFileText className="h-8 w-8 text-purple-600 mb-2" />
                <p className="text-2xl font-bold text-gray-900">{stats.character_count?.toLocaleString() || 0}</p>
                <p className="text-sm text-gray-600">Characters</p>
              </div>
            )}
            {stats.image_count !== undefined && (
              <div className={`rounded-lg p-4 border ${
                images.successfully_downloaded > 0
                  ? 'bg-success-50 border-success-200'
                  : images.total_found > 0
                  ? 'bg-warning-50 border-warning-200'
                  : 'bg-gray-50 border-gray-200'
              }`}>
                <FiImage className={`h-8 w-8 mb-2 ${
                  images.successfully_downloaded > 0
                    ? 'text-success-600'
                    : images.total_found > 0
                    ? 'text-warning-600'
                    : 'text-gray-400'
                }`} />
                <p className="text-2xl font-bold text-gray-900">
                  {images.successfully_downloaded || 0}
                  {images.total_found > 0 && `/${images.total_found}`}
                </p>
                <p className="text-sm text-gray-600">
                  {images.successfully_downloaded > 0 ? 'Images Downloaded' : images.total_found > 0 ? 'Images (Failed)' : 'Images'}
                </p>
              </div>
            )}
            {stats.total_links !== undefined && (
              <div className="bg-primary-50 rounded-lg p-4 border border-primary-200">
                <FiFileText className="h-8 w-8 text-primary-600 mb-2" />
                <p className="text-2xl font-bold text-gray-900">{stats.total_links || 0}</p>
                <p className="text-sm text-gray-600">Links</p>
              </div>
            )}
            {metadata.execution_time && (
              <div className="bg-warning-50 rounded-lg p-4 border border-warning-200">
                <FiClock className="h-8 w-8 text-warning-600 mb-2" />
                <p className="text-2xl font-bold text-gray-900">{metadata.execution_time.toFixed(2)}s</p>
                <p className="text-sm text-gray-600">Duration</p>
              </div>
            )}
          </div>

          {/* Download Files */}
          {result.output_files && result.output_files.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Output Files</h3>
              
              {/* Show ZIP download if images were downloaded */}
              {result.has_images ? (
                <div className="bg-gradient-to-r from-primary-50 to-primary-100 rounded-lg p-4 border-2 border-primary-300">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <FiFileText className="h-6 w-6 text-primary-600" />
                      <div>
                        <p className="text-sm font-semibold text-gray-900">All Files ({result.output_files.length})</p>
                        <p className="text-xs text-gray-600">Includes content and downloaded images</p>
                      </div>
                    </div>
                    <button
                      onClick={handleDownloadZip}
                      className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors shadow-md hover:shadow-lg"
                    >
                      <FiDownload className="h-5 w-5" />
                      <span className="font-medium">Download All (ZIP)</span>
                    </button>
                  </div>
                </div>
              ) : (
                /* Show individual file downloads if no images */
                <div className="space-y-2">
                  {result.output_files.map((file, idx) => (
                    <div key={idx} className="flex items-center justify-between bg-gray-50 rounded-lg p-3 border border-gray-200">
                      <div className="flex items-center space-x-3">
                        <FiFileText className="h-5 w-5 text-gray-400" />
                        <span className="text-sm font-medium text-gray-900">{file}</span>
                      </div>
                      <button
                        onClick={() => handleDownload(file)}
                        className="flex items-center space-x-2 px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
                      >
                        <FiDownload className="h-4 w-4" />
                        <span>Download</span>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Extraction Parameters */}
          <div className="mb-6">
            <button
              onClick={() => toggleSection('parameters')}
              className="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <h3 className="text-lg font-semibold text-gray-900">Extraction Parameters</h3>
              {expandedSections.parameters ? (
                <FiChevronUp className="h-5 w-5 text-gray-500" />
              ) : (
                <FiChevronDown className="h-5 w-5 text-gray-500" />
              )}
            </button>
            {expandedSections.parameters && (
              <div className="mt-2 bg-gray-50 rounded-lg p-4 space-y-2">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">Mode</p>
                    <p className="text-sm font-medium text-gray-900">{params.mode || 'content'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Formats</p>
                    <p className="text-sm font-medium text-gray-900">
                      {params.output_formats?.join(', ') || 'txt'}
                    </p>
                  </div>
                  {params.scope_class && (
                    <div>
                      <p className="text-xs text-gray-500">Scope Class</p>
                      <p className="text-sm font-medium text-gray-900">{params.scope_class}</p>
                    </div>
                  )}
                  {params.download_images !== undefined && (
                    <div>
                      <p className="text-xs text-gray-500">Download Images</p>
                      <p className="text-sm font-medium text-gray-900">
                        {params.download_images ? 'Yes' : 'No'}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Images Info */}
          {images.total_found > 0 && (
            <div className="mb-6">
              <button
                onClick={() => toggleSection('images')}
                className="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <h3 className="text-lg font-semibold text-gray-900">
                  Images ({images.successfully_downloaded}/{images.total_found})
                </h3>
                {expandedSections.images ? (
                  <FiChevronUp className="h-5 w-5 text-gray-500" />
                ) : (
                  <FiChevronDown className="h-5 w-5 text-gray-500" />
                )}
              </button>
              {expandedSections.images && (
                <div className="mt-2 bg-gray-50 rounded-lg p-4 max-h-60 overflow-y-auto">
                  <div className="space-y-2">
                    {images.image_list?.map((img, idx) => (
                      <div key={idx} className="flex items-center justify-between text-sm">
                        <span className="text-gray-700 truncate flex-1">{img.url}</span>
                        <span className={`ml-2 px-2 py-0.5 rounded text-xs ${
                          img.status === 'success' ? 'bg-success-100 text-success-700' : 'bg-error-100 text-error-700'
                        }`}>
                          {img.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Errors and Warnings */}
          {(result.errors?.length > 0 || metadata.warnings?.length > 0) && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Issues</h3>
              <div className="space-y-2">
                {result.errors?.map((error, idx) => (
                  <div key={idx} className="flex items-start space-x-2 bg-error-50 border border-error-200 rounded-lg p-3">
                    <FiAlertTriangle className="h-5 w-5 text-error-600 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-error-800">{error}</p>
                  </div>
                ))}
                {metadata.warnings?.map((warning, idx) => (
                  <div key={idx} className="flex items-start space-x-2 bg-warning-50 border border-warning-200 rounded-lg p-3">
                    <FiAlertTriangle className="h-5 w-5 text-warning-600 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-warning-800">{warning}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsModal;
