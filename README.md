# AI Interview Preparation Environment

Production-ready RL system for technical interview practice with intelligent feedback and model configuration.

## 🚀 Quick Start

### Backend
```bash
cd backend
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Access the application at **http://localhost:3000**

## ⚙️ Configuration

### HuggingFace Model Setup

1. **Set API Token** (Option 1 - Environment):
   ```bash
   # Create backend/.env file
   echo "HF_TOKEN=your_huggingface_token_here" > backend/.env
   ```

2. **Set API Token** (Option 2 - UI):
   - Click ⚙️ button in top-right
   - Enter your HuggingFace API token
   - Select or enter model name
   - Save configuration

### Supported Models
- Qwen/Qwen3-Coder-Next:novita (default)
- meta-llama/Llama-3.3-70B-Instruct
- Qwen/Qwen2.5-72B-Instruct
- mistralai/Mixtral-8x7B-Instruct-v0.1
- Any HuggingFace model with inference API

## 📚 Features

- **Keyword-Based Scoring**: Proportional evaluation (not binary)
- **Structured Feedback**: Missing & matched keywords identified
- **Retry Mechanism**: Agent improves answers using feedback
- **Memory System**: Tracks attempts and improvement
- **Hybrid Evaluation**: Keyword (70%) + AI scoring (30%)
- **Dynamic Configuration**: Change models without restart
- **Beautiful UI**: React interface with real-time updates

## 📖 Documentation

See `docs/PROJECT.md` for:
- Complete architecture details
- API endpoints reference
- Development guide
- Extension points

## 🏗️ Project Structure

```
ai-interview-env/
├── backend/
│   ├── app/              # Core application
│   │   ├── agent.py      # LLM agent with retry
│   │   ├── environment.py # RL environment
│   │   ├── evaluator.py  # Hybrid scoring
│   │   └── dataset.json  # Questions
│   ├── main.py           # FastAPI server
│   └── requirements.txt
├── frontend/             # React application
└── docs/                 # Documentation
```

## 🛠️ Development

### Add Questions
Edit `backend/app/dataset.json`:
```json
{
  "question": "Your question?",
  "keywords": ["key1", "key2"],
  "difficulty": "medium"
}
```

### Run Tests
```bash
cd backend
pytest
```

### API Endpoints
- `GET /question` - Get new question
- `POST /answer` - Submit answer
- `POST /auto-run` - Auto-generate & improve
- `GET /config` - Get current config
- `POST /config` - Update API key/model
- `GET /stats` - Episode statistics

## 📄 License

MIT License - Free for educational and commercial use

## 🙏 Credits

Built with FastAPI, React, and HuggingFace models for AI interview preparation.
