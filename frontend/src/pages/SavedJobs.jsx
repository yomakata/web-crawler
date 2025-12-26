import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { FiBookmark, FiTrash2, FiPlay, FiCalendar, FiGlobe, FiLock } from 'react-icons/fi';
import { crawlAPI } from '../services/api';

const SavedJobs = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Fetch saved jobs
  const { data: savedJobsData, isLoading } = useQuery(
    'savedJobs',
    () => crawlAPI.savedJobs.list(),
    {
      refetchOnMount: true,
    }
  );

  // Delete job mutation
  const deleteMutation = useMutation(
    (savedJobId) => crawlAPI.savedJobs.delete(savedJobId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('savedJobs');
        setDeleteConfirm(null);
      },
    }
  );

  const handleLoadJob = (job) => {
    // Navigate to crawler page with job data
    navigate('/crawler', { state: { savedJob: job } });
  };

  const handleDeleteJob = (savedJobId) => {
    deleteMutation.mutate(savedJobId);
  };

  const savedJobs = savedJobsData?.saved_jobs || [];

  return (
    <div className="flex-1 bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Saved Jobs</h1>
          <p className="text-gray-600">
            Manage your saved crawling configurations
          </p>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600">Loading saved jobs...</p>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && savedJobs.length === 0 && (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <FiBookmark className="mx-auto h-16 w-16 text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No saved jobs yet</h3>
            <p className="text-gray-600 mb-6">
              Save your crawling configurations for quick reuse
            </p>
            <button
              onClick={() => navigate('/crawler')}
              className="btn-primary"
            >
              Go to Crawler
            </button>
          </div>
        )}

        {/* Jobs Grid */}
        {!isLoading && savedJobs.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedJobs.map((job) => (
              <div
                key={job.saved_job_id}
                className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6"
              >
                {/* Job Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {job.name}
                    </h3>
                    {job.description && (
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {job.description}
                      </p>
                    )}
                  </div>
                  <FiBookmark className="text-primary-600 h-5 w-5 flex-shrink-0 ml-2" />
                </div>

                {/* Job Details */}
                <div className="space-y-2 mb-4 text-sm">
                  {/* Mode */}
                  <div className="flex items-center text-gray-600">
                    <span className="font-medium w-20">Mode:</span>
                    <span className="capitalize">{job.mode}</span>
                  </div>

                  {/* URL or CSV */}
                  {job.input_method === 'single' && job.url && (
                    <div className="flex items-start text-gray-600">
                      <FiGlobe className="h-4 w-4 mt-0.5 mr-2 flex-shrink-0" />
                      <span className="break-all text-xs">{job.url}</span>
                    </div>
                  )}
                  {job.input_method === 'bulk' && job.csv_filename && (
                    <div className="flex items-center text-gray-600">
                      <span className="font-medium">CSV:</span>
                      <span className="ml-2 text-xs">{job.csv_filename}</span>
                    </div>
                  )}

                  {/* Scope */}
                  {(job.scope_class || job.scope_id) && (
                    <div className="flex items-center text-gray-600">
                      <span className="font-medium w-20">Scope:</span>
                      <span className="text-xs">
                        {job.scope_class && `class="${job.scope_class}"`}
                        {job.scope_id && `id="${job.scope_id}"`}
                      </span>
                    </div>
                  )}

                  {/* Auth */}
                  {job.auth_method && (
                    <div className="flex items-center text-gray-600">
                      <FiLock className="h-4 w-4 mr-2" />
                      <span className="text-xs capitalize">{job.auth_method} auth</span>
                    </div>
                  )}

                  {/* Updated */}
                  <div className="flex items-center text-gray-500 text-xs">
                    <FiCalendar className="h-3 w-3 mr-1" />
                    <span>
                      Updated {new Date(job.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 pt-4 border-t border-gray-100">
                  <button
                    onClick={() => handleLoadJob(job)}
                    className="flex-1 btn-primary py-2 text-sm"
                  >
                    <FiPlay className="inline h-4 w-4 mr-1" />
                    Load Job
                  </button>
                  <button
                    onClick={() => setDeleteConfirm(job.saved_job_id)}
                    className="btn-secondary p-2"
                    title="Delete job"
                  >
                    <FiTrash2 className="h-4 w-4" />
                  </button>
                </div>

                {/* Delete Confirmation */}
                {deleteConfirm === job.saved_job_id && (
                  <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-800 mb-2">Delete this saved job?</p>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleDeleteJob(job.saved_job_id)}
                        disabled={deleteMutation.isLoading}
                        className="flex-1 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700 disabled:opacity-50"
                      >
                        {deleteMutation.isLoading ? 'Deleting...' : 'Delete'}
                      </button>
                      <button
                        onClick={() => setDeleteConfirm(null)}
                        className="flex-1 px-3 py-1 bg-white border border-gray-300 rounded text-sm hover:bg-gray-50"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SavedJobs;
