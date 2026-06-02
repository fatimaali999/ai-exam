import React, { useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ReportPage.css';

const ReportPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { questions, answers, grades } = location.state || { questions: [], answers: {}, grades: {} };

  const statistics = useMemo(() => {
    const scores = Object.values(grades).map(g => g.score || 0);
    const totalScore = scores.reduce((a, b) => a + b, 0);
    const averageScore = scores.length ? (totalScore / scores.length).toFixed(1) : 0;
    const answeredCount = Object.keys(grades).length;

    return {
      totalScore,
      averageScore,
      answeredCount,
      totalQuestions: questions.length,
      scores
    };
  }, [grades, questions]);

  const handleRetry = () => {
    navigate('/');
  };

  if (!questions.length) {
    return <div className="report-container"><p>No exam data found.</p></div>;
  }

  return (
    <div className="report-container">
      <div className="report-card">
        <h1>📊 Exam Report</h1>

        <div className="stats-grid">
          <div className="stat-box">
            <h3>Average Score</h3>
            <p className="stat-value">{statistics.averageScore}%</p>
          </div>
          <div className="stat-box">
            <h3>Questions Answered</h3>
            <p className="stat-value">{statistics.answeredCount}/{statistics.totalQuestions}</p>
          </div>
          <div className="stat-box">
            <h3>Total Points</h3>
            <p className="stat-value">{statistics.totalScore}</p>
          </div>
        </div>

        <div className="questions-review">
          <h2>📋 Detailed Feedback</h2>
          {questions.map((question, index) => {
            const grade = grades[index];
            return (
              <div key={index} className="review-item">
                <h4>Question {index + 1}</h4>
                <p className="q-text"><strong>Q:</strong> {question}</p>
                <p className="a-text"><strong>Your Answer:</strong> {answers[index] || "Not answered"}</p>
                
                {grade ? (
                  <div className="feedback">
                    <p className="score">Score: <span className={`score-badge ${grade.score >= 70 ? 'pass' : 'fail'}`}>{grade.score}/100</span></p>
                    <p className="explanation"><strong>Feedback:</strong> {grade.explanation}</p>
                  </div>
                ) : (
                  <p className="not-graded">⏳ Not graded yet</p>
                )}
              </div>
            );
          })}
        </div>

        <div className="recommendations">
          <h3>📚 Revision Recommendations</h3>
          <ul>
            {statistics.scores.map((score, idx) => {
              if (score < 60) {
                return <li key={idx}>❌ Question {idx + 1}: Review this concept carefully - Score was {score}%</li>;
              } else if (score < 80) {
                return <li key={idx}>⚠️ Question {idx + 1}: Good attempt but some details were missing - Score was {score}%</li>;
              } else {
                return <li key={idx}>✅ Question {idx + 1}: Excellent understanding - Score was {score}%</li>;
              }
            })}
          </ul>
        </div>

        <button className="btn-retry" onClick={handleRetry}>
          🔄 Try Another Exam
        </button>
      </div>
    </div>
  );
};

export default ReportPage;
