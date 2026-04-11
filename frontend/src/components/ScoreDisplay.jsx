import React from 'react';
import './ScoreDisplay.css';

function ScoreDisplay({ score, reward, feedback }) {
  const clampOpenValue = (value) => {
    const numeric = Number(value);
    const safeNumeric = Number.isFinite(numeric) ? numeric : 0.1;
    return Math.min(0.9, Math.max(0.1, safeNumeric));
  };

  const safeScore = clampOpenValue(score);
  const safeReward = clampOpenValue(reward);

  const getScoreColor = (score) => {
    if (score >= 0.8) return '#4caf50';
    if (score >= 0.5) return '#ff9800';
    if (score >= 0.3) return '#ffc107';
    return '#f44336';
  };

  const getRewardEmoji = (reward) => {
    if (reward >= 0.8) return '🏆';
    if (reward >= 0.6) return '👍';
    if (reward >= 0.4) return '🤔';
    return '⚠️';
  };

  return (
    <div className="score-display">
      <h3>📊 Evaluation Results</h3>
      
      <div className="metrics">
        <div className="metric-card">
          <div className="metric-label">Score</div>
          <div 
            className="metric-value"
            style={{ color: getScoreColor(safeScore) }}
          >
            {(safeScore * 100).toFixed(1)}%
          </div>
          <div className="metric-bar">
            <div 
              className="metric-fill"
              style={{ 
                width: `${safeScore * 100}%`,
                backgroundColor: getScoreColor(safeScore)
              }}
            />
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Reward</div>
          <div className={`metric-value reward-${safeReward >= 0.7 ? 'positive' : safeReward <= 0.3 ? 'negative' : 'neutral'}`}>
            {getRewardEmoji(safeReward)} {safeReward.toFixed(1)}
          </div>
        </div>
      </div>

      <div className="feedback-section">
        <h4>💬 Feedback</h4>
        <p className="feedback-text">{feedback}</p>
      </div>
    </div>
  );
}

export default ScoreDisplay;
