import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const kmlApi = {
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Upload failed');
    }
  },

  parseFile: async (filePath) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/parse/kml`, {
        file_path: filePath,
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Parse failed');
    }
  },

  exportData: async (filePath, format) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/export/${format}`, {
        file_path: filePath,
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Export failed');
    }
  },
};

export default kmlApi;
