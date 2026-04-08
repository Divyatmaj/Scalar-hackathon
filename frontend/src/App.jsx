import React, { useState } from 'react';
import axios from 'axios';
import QuestionCard from './components/QuestionCard';
import AnswerBox from './components/AnswerBox';
import ScoreDisplay from './components/ScoreDisplay';
import SettingsModal from './components/SettingsModal';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [question, setQuestion] = useState(null);
  const [difficulty, setDifficulty] = useState('');
  const [answer, setAnswer] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [episodeData, setEpisodeData] = useState(null);
  const [rewardHistory, setRewardHistory] = useState([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Get new question
  const getQuestion = async () => {
    setLoading(true);
    setAnswer('');
    setResult(null);
    setEpisodeData(null);
    
    try {
      const response = await axios.get(`${API_URL}/question`);
      setQuestion(response.data.state.question);
      setDifficulty(response.data.state.difficulty);
    } catch (error) {
      console.error('Error fetching question:', error);
      alert('Failed to fetch question. Make sure backend is running on port 8000');
    } finally {
      setLoading(false);
    }
  };

  // Generate AI answer
  const generateAnswer = async () => {
    if (!question) {
      alert('Please get a question first!');
      return;
    }

    setLoading(true);
    setResult(null);
    setEpisodeData(null);
    
    try {
      const response = await axios.post(`${API_URL}/auto-run`, {
        use_retry: true
      });
      
      const episode = response.data.episode;
      setEpisodeData(episode);
      
      // Set the final answer and result
      const finalAttempt = episode.attempt_2 || episode.attempt_1;
      setAnswer(finalAttempt.answer);
      setResult({
        reward: finalAttempt.reward,
        score: finalAttempt.score,
        feedback: finalAttempt.feedback
      });

      // Update reward history
      setRewardHistory([...rewardHistory, finalAttempt.reward]);
      
    } catch (error) {
      console.error('Error generating answer:', error);
      alert('Failed to generate answer. Check if OPENAI_API_KEY is set (or it will use mock answers)');
    } finally {
      setLoading(false);
    }
  };

  // Submit manual answer
  const submitAnswer = async () => {
    if (!question) {
      alert('Please get a question first!');
      return;
    }
    if (!answer.trim()) {
      alert('Please enter an answer!');
      return;
    }

    setLoading(true);
    setResult(null);
    
    try {
      const response = await axios.post(`${API_URL}/answer`, {
        answer: answer
      });
      
      setResult(response.data.result);
      setRewardHistory([...rewardHistory, response.data.result.reward]);
      
    } catch (error) {
      console.error('Error submitting answer:', error);
      alert('Failed to submit answer');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="header">
        <h1>🤖 AI Interview Preparation</h1>
        <button 
          className="settings-btn"
          onClick={() => setIsSettingsOpen(true)}
          title="Configure Model"
        >
          ⚙️
        </button>
        <p className="subtitle">Reinforcement Learning Environment</p>
        <div className="rl-flow">
          <span className="flow-item">STATE (Question)</span>
          <span className="arrow">→</span>
          <span className="flow-item">ACTION (Answer)</span>
          <span className="arrow">→</span>
          <span className="flow-item">REWARD (Score)</span>
          <span className="arrow">→</span>
          <span className="flow-item">NEXT STATE</span>
        </div>
      </header>

      <SettingsModal 
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSave={() => {
          // Optional: Refresh or show success message
          alert('✅ Model configuration updated!');
        }}
      />

      <div className="container">
        <div className="controls">
          <button 
            onClick={getQuestion} 
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? '⏳ Loading...' : '🎯 Get New Question'}
          </button>
          
          <button 
            onClick={generateAnswer} 
            disabled={loading || !question}
            className="btn btn-success"
          >
            {loading ? '🤔 Thinking...' : '🤖 Generate AI Answer'}
          </button>
        </div>

        {question && (
          <QuestionCard 
            question={question} 
            difficulty={difficulty}
          />
        )}

        {episodeData && (
          <div className="episode-container">
            <h3>📊 Episode Results</h3>
            
            <div className="attempt-section">
              <h4>Attempt 1:</h4>
              <p className="answer-text">{episodeData.attempt_1.answer}</p>
              <ScoreDisplay 
                score={episodeData.attempt_1.score}
                reward={episodeData.attempt_1.reward}
                feedback={episodeData.attempt_1.feedback}
              />
            </div>

            {episodeData.attempt_2 && (
              <div className="attempt-section retry">
                <h4>🔄 Attempt 2 (Retry with Feedback):</h4>
                <p className="answer-text">{episodeData.attempt_2.answer}</p>
                <ScoreDisplay 
                  score={episodeData.attempt_2.score}
                  reward={episodeData.attempt_2.reward}
                  feedback={episodeData.attempt_2.feedback}
                />
                <div className="improvement">
                  <strong>Improvement: </strong>
                  <span className={episodeData.improvement > 0 ? 'positive' : 'negative'}>
                    {episodeData.improvement > 0 ? '↑' : '↓'} 
                    {(episodeData.improvement * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            )}
          </div>
        )}

        {!episodeData && question && (
          <AnswerBox 
            answer={answer}
            setAnswer={setAnswer}
            onSubmit={submitAnswer}
            disabled={loading}
          />
        )}

        {result && !episodeData && (
          <ScoreDisplay 
            score={result.score}
            reward={result.reward}
            feedback={result.feedback}
          />
        )}

        {rewardHistory.length > 0 && (
          <div className="history-section">
            <h3>📈 Reward History</h3>
            <div className="reward-graph">
              {rewardHistory.map((reward, index) => (
                <div key={index} className="reward-bar-container">
                  <div 
                    className={`reward-bar ${reward >= 5 ? 'positive' : reward < 0 ? 'negative' : 'neutral'}`}
                    style={{
                      height: `${Math.abs(reward) * 10 + 20}px`
                    }}
                  >
                    <span className="reward-value">{reward}</span>
                  </div>
                  <span className="episode-number">E{index + 1}</span>
                </div>
              ))}
            </div>
            <div className="stats">
              <div>Total Episodes: {rewardHistory.length}</div>
              <div>Avg Reward: {(rewardHistory.reduce((a, b) => a + b, 0) / rewardHistory.length).toFixed(2)}</div>
            </div>
          </div>
        )}
      </div>

      <footer className="footer">
        <p>Built with RL principles: Environment + Agent + Reward System</p>
      </footer>
    </div>
  );
}

export default App;
