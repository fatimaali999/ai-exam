import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './UploadPage.css';

const UploadPage = () => {
  const [loading, setLoading] = useState(false);
  const [notesText, setNotesText] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleGenerateQuestions = async () => {
    if (!notesText.trim()) {
      setError("Please paste or upload some study notes first!");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      // FIX: Changed from absolute web link to standard relative API cloud path routing
      const response = await fetch("/api/generate-questions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ notes: notesText }),
      });

      const data = await response.json();

      if (data.success) {
        try {
          const completeExamQuestions = JSON.parse(data.questions);
          console.log("Your 10 Exam Questions are ready:", completeExamQuestions);
          
          // Route right into your interactive exam interface page view container
          navigate('/exam', { state: { questions: completeExamQuestions } });
        } catch (parseError) {
          setError("Error parsing questions from AI. Please try again.");
          console.error("Parse error:", parseError);
        }
        
      } else {
        setError("AI Generation Error: " + data.error);
      }
    } catch (error) {
      console.error("Network communication failed:", error);
      setError("Could not connect to your cloud serverless function. Make sure GEMINI_API_KEY is set in Vercel.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-card">
        <h1>📚 AI Exam Simulator</h1>
        <p className="subtitle">Upload your study notes and let AI generate personalized exam questions</p>
        
        <textarea
          className="notes-input"
          placeholder="Paste your study notes, PDF text, or lecture slides here..."
          value={notesText}
          onChange={(e) => setNotesText(e.target.value)}
          rows="12"
        />
        
        {error && <div className="error-message">{error}</div>}
        
        <button 
          className="generate-btn"
          onClick={handleGenerateQuestions}
          disabled={loading}
        >
          {loading ? "⏳ AI is reviewing notes..." : "✨ Generate Custom Exam"}
        </button>
        
        <p className="info-text">
          Your notes are processed securely. A 10-question exam will be generated based on your content.
        </p>
      </div>
    </div>
  );
};

export default UploadPage;