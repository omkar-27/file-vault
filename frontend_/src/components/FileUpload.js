import React, { useState } from 'react';
import axios from 'axios';
import './FileUpload.css';

function FileUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (replace = false) => {
    if (!file) {
      setMessage('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    if (replace) formData.append('replace', 'true');

    try {
      setUploading(true); // Show loader
      const res = await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (res.data.status === 'duplicate') {
        setMessage('File already exists with the same content. Not uploaded again.');
      } else if (res.data.status === 'name_conflict') {
        const confirmReplace = window.confirm(
          `A file named "${file.name}" already exists with different content.\nDo you want to replace it?`
        );
        if (confirmReplace) {
          handleUpload(true);
        } else {
          setMessage('Upload cancelled by user.');
        }
      } else {
        const filePath = res.data.file;
        const uploadedFilename =
          res.data.filename ||
          (filePath && typeof filePath === 'string' ? filePath.split('/').pop() : null);

        setMessage('Uploaded successfully.');
        setTimeout(() => {
            window.location.reload(); // Refresh after 2 seconds
          }, 2000);
      }
    } catch (err) {
      const response = err.response;
      setMessage(`Upload failed: ${response?.data?.error || err.message}`);
    } finally {
      setUploading(false); // Hide loader
    }
  };

  return (
    <div className="upload-container">
      <h2>📤 Upload a File</h2>
      <input type="file" onChange={e => setFile(e.target.files[0])} />
      <button onClick={() => handleUpload()} disabled={uploading}>
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
      {message && <p className="upload-message">{message}</p>}
    </div>
  );
}

export default FileUpload;
