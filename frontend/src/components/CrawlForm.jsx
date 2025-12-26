import { useState, useEffect } from 'react';
import { FiPlay, FiLoader, FiLock, FiChevronDown, FiChevronUp, FiEye, FiSave } from 'react-icons/fi';
import ModeSelector from './ModeSelector';
import URLInput from './URLInput';
import CSVUpload from './CSVUpload';
import SaveJobModal from './SaveJobModal';

const CrawlForm = ({ onSubmit, onPreview, isLoading, savedJob, onSaveJob }) => {
  const [inputMethod, setInputMethod] = useState('single'); // 'single' or 'bulk'
  const [mode, setMode] = useState('content');
  const [url, setUrl] = useState('');
  const [csvFile, setCsvFile] = useState(null);
  const [formats, setFormats] = useState(['txt']);
  const [scopeClass, setScopeClass] = useState('');
  const [scopeId, setScopeId] = useState('');
  const [downloadImages, setDownloadImages] = useState(false);
  const [linkType, setLinkType] = useState('all');
  const [errors, setErrors] = useState({});
  
  // Authentication state
  const [showAuth, setShowAuth] = useState(false);
  const [authMethod, setAuthMethod] = useState('cookies'); // 'cookies', 'headers', or 'basic'
  const [cookies, setCookies] = useState('');
  const [authHeaders, setAuthHeaders] = useState('');
  const [basicAuthUsername, setBasicAuthUsername] = useState('');
  const [basicAuthPassword, setBasicAuthPassword] = useState('');
  
  // Bulk CSV global authentication state
  const [bulkGlobalAuth, setBulkGlobalAuth] = useState(false);

  // Bulk CSV combine results state
  const [combineResults, setCombineResults] = useState(false);

  // Save job modal state
  const [showSaveModal, setShowSaveModal] = useState(false);
  
  // Store loaded job name and description for default values
  const [loadedJobName, setLoadedJobName] = useState('');
  const [loadedJobDescription, setLoadedJobDescription] = useState('');

  // Load saved job data when provided
  useEffect(() => {
    if (savedJob) {
      setInputMethod(savedJob.input_method || 'single');
      setMode(savedJob.mode || 'content');
      setUrl(savedJob.url || '');
      setFormats(savedJob.formats || ['txt']);
      setScopeClass(savedJob.scope_class || '');
      setScopeId(savedJob.scope_id || '');
      setDownloadImages(savedJob.download_images || false);
      setLinkType(savedJob.link_type || 'all');
      setCombineResults(savedJob.combine_results || false);
      
      // Store loaded job name and description for save modal
      setLoadedJobName(savedJob.name || '');
      setLoadedJobDescription(savedJob.description || '');
      
      // Restore CSV file from saved content
      if (savedJob.input_method === 'bulk' && savedJob.csv_content && savedJob.csv_filename) {
        try {
          // Create a File object from the CSV content
          const blob = new Blob([savedJob.csv_content], { type: 'text/csv' });
          const file = new File([blob], savedJob.csv_filename, { type: 'text/csv' });
          setCsvFile(file);
        } catch (error) {
          console.error('Error restoring CSV file:', error);
        }
      }
      
      // Load auth settings
      if (savedJob.auth_method) {
        // Set authentication for single URL mode
        if (savedJob.input_method === 'single') {
          setShowAuth(true);
        }
        // Set authentication for bulk CSV mode
        if (savedJob.input_method === 'bulk') {
          setBulkGlobalAuth(true);
        }
        setAuthMethod(savedJob.auth_method);
        setCookies(savedJob.cookies || '');
        setAuthHeaders(savedJob.auth_headers || '');
        setBasicAuthUsername(savedJob.basic_auth_username || '');
        setBasicAuthPassword(savedJob.basic_auth_password || '');
      } else {
        // Reset auth states if no auth method saved
        setShowAuth(false);
        setBulkGlobalAuth(false);
      }
    }
  }, [savedJob]);

  // Parse cookies from Chrome DevTools format to JSON object
  const parseCookieString = (cookieStr) => {
    // Sanitize input: remove "cookie:" prefix, newlines, carriage returns
    let trimmed = cookieStr.trim()
      .replace(/^cookie[:\s]+/i, '')  // Remove "cookie:" or "Cookie:" prefix
      .replace(/\n/g, '; ')           // Replace newlines with semicolons
      .replace(/\r/g, '')             // Remove carriage returns
      .trim();
    
    // If it's already valid JSON, return parsed JSON
    if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
      try {
        return JSON.parse(trimmed);
      } catch (e) {
        throw new Error('Invalid JSON format');
      }
    }
    
    // Parse Chrome DevTools cookie format: "key1=value1; key2=value2; key3=value3"
    const cookieObj = {};
    const pairs = trimmed.split(';');
    
    for (const pair of pairs) {
      const trimmedPair = pair.trim();
      if (!trimmedPair) continue;
      
      const firstEquals = trimmedPair.indexOf('=');
      if (firstEquals === -1) continue;
      
      const key = trimmedPair.substring(0, firstEquals).trim();
      const value = trimmedPair.substring(firstEquals + 1).trim();
      
      if (key) {
        cookieObj[key] = value;
      }
    }
    
    if (Object.keys(cookieObj).length === 0) {
      throw new Error('No valid cookies found');
    }
    
    return cookieObj;
  };

  const validateForm = () => {
    const newErrors = {};

    if (inputMethod === 'single') {
      if (!url) {
        newErrors.url = 'URL is required';
      } else if (!/^https?:\/\/.+/.test(url)) {
        newErrors.url = 'Please enter a valid URL starting with http:// or https://';
      }
    } else {
      if (!csvFile) {
        newErrors.csv = 'Please upload a CSV file';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const buildRequestData = () => {
    const data = {
      inputMethod,
      mode,
      formats,
      scopeClass: scopeClass || null,
      scopeId: scopeId || null,
      downloadImages: mode === 'content' ? downloadImages : false,
      linkType: mode === 'link' ? linkType : 'all',
    };
    
    // Add bulk-specific options
    if (inputMethod === 'bulk') {
      data.combineResults = combineResults;
      data.bulkGlobalAuth = bulkGlobalAuth;
      if (bulkGlobalAuth) {
        data.authMethod = authMethod;
      }
    }
    
    // Add authentication based on selected method
    if ((inputMethod === 'single' && authMethod === 'cookies' && cookies.trim()) ||
        (inputMethod === 'bulk' && bulkGlobalAuth && authMethod === 'cookies' && cookies.trim())) {
      try {
        data.cookies = parseCookieString(cookies);
      } catch (e) {
        setErrors({ ...errors, cookies: `Invalid cookie format: ${e.message}` });
        return;
      }
    }
    
    if ((inputMethod === 'single' && authMethod === 'headers' && authHeaders.trim()) ||
        (inputMethod === 'bulk' && bulkGlobalAuth && authMethod === 'headers' && authHeaders.trim())) {
      try {
        data.auth_headers = JSON.parse(authHeaders);
      } catch (e) {
        setErrors({ ...errors, authHeaders: 'Invalid JSON format for headers' });
        return;
      }
    }
    
    if ((inputMethod === 'single' && authMethod === 'basic' && basicAuthUsername.trim()) ||
        (inputMethod === 'bulk' && bulkGlobalAuth && authMethod === 'basic' && basicAuthUsername.trim())) {
      data.basic_auth_username = basicAuthUsername;
      data.basic_auth_password = basicAuthPassword;
    }

    return data;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    const data = buildRequestData();
    if (!data) return;

    if (inputMethod === 'single') {
      data.url = url;
      onSubmit(data);
    } else {
      data.file = csvFile;
      onSubmit(data);
    }
  };

  const handlePreview = (e) => {
    e.preventDefault();
    
    if (!url) {
      setErrors({ url: 'URL is required for preview' });
      return;
    }
    
    if (!/^https?:\/\/.+/.test(url)) {
      setErrors({ url: 'Please enter a valid URL starting with http:// or https://' });
      return;
    }

    const data = buildRequestData();
    if (!data) return;

    data.url = url;
    data.scope_class = scopeClass || null;
    data.scope_id = scopeId || null;
    
    onPreview(data);
  };

  const handleSaveJob = async (jobInfo) => {
    console.log('=== handleSaveJob called ===');
    console.log('jobInfo from modal:', jobInfo);
    console.log('Form state:', {
      inputMethod,
      mode,
      url,
      csvFile: csvFile?.name,
      formats,
      scopeClass,
      scopeId,
      downloadImages,
      linkType,
      showAuth,
      bulkGlobalAuth,
      authMethod,
      cookies: cookies?.substring(0, 50),
      authHeaders: authHeaders?.substring(0, 50),
      basicAuthUsername
    });

    // Read CSV file content if in bulk mode
    let csvContent = null;
    if (inputMethod === 'bulk' && csvFile) {
      try {
        csvContent = await csvFile.text();
      } catch (error) {
        console.error('Error reading CSV file:', error);
      }
    }

    // Determine if authentication should be saved
    const hasAuth = (inputMethod === 'single' && showAuth) || (inputMethod === 'bulk' && bulkGlobalAuth);

    const jobData = {
      ...jobInfo,
      input_method: inputMethod,
      mode,
      url: inputMethod === 'single' ? url : null,
      csv_filename: inputMethod === 'bulk' && csvFile ? csvFile.name : null,
      csv_content: csvContent,
      formats,
      scope_class: scopeClass || null,
      scope_id: scopeId || null,
      download_images: downloadImages,
      link_type: linkType,
      combine_results: combineResults,
      auth_method: hasAuth ? authMethod : null,
      cookies: (hasAuth && authMethod === 'cookies') ? cookies : null,
      auth_headers: (hasAuth && authMethod === 'headers') ? authHeaders : null,
      basic_auth_username: (hasAuth && authMethod === 'basic') ? basicAuthUsername : null,
      basic_auth_password: (hasAuth && authMethod === 'basic') ? basicAuthPassword : null,
    };

    console.log('Final jobData to be saved:', jobData);
    await onSaveJob(jobData);
    setShowSaveModal(false);
  };

  const handleFormatChange = (format) => {
    setFormats(prev => 
      prev.includes(format)
        ? prev.filter(f => f !== format)
        : [...prev, format]
    );
  };

  const availableFormats = mode === 'content' 
    ? ['txt', 'md', 'html'] 
    : ['txt', 'json'];

  return (
    <>
    <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-lg p-6 md:p-8">
      {/* Loaded Job Indicator */}
      {loadedJobName && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-blue-800">
                Loaded Job Configuration
              </h3>
              <div className="mt-1 text-sm text-blue-700">
                <p className="font-semibold">{loadedJobName}</p>
                {loadedJobDescription && (
                  <p className="mt-1 text-blue-600">{loadedJobDescription}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Input Method Selector */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          Input Method
        </label>
        <div className="flex space-x-4">
          <button
            type="button"
            onClick={() => setInputMethod('single')}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
              inputMethod === 'single'
                ? 'bg-primary-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Single URL
          </button>
          <button
            type="button"
            onClick={() => setInputMethod('bulk')}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
              inputMethod === 'bulk'
                ? 'bg-primary-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Bulk CSV
          </button>
        </div>
      </div>

      {/* Mode Selector */}
      <ModeSelector mode={mode} onChange={setMode} />

      {/* URL or CSV Input */}
      {inputMethod === 'single' ? (
        <URLInput url={url} onChange={setUrl} error={errors.url} />
      ) : (
        <>
          <CSVUpload file={csvFile} onChange={setCsvFile} error={errors.csv} mode={mode} />

          {/* Combine Results Option */}
          <div className="mb-6 border-t pt-6">
            <div className="flex items-center mb-3">
              <input
                type="checkbox"
                id="combineResults"
                checked={combineResults}
                onChange={(e) => setCombineResults(e.target.checked)}
                className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="combineResults" className="ml-3 text-sm font-semibold text-gray-700">
                📄 Combine all results into a single file
              </label>
            </div>

            <p className="text-xs text-gray-600">
              💡 When enabled, all crawled content will be merged into one consolidated file instead of separate files for each URL.
            </p>
          </div>

          {/* Bulk CSV Global Authentication Section */}
          <div className="mb-6 border-t pt-6">
            <div className="flex items-center mb-3">
              <input
                type="checkbox"
                id="bulkGlobalAuth"
                checked={bulkGlobalAuth}
                onChange={(e) => setBulkGlobalAuth(e.target.checked)}
                className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="bulkGlobalAuth" className="ml-3 text-sm font-semibold text-gray-700">
                Apply authentication to all URLs in CSV
              </label>
            </div>
            
            <p className="text-xs text-gray-600 mb-4">
              💡 Enable this to use the same authentication for all URLs. If disabled, 
              authentication will be read from CSV columns (auth_enabled, auth_type, cookies, etc.)
            </p>
            
            {bulkGlobalAuth && (
              <div className="bg-gray-50 rounded-lg p-4 space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                  <p className="text-sm text-blue-800 font-medium mb-1">
                    🔐 Global Authentication for All URLs
                  </p>
                  <p className="text-xs text-blue-700">
                    These credentials will be applied to every URL in your CSV file.
                  </p>
                </div>

                {/* Authentication Method Selector */}
                <div className="mb-4">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Authentication Method
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => setAuthMethod('cookies')}
                      className={`py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                        authMethod === 'cookies'
                          ? 'bg-primary-600 text-white shadow-md'
                          : 'bg-white text-gray-700 border border-gray-300 hover:border-primary-400'
                      }`}
                    >
                      Cookies
                    </button>
                    <button
                      type="button"
                      onClick={() => setAuthMethod('headers')}
                      className={`py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                        authMethod === 'headers'
                          ? 'bg-primary-600 text-white shadow-md'
                          : 'bg-white text-gray-700 border border-gray-300 hover:border-primary-400'
                      }`}
                    >
                      Headers
                    </button>
                    <button
                      type="button"
                      onClick={() => setAuthMethod('basic')}
                      className={`py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                        authMethod === 'basic'
                          ? 'bg-primary-600 text-white shadow-md'
                          : 'bg-white text-gray-700 border border-gray-300 hover:border-primary-400'
                      }`}
                    >
                      Basic Auth
                    </button>
                  </div>
                </div>

                {/* Cookies Input */}
                {authMethod === 'cookies' && (
                  <div>
                    <label htmlFor="bulkCookies" className="block text-sm font-semibold text-gray-700 mb-2">
                      Cookies
                    </label>
                    <textarea
                      id="bulkCookies"
                      value={cookies}
                      onChange={(e) => setCookies(e.target.value)}
                      placeholder='session=abc123; token=xyz789'
                      rows="3"
                      className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Paste cookies from Browser DevTools
                    </p>
                  </div>
                )}

                {/* Authentication Headers */}
                {authMethod === 'headers' && (
                  <div>
                    <label htmlFor="bulkAuthHeaders" className="block text-sm font-semibold text-gray-700 mb-2">
                      Authentication Headers (JSON)
                    </label>
                    <textarea
                      id="bulkAuthHeaders"
                      value={authHeaders}
                      onChange={(e) => setAuthHeaders(e.target.value)}
                      placeholder='{"Authorization": "Bearer your-token"}'
                      rows="2"
                      className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
                    />
                  </div>
                )}

                {/* Basic Authentication */}
                {authMethod === 'basic' && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="bulkBasicAuthUsername" className="block text-sm font-semibold text-gray-700 mb-2">
                        Username
                      </label>
                      <input
                        type="text"
                        id="bulkBasicAuthUsername"
                        value={basicAuthUsername}
                        onChange={(e) => setBasicAuthUsername(e.target.value)}
                        placeholder="username"
                        className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label htmlFor="bulkBasicAuthPassword" className="block text-sm font-semibold text-gray-700 mb-2">
                        Password
                      </label>
                      <input
                        type="password"
                        id="bulkBasicAuthPassword"
                        value={basicAuthPassword}
                        onChange={(e) => setBasicAuthPassword(e.target.value)}
                        placeholder="password"
                        className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </>
      )}

      {/* Content Mode Options */}
      {mode === 'content' && inputMethod === 'single' && (
        <>
          {/* Output Formats */}
          <div className="mb-4">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Output Formats
            </label>
            <div className="flex flex-wrap gap-3">
              {availableFormats.map(format => (
                <label key={format} className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formats.includes(format)}
                    onChange={() => handleFormatChange(format)}
                    className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700 uppercase">
                    {format}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Scope Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label htmlFor="scopeClass" className="block text-sm font-semibold text-gray-700 mb-2">
                Scope Class (Optional)
              </label>
              <input
                type="text"
                id="scopeClass"
                value={scopeClass}
                onChange={(e) => setScopeClass(e.target.value)}
                placeholder="main-content"
                className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div>
              <label htmlFor="scopeId" className="block text-sm font-semibold text-gray-700 mb-2">
                Scope ID (Optional)
              </label>
              <input
                type="text"
                id="scopeId"
                value={scopeId}
                onChange={(e) => setScopeId(e.target.value)}
                placeholder="article-content"
                className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Download Images */}
          <div className="mb-4">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={downloadImages}
                onChange={(e) => setDownloadImages(e.target.checked)}
                className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <span className="ml-3 text-sm font-medium text-gray-700">
                Download images from the page
              </span>
            </label>
          </div>
        </>
      )}

      {/* Link Mode Options */}
      {mode === 'link' && inputMethod === 'single' && (
        <>
          {/* Output Formats */}
          <div className="mb-4">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Output Formats
            </label>
            <div className="flex flex-wrap gap-3">
              {availableFormats.map(format => (
                <label key={format} className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formats.includes(format)}
                    onChange={() => handleFormatChange(format)}
                    className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700 uppercase">
                    {format}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Scope Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label htmlFor="scopeClass" className="block text-sm font-semibold text-gray-700 mb-2">
                Scope Class (Optional)
              </label>
              <input
                type="text"
                id="scopeClass"
                value={scopeClass}
                onChange={(e) => setScopeClass(e.target.value)}
                placeholder="main-content"
                className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div>
              <label htmlFor="scopeId" className="block text-sm font-semibold text-gray-700 mb-2">
                Scope ID (Optional)
              </label>
              <input
                type="text"
                id="scopeId"
                value={scopeId}
                onChange={(e) => setScopeId(e.target.value)}
                placeholder="article-content"
                className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Link Type Filter */}
          <div className="mb-4">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Link Type Filter
            </label>
            <div className="flex space-x-4">
              {['all', 'internal', 'external'].map(type => (
                <label key={type} className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="linkType"
                    value={type}
                    checked={linkType === type}
                    onChange={(e) => setLinkType(e.target.value)}
                    className="w-5 h-5 text-primary-600 border-gray-300 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700 capitalize">
                    {type}
                  </span>
                </label>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Authentication Section (for intranet/protected sites) */}
      {inputMethod === 'single' && (
        <div className="mb-6 border-t pt-6">
          <button
            type="button"
            onClick={() => setShowAuth(!showAuth)}
            className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 font-medium transition-colors mb-3"
          >
            <FiLock className="h-4 w-4" />
            <span>{showAuth ? 'Hide' : 'Show'} Authentication Options</span>
            {showAuth ? (
              <FiChevronUp className="h-4 w-4" />
            ) : (
              <FiChevronDown className="h-4 w-4" />
            )}
          </button>
          
          {showAuth && (
            <div className="bg-gray-50 rounded-lg p-4 space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                <p className="text-sm text-blue-800 font-medium mb-1">
                  🔐 For Intranet/Protected Sites
                </p>
                <p className="text-xs text-blue-700">
                  Choose the authentication method your site uses. Most company intranets use cookies.
                </p>
              </div>

              {/* Authentication Method Selector */}
              <div className="mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Authentication Method
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => setAuthMethod('cookies')}
                    className={`py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                      authMethod === 'cookies'
                        ? 'bg-primary-600 text-white shadow-md'
                        : 'bg-white text-gray-700 border border-gray-300 hover:border-primary-400'
                    }`}
                  >
                    Cookies
                  </button>
                  <button
                    type="button"
                    onClick={() => setAuthMethod('headers')}
                    className={`py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                      authMethod === 'headers'
                        ? 'bg-primary-600 text-white shadow-md'
                        : 'bg-white text-gray-700 border border-gray-300 hover:border-primary-400'
                    }`}
                  >
                    Headers
                  </button>
                  <button
                    type="button"
                    onClick={() => setAuthMethod('basic')}
                    className={`py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                      authMethod === 'basic'
                        ? 'bg-primary-600 text-white shadow-md'
                        : 'bg-white text-gray-700 border border-gray-300 hover:border-primary-400'
                    }`}
                  >
                    Basic Auth
                  </button>
                </div>
              </div>

              {/* Cookies Input - Only show when cookies method selected */}
              {authMethod === 'cookies' && (
                <div>
                  <label htmlFor="cookies" className="block text-sm font-semibold text-gray-700 mb-2">
                    Cookies
                  </label>
                  <textarea
                    id="cookies"
                    value={cookies}
                    onChange={(e) => setCookies(e.target.value)}
                    placeholder='Paste from DevTools: cookie1=value1; cookie2=value2
Or JSON: {"cookie1": "value1", "cookie2": "value2"}'
                    rows="4"
                    className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
                  />
                  {errors.cookies && (
                    <p className="text-red-600 text-sm mt-1">{errors.cookies}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    💡 <strong>Tip:</strong> Open DevTools (F12) → Network tab → Click any request → Copy the entire &quot;cookie&quot; value from Request Headers
                  </p>
                </div>
              )}

              {/* Authentication Headers - Only show when headers method selected */}
              {authMethod === 'headers' && (
                <div>
                  <label htmlFor="authHeaders" className="block text-sm font-semibold text-gray-700 mb-2">
                    Authentication Headers (JSON format)
                  </label>
                  <textarea
                    id="authHeaders"
                    value={authHeaders}
                    onChange={(e) => setAuthHeaders(e.target.value)}
                    placeholder='{"Authorization": "Bearer your-token", "X-API-Key": "key123"}'
                    rows="2"
                    className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
                  />
                  {errors.authHeaders && (
                    <p className="text-red-600 text-sm mt-1">{errors.authHeaders}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    For Bearer tokens or API keys (found in Network tab → Request Headers)
                  </p>
                </div>
              )}

              {/* Basic Authentication - Only show when basic method selected */}
              {authMethod === 'basic' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="basicAuthUsername" className="block text-sm font-semibold text-gray-700 mb-2">
                      Username
                    </label>
                    <input
                      type="text"
                      id="basicAuthUsername"
                      value={basicAuthUsername}
                      onChange={(e) => setBasicAuthUsername(e.target.value)}
                      placeholder="username"
                      className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label htmlFor="basicAuthPassword" className="block text-sm font-semibold text-gray-700 mb-2">
                      Password
                    </label>
                    <input
                      type="password"
                      id="basicAuthPassword"
                      value={basicAuthPassword}
                      onChange={(e) => setBasicAuthPassword(e.target.value)}
                      placeholder="password"
                      className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <p className="text-xs text-gray-500 col-span-2 -mt-2">
                    For sites that show a browser popup asking for username/password
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      {inputMethod === 'single' ? (
        <div className="space-y-3">
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handlePreview}
              disabled={isLoading}
              className="flex-1 flex items-center justify-center space-x-2 bg-white text-primary-600 border-2 border-primary-600 py-3.5 px-6 rounded-lg hover:bg-primary-50 disabled:bg-gray-100 disabled:text-gray-400 disabled:border-gray-300 disabled:cursor-not-allowed transition-colors font-semibold text-lg shadow-lg hover:shadow-xl"
            >
              <FiEye className="h-5 w-5" />
              <span>Preview Page</span>
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 flex items-center justify-center space-x-2 bg-primary-600 text-white py-3.5 px-6 rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold text-lg shadow-lg hover:shadow-xl"
            >
              {isLoading ? (
                <>
                  <FiLoader className="h-5 w-5 animate-spin" />
                  <span>Crawling...</span>
                </>
              ) : (
                <>
                  <FiPlay className="h-5 w-5" />
                  <span>Start Crawling</span>
                </>
              )}
            </button>
          </div>
          {onSaveJob && (
            <button
              type="button"
              onClick={() => setShowSaveModal(true)}
              disabled={isLoading}
              className="w-full flex items-center justify-center space-x-2 bg-white text-gray-700 border-2 border-gray-300 py-2.5 px-4 rounded-lg hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400 disabled:border-gray-300 disabled:cursor-not-allowed transition-colors font-medium shadow-sm hover:shadow-md"
            >
              <FiSave className="h-4 w-4" />
              <span>Save Job Configuration</span>
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center space-x-2 bg-primary-600 text-white py-3.5 px-6 rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold text-lg shadow-lg hover:shadow-xl"
          >
            {isLoading ? (
              <>
                <FiLoader className="h-5 w-5 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <FiPlay className="h-5 w-5" />
                <span>Start Crawling</span>
              </>
            )}
          </button>
          {onSaveJob && (
            <button
              type="button"
              onClick={() => setShowSaveModal(true)}
              disabled={isLoading}
              className="w-full flex items-center justify-center space-x-2 bg-white text-gray-700 border-2 border-gray-300 py-2.5 px-4 rounded-lg hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400 disabled:border-gray-300 disabled:cursor-not-allowed transition-colors font-medium shadow-sm hover:shadow-md"
            >
              <FiSave className="h-4 w-4" />
              <span>Save Job Configuration</span>
            </button>
          )}
        </div>
      )}
    </form>

    {/* Save Job Modal - Outside form to prevent form submission issues */}
    <SaveJobModal
      isOpen={showSaveModal}
      onClose={() => setShowSaveModal(false)}
      onSave={handleSaveJob}
      initialData={{
        name: loadedJobName,
        description: loadedJobDescription
      }}
    />
  </>
  );
};

export default CrawlForm;
