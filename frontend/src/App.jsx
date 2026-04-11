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

  const clampOpenValue = (val) => {
    const numeric = Number(val);
    const safeNumeric = Number.isFinite(numeric) ? numeric : 0.1;
    return Math.min(0.9, Math.max(0.1, safeNumeric));
  };

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
      
      const finalAttempt = episode.attempt_2 || episode.attempt_1;
      setAnswer(finalAttempt.answer);
      setResult({
        reward: clampOpenValue(finalAttempt.reward),
        score: clampOpenValue(finalAttempt.score),
        feedback: finalAttempt.feedback
      });

      setRewardHistory([...rewardHistory, clampOpenValue(finalAttempt.reward)]);
      
    } catch (error) {
      console.error('Error generating answer:', error);
      const detail = error?.response?.data?.detail;
      alert(detail ? `Failed to generate answer: ${detail}` : 'Failed to generate answer.');
    } finally {
      setLoading(false);
    }
  };

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

      setRewardHistory([...rewardHistory, clampOpenValue(response.data.result.reward)]);
      
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
        >
          ⚙️
        </button>
        <p className="subtitle">Reinforcement Learning Environment</p>
      </header>

      <SettingsModal 
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSave={() => alert('✅ Model configuration updated!')}
      />

      <div className="container">
        <div className="controls">
          <button onClick={getQuestion} disabled={loading} className="btn btn-primary">
            {loading ? '⏳ Loading...' : '🎯 Get New Question'}
          </button>
          
          <button onClick={generateAnswer} disabled={loading || !question} className="btn btn-success">
            {loading ? '🤔 Thinking...' : '🤖 Generate AI Answer'}
          </button>
        </div>

        {question && <QuestionCard question={question} difficulty={difficulty} />}

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
                <h4>🔄 Attempt 2:</h4>
                <p className="answer-text">{episodeData.attempt_2.answer}</p>
                <ScoreDisplay 
                  score={episodeData.attempt_2.score}
                  reward={episodeData.attempt_2.reward}
                  feedback={episodeData.attempt_2.feedback}
                />
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
                    className={`reward-bar ${reward >= 0.7 ? 'positive' : reward <= 0.3 ? 'negative' : 'neutral'}`}
                    style={{ height: `${reward * 100}px` }}
                  >
                    {/* 🔥 FIX HERE */}
                    <span className="reward-value">{clampOpenValue(reward).toFixed(1)}</span>
                  </div>
                  <span className="episode-number">E{index + 1}</span>
                </div>
              ))}
            </div>

            {/* 🔥 FIX AVG */}
            <div className="stats">
              <div>Total Episodes: {rewardHistory.length}</div>
              <div>
                Avg Reward: {
                  clampOpenValue(
                    rewardHistory.reduce((a, b) => a + b, 0) / rewardHistory.length
                  ).toFixed(1)
                }
              </div>
            </div>
          </div>
        )}
      </div>

      <footer className="footer">
        <p>Built with RL principles</p>
      </footer>
    </div>
  );
}

export default App;
