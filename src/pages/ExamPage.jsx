import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ExamPage.css';

const ExamPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [grades, setGrades] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (location.state?.questions) {
      setQuestions(location.state.questions);
      setAnswers({});
      setGrades({});
    } else {
      navigate('/');
    }
  }, [location, navigate]);

  const handleAnswerChange = (e) => {
    setAnswers({
      ...answers,
      [currentQIndex]: e.target.value
    });
  };

  const handleGradeAnswer = async () => {
    const answer = answers[currentQIndex] || "";
    
    if (!answer.trim()) {
      setError("Please type an answer before submitting.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch("https://ai-exam-tawny.vercel.app/api/grade-answer", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: questions[currentQIndex],
          answer: answer
        }),
      });

      const data = await response.json();

      if (data.success) {
        try {
          const evaluation = JSON.parse(data.evaluation);
          setGrades({
            ...grades,
            [currentQIndex]: evaluation
          });
        } catch (parseError) {
          setError("Error parsing grading response. Please try again.");
          console.error("Parse error:", parseError);
        }
      } else {
        setError("Grading Error: " + data.error);
      }
    } catch (error) {
      console.error("Network communication failed:", error);
      setError("Could not connect to grading service. Make sure API key is configured.");
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (currentQIndex < questions.length - 1) {
      setCurrentQIndex(currentQIndex + 1);
      setError("");
    }
  };

  const handlePrev = () => {
    if (currentQIndex > 0) {
      setCurrentQIndex(currentQIndex - 1);
      setError("");
    }
  };

  const handleFinish = () => {
    navigate('/report', { state: { questions, answers, grades } });
  };

  if (!questions.length) {
    return <div className="exam-container"><p>Loading exam...</p></div>;
  }

  const currentQuestion = questions[currentQIndex];
  const currentGrade = grades[currentQIndex];

  return (
    <div className="exam-container">
      <div className="exam-card">
        <div className="progress-bar">
          <div className="progress" style={{ width: `${((currentQIndex + 1) / questions.length) * 100}%` }}></div>
        </div>
        
        <div className="question-header">
          <h2>Question {currentQIndex + 1} of {questions.length}</h2>
        </div>

        <div className="question-box">
          <p className="question-text">{currentQuestion}</p>
        </div>

        <textarea
          className="answer-input"
          placeholder="Type your answer here..."
          value={answers[currentQIndex] || ""}
          onChange={handleAnswerChange}
          rows="6"
        />

        {currentGrade && (
          <div className="grade-box">
            <h3>✅ Graded!</h3>
            <div className="score">Score: <span className="score-value">{currentGrade.score}/100</span></div>
            <p className="explanation">{currentGrade.explanation}</p>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}

        <div className="button-group">
          <button 
            className="btn-secondary"
            onClick={handlePrev}
            disabled={currentQIndex === 0}
          >
            ← Previous
          </button>

          {!currentGrade ? (
            <button 
              className="btn-primary"
              onClick={handleGradeAnswer}
              disabled={loading}
            >
              {loading ? "⏳ Grading..." : "📝 Submit & Grade"}
            </button>
          ) : (
            <button 
              className="btn-primary"
              onClick={handleNext}
              disabled={currentQIndex === questions.length - 1}
            >
              Next →
            </button>
          )}

          {currentQIndex === questions.length - 1 && currentGrade && (
            <button 
              className="btn-success"
              onClick={handleFinish}
            >
              📊 View Report
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExamPage;
