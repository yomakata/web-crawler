import { useState, useEffect } from 'react';
import { FiX, FiSave, FiAlertTriangle } from 'react-icons/fi';

const SaveJobModal = ({ isOpen, onClose, onSave, initialData = {} }) => {
  const [name, setName] = useState(initialData.name || '');
  const [description, setDescription] = useState(initialData.description || '');
  const [isSaving, setIsSaving] = useState(false);
  const [showConfirmUpdate, setShowConfirmUpdate] = useState(false);
  const [existingJob, setExistingJob] = useState(null);

  // Update form when modal opens with new initial data
  useEffect(() => {
    if (isOpen) {
      setName(initialData.name || '');
      setDescription(initialData.description || '');
      setShowConfirmUpdate(false);
      setExistingJob(null);
    }
  }, [isOpen, initialData.name, initialData.description]);

  if (!isOpen) return null;

  const handleSubmit = async (e, forceUpdate = false) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const result = await onSave({ name, description, force_update: forceUpdate });
      
      // Check if we got a duplicate name error
      if (result && result.error === 'duplicate_name') {
        setExistingJob(result.existing_job);
        setShowConfirmUpdate(true);
        setIsSaving(false);
        return;
      }
      
      // Success - close modal
      onClose();
      setShowConfirmUpdate(false);
      setExistingJob(null);
    } catch (error) {
      // Check if the error response indicates duplicate
      if (error.response?.data?.error === 'duplicate_name') {
        setExistingJob(error.response.data.existing_job);
        setShowConfirmUpdate(true);
      } else {
        // Only log unexpected errors
        console.error('Save job error:', error);
        alert('Failed to save job: ' + (error.response?.data?.message || error.message));
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleConfirmUpdate = (e) => {
    handleSubmit(e, true);
  };

  const handleCancelUpdate = () => {
    setShowConfirmUpdate(false);
    setExistingJob(null);
    setIsSaving(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Show confirmation dialog if duplicate name detected */}
        {showConfirmUpdate ? (
          <>
            {/* Confirmation Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <FiAlertTriangle className="h-6 w-6 text-yellow-500" />
                <h2 className="text-xl font-semibold text-gray-900">Job Name Already Exists</h2>
              </div>
              <button
                onClick={() => {
                  handleCancelUpdate();
                  onClose();
                }}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <FiX className="h-6 w-6" />
              </button>
            </div>

            {/* Confirmation Content */}
            <div className="p-6">
              <p className="text-gray-700 mb-4">
                A job with the name <strong>&quot;{name}&quot;</strong> already exists. Do you want to update and replace the existing job configuration?
              </p>
              
              {existingJob && (
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Existing Job Details:</p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {existingJob.description && (
                      <li><strong>Description:</strong> {existingJob.description}</li>
                    )}
                    <li><strong>Input Method:</strong> {existingJob.input_method === 'single' ? 'Single URL' : 'Bulk CSV'}</li>
                    <li><strong>Mode:</strong> {existingJob.mode}</li>
                    {existingJob.url && (
                      <li><strong>URL:</strong> {existingJob.url.substring(0, 50)}{existingJob.url.length > 50 ? '...' : ''}</li>
                    )}
                    <li><strong>Last Updated:</strong> {new Date(existingJob.updated_at).toLocaleString()}</li>
                  </ul>
                </div>
              )}

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                <p className="text-sm text-yellow-800">
                  ⚠️ This will permanently replace the existing job configuration with the new one.
                </p>
              </div>

              {/* Confirmation Actions */}
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleCancelUpdate}
                  disabled={isSaving}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleConfirmUpdate}
                  disabled={isSaving}
                  className="flex-1 flex items-center justify-center space-x-2 bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  <FiSave className="h-4 w-4" />
                  <span>{isSaving ? 'Updating...' : 'Update & Replace'}</span>
                </button>
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Normal Save Dialog Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Save Job Configuration</h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <FiX className="h-6 w-6" />
              </button>
            </div>

            {/* Normal Save Dialog Content */}
            <form onSubmit={handleSubmit} className="p-6">
              <div className="space-y-4">
                {/* Job Name */}
                <div>
                  <label htmlFor="jobName" className="block text-sm font-medium text-gray-700 mb-1">
                    Job Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="jobName"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g., Daily News Crawler"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                {/* Description */}
                <div>
                  <label htmlFor="jobDescription" className="block text-sm font-medium text-gray-700 mb-1">
                    Description (optional)
                  </label>
                  <textarea
                    id="jobDescription"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Add notes about this job configuration..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                  />
                </div>
              </div>

              {/* Footer */}
              <div className="flex gap-3 mt-6">
                <button
                  type="button"
                  onClick={onClose}
                  disabled={isSaving}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSaving || !name.trim()}
                  className="flex-1 flex items-center justify-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  <FiSave className="h-4 w-4" />
                  <span>{isSaving ? 'Saving...' : 'Save Job'}</span>
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
};

export default SaveJobModal;
