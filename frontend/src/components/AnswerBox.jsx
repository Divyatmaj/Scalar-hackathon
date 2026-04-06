import React from 'react';
import './AnswerBox.css';

function AnswerBox({ answer, setAnswer, onSubmit, disabled }) {
  return (
    <div className="answer-box">
      <h3>✍️ Your Answer (Manual Mode)</h3>
      <textarea
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        placeholder="Type your answer here... (or use 'Generate AI Answer' for automatic mode)"
        rows="6"
        disabled={disabled}
        className="answer-textarea"
      />
      <button 
        onClick={onSubmit}
        disabled={disabled || !answer.trim()}
        className="btn btn-secondary"
      >
        {disabled ? '⏳ Processing...' : '📤 Submit Answer'}
      </button>
    </div>
  );
}

export default AnswerBox;
