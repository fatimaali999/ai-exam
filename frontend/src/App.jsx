import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import ExamPage from './pages/ExamPage';
import ReportPage from './pages/ReportPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/exam" element={<ExamPage />} />
          <Route path="/report" element={<ReportPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
