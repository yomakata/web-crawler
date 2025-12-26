import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUploadCloud, FiFile, FiX, FiHelpCircle } from 'react-icons/fi';

const CSVUpload = ({ file, onChange, error, mode = 'content' }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const [hideTimeout, setHideTimeout] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      onChange(acceptedFiles[0]);
    }
  }, [onChange]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.csv']
    },
    maxFiles: 1,
    multiple: false
  });

  const removeFile = (e) => {
    e.stopPropagation();
    onChange(null);
  };

  const handleMouseEnter = () => {
    if (hideTimeout) {
      clearTimeout(hideTimeout);
      setHideTimeout(null);
    }
    setShowTooltip(true);
  };

  const handleMouseLeave = () => {
    const timeout = setTimeout(() => {
      setShowTooltip(false);
    }, 200); // 200ms delay before hiding
    setHideTimeout(timeout);
  };

  return (
    <div className="mb-4">
      <div className="flex items-center mb-2 relative">
        <label className="text-sm font-semibold text-gray-700">
          Upload CSV File
        </label>
        <div
          className="relative ml-2 inline-block"
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          <FiHelpCircle className="h-4 w-4 text-gray-400 hover:text-primary-600 cursor-help transition-colors" />

          {/* Tooltip */}
          {showTooltip && (
            <div
              className="absolute left-0 top-5 z-50 w-[600px] bg-white border border-gray-200 rounded-lg shadow-xl p-4"
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
            >
              <div className="text-xs text-gray-700 space-y-3 max-h-96 overflow-y-auto select-text">
                <p className="font-semibold text-sm text-gray-900 mb-2">CSV Format Examples:</p>

                {mode === 'content' && (
                  <>
                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                      <p className="font-semibold mb-1.5 text-gray-800">Content Mode (no authentication):</p>
                      <code className="block text-xs text-gray-700 font-mono">
                        url,mode,scope_class,format,download_images<br/>
                        https://example.com,content,main-content,txt,false
                      </code>
                    </div>

                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                      <p className="font-semibold mb-1.5 text-gray-800">Content Mode with Cookies Authentication:</p>
                      <code className="block text-xs text-gray-700 font-mono">
                        url,mode,scope_class,format,download_images,auth_enabled,auth_type,cookies<br/>
                        https://example.com,content,main-content,txt,false,true,cookies,&quot;session=abc123&quot;
                      </code>
                    </div>

                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                      <p className="font-semibold mb-1.5 text-gray-800">Content Mode with Basic Auth:</p>
                      <code className="block text-xs text-gray-700 font-mono">
                        url,mode,scope_class,format,download_images,auth_enabled,auth_type,basic_auth_username,basic_auth_password<br/>
                        https://example.com,content,main-content,txt,false,true,basic,myuser,mypassword
                      </code>
                    </div>

                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                      <p className="font-semibold mb-1.5 text-gray-800">Content Mode with Auth Headers:</p>
                      <code className="block text-xs text-gray-700 font-mono">
                        url,mode,scope_class,format,download_images,auth_enabled,auth_type,auth_headers<br/>
                        {`https://example.com,content,main-content,txt,false,true,headers,"{'Authorization': 'Bearer token123'}"`}
                      </code>
                    </div>
                  </>
                )}

                {mode === 'link' && (
                  <>
                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                      <p className="font-semibold mb-1.5 text-gray-800">Link Mode (no authentication):</p>
                      <code className="block text-xs text-gray-700 font-mono">
                        url,mode,scope_class,format<br/>
                        https://example.com,link,main-content,txt
                      </code>
                    </div>

                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                      <p className="font-semibold mb-1.5 text-gray-800">Link Mode with Cookies Authentication:</p>
                      <code className="block text-xs text-gray-700 font-mono">
                        url,mode,scope_class,format,auth_enabled,auth_type,cookies<br/>
                        https://example.com,link,main-content,txt,true,cookies,&quot;session=abc123&quot;
                      </code>
                    </div>

                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                      <p className="font-semibold mb-1.5 text-gray-800">Link Mode with Basic Auth:</p>
                      <code className="block text-xs text-gray-700 font-mono">
                        url,mode,scope_class,format,auth_enabled,auth_type,basic_auth_username,basic_auth_password<br/>
                        https://example.com,link,main-content,txt,true,basic,myuser,mypassword
                      </code>
                    </div>

                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                      <p className="font-semibold mb-1.5 text-gray-800">Link Mode with Auth Headers:</p>
                      <code className="block text-xs text-gray-700 font-mono">
                        url,mode,scope_class,format,auth_enabled,auth_type,auth_headers<br/>
                        {`https://example.com,link,main-content,txt,true,headers,"{'Authorization': 'Bearer token123'}"`}
                      </code>
                    </div>
                  </>
                )}

                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
                  <p className="text-xs text-blue-800">
                    <strong>💡 Tip:</strong> You can use global authentication below to apply the same credentials to all URLs,
                    or include authentication columns in your CSV for per-URL authentication.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {!file ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : error
              ? 'border-error-500 bg-error-50'
              : 'border-gray-300 bg-gray-50 hover:border-primary-400 hover:bg-primary-50'
          }`}
        >
          <input {...getInputProps()} />
          <FiUploadCloud className="mx-auto h-12 w-12 text-gray-400 mb-3" />
          {isDragActive ? (
            <p className="text-sm text-primary-600 font-medium">Drop the CSV file here...</p>
          ) : (
            <>
              <p className="text-sm text-gray-600 mb-1">
                <span className="font-semibold text-primary-600">Click to upload</span> or drag and drop
              </p>
              <p className="text-xs text-gray-500">CSV file with URL column (max 10MB)</p>
            </>
          )}
        </div>
      ) : (
        <div className="border-2 border-primary-500 bg-primary-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FiFile className="h-8 w-8 text-primary-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">{file.name}</p>
                <p className="text-xs text-gray-500">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={removeFile}
              className="p-2 text-gray-400 hover:text-error-600 transition-colors"
            >
              <FiX className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}
      
      {error && (
        <p className="mt-2 text-sm text-error-600">{error}</p>
      )}
    </div>
  );
};

export default CSVUpload;
