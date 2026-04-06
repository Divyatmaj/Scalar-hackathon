import React from 'react';
import './QuestionCard.css';

function QuestionCard({ question, difficulty }) {
  const getDifficultyColor = (diff) => {
    switch (diff?.toLowerCase()) {
      case 'easy': return '#4caf50';
      case 'medium': return '#ff9800';
      case 'hard': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  return (
    <div className="question-card">
      <div className="question-header">
        <h2>📝 Current Question</h2>
        <span 
          className="difficulty-badge"
          style={{ backgroundColor: getDifficultyColor(difficulty) }}
        >
          {difficulty?.toUpperCase() || 'UNKNOWN'}
        </span>
      </div>
      <div className="question-content">
        <p>{question}</p>
      </div>
    </div>
  );
}

export default QuestionCard;
