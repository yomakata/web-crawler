import { FiGlobe } from 'react-icons/fi';

const URLInput = ({ url, onChange, error }) => {
  return (
    <div className="mb-4">
      <label htmlFor="url" className="block text-sm font-semibold text-gray-700 mb-2">
        URL to Crawl
      </label>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <FiGlobe className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="url"
          id="url"
          value={url}
          onChange={(e) => onChange(e.target.value)}
          placeholder="https://example.com"
          className={`block w-full pl-10 pr-3 py-3 border ${
            error ? 'border-error-500' : 'border-gray-300'
          } rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors`}
        />
      </div>
      {error && (
        <p className="mt-2 text-sm text-error-600">{error}</p>
      )}
    </div>
  );
};

export default URLInput;
