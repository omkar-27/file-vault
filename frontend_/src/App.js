import React from 'react';
import FileUpload from './components/FileUpload';
import FileList from './components/FileList';

function App() {
  return (
    <div className="App">
      <h1>Abnormal File Vault</h1>
      <FileUpload />
      <hr />
      <FileList />
    </div>
  );
}

export default App;