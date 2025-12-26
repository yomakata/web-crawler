import { FiX, FiCheckCircle, FiAlertTriangle, FiInfo } from 'react-icons/fi';

const PreviewModal = ({ preview, onClose, onContinue }) => {
  if (!preview) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold">Page Preview</h2>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 transition-colors"
          >
            <FiX className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Success/Error Status */}
          <div className={`flex items-start space-x-3 p-4 rounded-lg ${
            preview.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            {preview.success ? (
              <>
                <FiCheckCircle className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-semibold text-green-800">Page loaded successfully!</p>
                  <p className="text-sm text-green-700 mt-1">Authentication worked and page is accessible</p>
                </div>
              </>
            ) : (
              <>
                <FiAlertTriangle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-semibold text-red-800">Failed to load page</p>
                  <p className="text-sm text-red-700 mt-1">{preview.error}</p>
                </div>
              </>
            )}
          </div>

          {preview.success && (
            <>
              {/* Page Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
                  <FiInfo className="h-5 w-5 mr-2" />
                  Page Information
                </h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-blue-700 font-medium">Title:</span>
                    <p className="text-gray-800 mt-1">{preview.title}</p>
                  </div>
                  <div>
                    <span className="text-blue-700 font-medium">URL:</span>
                    <p className="text-gray-600 mt-1 text-xs break-all">{preview.url}</p>
                  </div>
                  <div>
                    <span className="text-blue-700 font-medium">Content Size:</span>
                    <p className="text-gray-800 mt-1">{(preview.statistics?.content_length / 1024).toFixed(2)} KB</p>
                  </div>
                  <div>
                    <span className="text-blue-700 font-medium">Text Length:</span>
                    <p className="text-gray-800 mt-1">{preview.statistics?.text_length?.toLocaleString()} characters</p>
                  </div>
                </div>
              </div>

              {/* Scope Element Check */}
              {preview.has_scope_element !== undefined && (
                <div className={`border rounded-lg p-4 ${
                  preview.has_scope_element 
                    ? 'bg-green-50 border-green-200' 
                    : 'bg-yellow-50 border-yellow-200'
                }`}>
                  <h3 className={`font-semibold mb-2 flex items-center ${
                    preview.has_scope_element ? 'text-green-900' : 'text-yellow-900'
                  }`}>
                    {preview.has_scope_element ? (
                      <>
                        <FiCheckCircle className="h-5 w-5 mr-2" />
                        Scoped Element Found ✓
                      </>
                    ) : (
                      <>
                        <FiAlertTriangle className="h-5 w-5 mr-2" />
                        Scoped Element NOT Found
                      </>
                    )}
                  </h3>
                  
                  {preview.has_scope_element ? (
                    <div className="space-y-2">
                      {preview.scope_element_info && (
                        <div className="text-sm text-green-700">
                          <p><strong>Tag:</strong> &lt;{preview.scope_element_info.tag}&gt;</p>
                          <p><strong>Text Length:</strong> {preview.scope_element_info.text_length} characters</p>
                        </div>
                      )}
                      <div className="mt-3">
                        <p className="text-sm font-medium text-green-800 mb-2">Content Preview:</p>
                        <textarea
                          readOnly
                          value={preview.scope_element_preview}
                          className="w-full bg-white border border-green-300 rounded p-3 text-sm text-gray-700 font-mono whitespace-pre-wrap resize-y min-h-[160px] max-h-[400px] focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm text-yellow-800">
                      <p className="mb-2">The specified class/ID was not found on this page.</p>
                      <p className="font-medium">Available classes (top 20):</p>
                      <div className="bg-white border border-yellow-300 rounded p-2 mt-2 max-h-32 overflow-y-auto">
                        <div className="flex flex-wrap gap-1">
                          {preview.available_classes?.slice(0, 20).map((cls, idx) => (
                            <span key={idx} className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                              {cls}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Page Statistics */}
              {preview.statistics && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-3">Page Statistics</h3>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-primary-600">{preview.statistics.total_links}</p>
                      <p className="text-gray-600">Links</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-primary-600">{preview.statistics.total_images}</p>
                      <p className="text-gray-600">Images</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-primary-600">{preview.statistics.total_paragraphs}</p>
                      <p className="text-gray-600">Paragraphs</p>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 flex justify-end space-x-3 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors font-medium"
          >
            Close
          </button>
          {preview.success && (
            <button
              onClick={onContinue}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center space-x-2"
            >
              <span>Continue with Extraction</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default PreviewModal;
