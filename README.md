# AI Interview Preparation Environment

Production-ready RL system for technical interview practice with intelligent feedback and OpenEnv compliance.

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
docker build -t ai-interview-env .
docker run -p 8000:8000 -e HF_TOKEN=your_token ai-interview-env
```

### Option 2: Local Development

**Backend:**
```bash
cd backend
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Access at **http://localhost:3000**

### Option 3: Run Inference (OpenEnv)
```bash
python3 inference.py
```

## ⚙️ Configuration

### Environment Variables
```bash
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen3-Coder-Next:novita
export HF_TOKEN=your_huggingface_token  # Optional, uses mock mode if not set
```

### UI Configuration
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

- **12 Technical Questions**: Algorithms, systems, databases, OOP, design patterns
- **Deterministic Grading**: Keyword matching (80%) + length scoring (20%)
- **Structured Feedback**: Missing & matched keywords identified
- **Retry Mechanism**: Agent improves answers using feedback
- **Memory System**: Tracks attempts and improvement
- **OpenEnv Compliant**: Full compliance with OpenEnv hackathon requirements
- **Dynamic Configuration**: Change models without restart
- **Beautiful UI**: React interface with real-time updates

## 🏗️ Project Structure

```
ai-interview-env/
├── openenv.yaml        # OpenEnv specification
├── inference.py        # Inference script
├── Dockerfile          # Container configuration
├── backend/
│   ├── app/
│   │   ├── agent.py      # LLM agent with retry
│   │   ├── environment.py # RL environment
│   │   ├── evaluator.py  # Deterministic scoring
│   │   └── dataset.json  # 12 questions
│   ├── main.py           # FastAPI server
│   └── requirements.txt
├── frontend/             # React application
└── docs/                 # Documentation
    ├── OPENENV.md        # OpenEnv compliance details
    └── PROJECT.md        # Full architecture guide
```

## 🔌 API Endpoints

### OpenEnv Endpoints
- `POST /reset` - Reset environment, get new question
- `POST /step` - Submit answer, get reward
- `GET /state` - Get current state

### Legacy Endpoints (for frontend)
- `GET /question` - Get new question
- `POST /answer` - Submit answer
- `POST /auto-run` - Auto-generate & improve
- `GET /config` - Get current config
- `POST /config` - Update API key/model
- `GET /stats` - Episode statistics

## ✅ OpenEnv Compliance

This project is fully compliant with OpenEnv hackathon requirements:
- ✅ openenv.yaml specification
- ✅ Deterministic grading (0.0-1.0 rewards)
- ✅ 12 tasks (≥3 required)
- ✅ Docker containerization
- ✅ /reset, /step, /state endpoints
- ✅ [START]/[STEP]/[END] logging in inference.py

See [docs/OPENENV.md](docs/OPENENV.md) for detailed compliance information.

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

### Test API Locally
```bash
# Start server
cd backend && python3 main.py

# Test in another terminal
curl -X POST http://localhost:8000/reset
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"action":"Binary search divides a sorted array"}'
curl http://localhost:8000/state
```

### Run Tests
```bash
cd backend
pytest
```

## 📖 Documentation

- **[docs/OPENENV.md](docs/OPENENV.md)** - OpenEnv compliance and validation
- **[docs/PROJECT.md](docs/PROJECT.md)** - Complete architecture details and development guide

## 📄 License

MIT License - Free for educational and commercial use

## 🙏 Credits

Built for OpenEnv Hackathon 2026 with FastAPI, React, and HuggingFace models.
