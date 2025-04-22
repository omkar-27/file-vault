import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './FileList.css';

function FileList() {
  const [files, setFiles] = useState([]);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
  });

  const [filters, setFilters] = useState({
    filename: '',
    min_size: '',
    max_size: '',
    start_date: '',
    end_date: '',
    sort_by: 'uploaded_at',
    order: 'desc',
    page: 1,
  });

  const fetchFiles = async () => {
    try {
      const query = new URLSearchParams(filters).toString();
      const url = `http://127.0.0.1:8000/api/files/?${query}`;
      const res = await axios.get(url);
      
      // Ensure response structure has 'results' for files
      if (res.data && res.data.results) {
        setFiles(res.data.results);
        setPagination({
          count: res.data.count,
          next: res.data.next,
          previous: res.data.previous,
        });
      } else {
        showMessage('No files found or invalid response format.', 'error');
      }
    } catch (error) {
      showMessage('Failed to fetch files.', 'error');
    }
  };

  useEffect(() => {
    fetchFiles();
  }, [filters]);

  const handleDelete = async (fileId, filename) => {
    const confirmDelete = window.confirm(`Are you sure you want to delete "${filename}"?`);
    if (!confirmDelete) return;

    try {
      await axios.delete(`http://127.0.0.1:8000/api/files/${fileId}/`);
      setFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
      showMessage(`Deleted "${filename}" successfully.`, 'success');
    } catch (err) {
      showMessage(`Failed to delete "${filename}".`, 'error');
    }
  };

  const handleDownload = async (fileId, filename) => {
    try {
      const res = await axios.get(`http://127.0.0.1:8000/api/download/${fileId}/`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Download error:', error);
      alert('Download failed.');
    }
  };

  const showMessage = (msg, type) => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => setMessage(''), 3000);
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= Math.ceil(pagination.count / 8)) {
      setFilters({ ...filters, page: newPage });
    }
  };

  return (
    <div className="file-list-container">
      <h2 className="vault-title">🗃️ Abnormal File Vault</h2>

      {/* Search Section */}
      <div className="search-section">
        <input
          type="text"
          name="filename"
          value={filters.filename}
          onChange={e => setFilters({ ...filters, filename: e.target.value })}
          placeholder="Search by filename..."
          className="search-input"
        />
      </div>

      {message && <div className={`message ${messageType}`}>{message}</div>}

      <div className="file-grid">
        {files.length === 0 ? (
          <p>No files found.</p>
        ) : (
          files.map(file => (
            <div key={file.id} className="file-card">
              <h4>{file.filename}</h4>
              <p><strong>Size:</strong> {(file.size / 1024).toFixed(2)} KB</p>
              <p><strong>Uploaded:</strong> {new Date(file.uploaded_at).toLocaleString()}</p>

              <div className="file-actions">
                <button
                  className="download-btn"
                  onClick={() => handleDownload(file.id, file.filename)}
                  title="Download"
                >
                  ⬇️
                </button>

                <button
                  className="delete-btn"
                  onClick={() => handleDelete(file.id, file.filename)}
                  title="Delete"
                >
                  ❌
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="pagination">
        <button
          onClick={() => handlePageChange(filters.page - 1)}
          disabled={filters.page === 1}
        >
          Prev
        </button>
        <span>{filters.page} of {Math.ceil(pagination.count / 8)}</span>
        <button
          onClick={() => handlePageChange(filters.page + 1)}
          disabled={filters.page === Math.ceil(pagination.count / 8)}
        >
          Next
        </button>
      </div>
    </div>
  );
}

export default FileList;
