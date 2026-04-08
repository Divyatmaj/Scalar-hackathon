import React, { useState, useEffect } from 'react';
import './SettingsModal.css';

const SettingsModal = ({ isOpen, onClose, onSave }) => {
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('Qwen/Qwen3-Coder-Next:novita');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  // Popular Hugging Face models
  const popularModels = [
    'Qwen/Qwen3-Coder-Next:novita',
    'meta-llama/Llama-3.3-70B-Instruct',
    'Qwen/Qwen2.5-72B-Instruct',
    'mistralai/Mixtral-8x7B-Instruct-v0.1',
    'microsoft/Phi-4',
    'google/gemma-2-9b-it',
  ];

  useEffect(() => {
    if (isOpen) {
      // Load current configuration when modal opens
      fetchCurrentConfig();
    }
  }, [isOpen]);

  const fetchCurrentConfig = async () => {
    try {
      const response = await fetch('http://localhost:8000/config');
      const data = await response.json();
      if (data.status === 'success') {
        setModel(data.config.model);
        // Don't set API key as it's not returned for security
      }
    } catch (error) {
      console.error('Error fetching config:', error);
    }
  };

  const handleSave = async () => {
    if (!apiKey.trim()) {
      alert('Please enter an API key');
      return;
    }

    setLoading(true);
    setStatus(null);

    try {
      const response = await fetch('http://localhost:8000/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: apiKey,
          model: model,
        }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        setStatus({ type: 'success', message: 'Configuration saved successfully!' });
        setTimeout(() => {
          onSave && onSave();
          onClose();
        }, 1500);
      } else {
        setStatus({ type: 'error', message: 'Failed to save configuration' });
      }
    } catch (error) {
      console.error('Error saving config:', error);
      setStatus({ type: 'error', message: 'Error connecting to backend' });
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>⚙️ Model Configuration</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <div className="form-group">
            <label htmlFor="apiKey">
              🔑 Hugging Face API Token
              <span className="required">*</span>
            </label>
            <input
              id="apiKey"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="hf_..."
              className="input-field"
            />
            <p className="helper-text">
              Get your token from{' '}
              <a 
                href="https://huggingface.co/settings/tokens" 
                target="_blank" 
                rel="noopener noreferrer"
              >
                huggingface.co/settings/tokens
              </a>
            </p>
          </div>

          <div className="form-group">
            <label htmlFor="model">
              🤖 Model / Inference Endpoint
            </label>
            <select
              id="model"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="input-field"
            >
              {popularModels.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            <p className="helper-text">
              Or enter a custom model name:
            </p>
            <input
              type="text"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              placeholder="owner/model-name:endpoint"
              className="input-field"
            />
          </div>

          {status && (
            <div className={`status-message ${status.type}`}>
              {status.message}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button 
            className="btn btn-secondary" 
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </button>
          <button 
            className="btn btn-primary" 
            onClick={handleSave}
            disabled={loading}
          >
            {loading ? '💾 Saving...' : '💾 Save Configuration'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;
