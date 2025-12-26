import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API methods
export const crawlAPI = {
  // Crawl single URL
  crawlSingle: async (data) => {
    const response = await api.post('/crawl/single', data);
    return response.data;
  },

  // Crawl bulk URLs from CSV
  crawlBulk: async (file, authData = null, combineResults = false) => {
    const formData = new FormData();
    formData.append('file', file);

    // Add combine results option
    if (combineResults) {
      formData.append('combine_results', 'true');
    }

    // Add authentication data if provided
    if (authData && authData.global_auth_enabled) {
      formData.append('global_auth_enabled', 'true');
      formData.append('auth_method', authData.auth_method);

      if (authData.cookies) {
        // Convert cookies object to string if needed
        const cookiesString = typeof authData.cookies === 'object'
          ? JSON.stringify(authData.cookies)
          : authData.cookies;
        formData.append('cookies', cookiesString);
      }
      if (authData.auth_headers) {
        formData.append('auth_headers', authData.auth_headers);
      }
      if (authData.basic_auth_username) {
        formData.append('basic_auth_username', authData.basic_auth_username);
        formData.append('basic_auth_password', authData.basic_auth_password || '');
      }
    }

    const response = await api.post('/crawl/bulk', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get job status
  getJobStatus: async (jobId) => {
    const response = await api.get(`/job/${jobId}/status`);
    return response.data;
  },

  // Get job results
  getJobResults: async (jobId) => {
    const response = await api.get(`/job/${jobId}/results`);
    return response.data;
  },

  // Get job metadata
  getJobMetadata: async (jobId) => {
    const response = await api.get(`/job/${jobId}/metadata`);
    return response.data;
  },

  // Preview page before extraction
  previewPage: async (data) => {
    const response = await api.post('/preview', data);
    return response.data;
  },

  // Get extraction history
  getHistory: async () => {
    const response = await api.get('/history');
    return response.data;
  },

  // Get saved jobs (convenience method)
  getSavedJobs: async () => {
    const response = await api.get('/jobs/saved');
    return response.data.saved_jobs || [];
  },

  // Delete job
  deleteJob: async (jobId) => {
    const response = await api.delete(`/job/${jobId}`);
    return response.data;
  },

  // Get download URL
  getDownloadUrl: (jobId, filename) => {
    return `${API_BASE_URL}/download/${jobId}/${filename}`;
  },

  // Get ZIP download URL (all files)
  getZipDownloadUrl: (jobId) => {
    return `${API_BASE_URL}/download/${jobId}`;
  },

  // Get debug HTML URL
  getDebugHtmlUrl: (debugPath) => {
    // Use absolute URL to backend to avoid React Router interception
    const backendUrl = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:5000';
    return `${backendUrl}/api/output/${debugPath}`;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Saved Jobs
  savedJobs: {
    // Create new saved job
    create: async (data) => {
      const response = await api.post('/jobs/saved', data);
      return response.data;
    },

    // Get all saved jobs
    list: async () => {
      const response = await api.get('/jobs/saved');
      return response.data;
    },

    // Get specific saved job
    get: async (savedJobId) => {
      const response = await api.get(`/jobs/saved/${savedJobId}`);
      return response.data;
    },

    // Update saved job
    update: async (savedJobId, data) => {
      const response = await api.put(`/jobs/saved/${savedJobId}`, data);
      return response.data;
    },

    // Delete saved job
    delete: async (savedJobId) => {
      const response = await api.delete(`/jobs/saved/${savedJobId}`);
      return response.data;
    },
  },
};

export default crawlAPI;
