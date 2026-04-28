import React, { useState } from 'react';
import xmlApi from '../services/xmlApi';

function UploadXML({ onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const response = await xmlApi.uploadFile(file);
      onSuccess(response.data, response.file_type);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-component">
      <h3>📤 Upload XML/OSM File</h3>
      <input
        type="file"
        accept=".osm,.xml"
        onChange={handleUpload}
        disabled={loading}
      />
      {loading && <p>Uploading...</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default UploadXML;
