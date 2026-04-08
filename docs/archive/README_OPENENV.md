# AI Interview Preparation - OpenEnv Compliant RL Environment

**OpenEnv Hackathon Submission**

A production-ready Reinforcement Learning environment for technical interview preparation with intelligent feedback, deterministic grading, and full OpenEnv compliance.

## 🚀 Quick Start

### Docker (Recommended)
```bash
docker build -t ai-interview-env .
docker run -p 8000:8000 -e HF_TOKEN=your_token ai-interview-env
```

### Local
```bash
cd backend
pip install -r requirements.txt
python3 main.py
```

### Run Inference
```bash
python3 inference.py
```

## 📋 OpenEnv Compliance

✅ **All requirements met**:
- openenv.yaml specification
- /reset, /step, /state endpoints
- Deterministic grading (no randomness)
- Rewards in [0.0, 1.0] range
- 12 tasks (≥3 required)
- Exact [START]/[STEP]/[END] logging
- Docker containerization
- Environment variable support

## 🎯 Key Features

- **12 Technical Interview Questions**: Covering algorithms, systems, databases, OOP
- **Deterministic Grading**: Keyword matching (80%) + length scoring (20%)
- **OpenEnv API**: POST /reset, POST /step, GET /state
- **Reward Range**: Always 0.0 to 1.0
- **Docker Ready**: Single command deployment
- **Environment Variables**: API_BASE_URL, MODEL_NAME, HF_TOKEN

## 📚 API Endpoints

### POST /reset
Reset environment and get new question
```json
Response:
{
  "question": "What is binary search?",
  "difficulty": "easy",
  "attempt": 0
}
```

### POST /step
Submit answer for evaluation
```json
Request:
{
  "action": "Binary search divides a sorted array..."
}

Response:
{
  "reward": 0.75,
  "done": false,
  "state": {
    "question": "...",
    "difficulty": "easy",
    "attempt": 1
  }
}
```

### GET /state
Get current environment state
```json
Response:
{
  "question": "...",
  "difficulty": "easy",
  "attempt": 1
}
```

## 🔧 Environment Variables

```bash
API_BASE_URL=https://router.huggingface.co/v1  # LLM API endpoint
MODEL_NAME=Qwen/Qwen3-Coder-Next:novita         # Model identifier
HF_TOKEN=your_token_here                        # Optional, uses mock if not set
```

## 📊 Tasks

12 technical interview questions:
1. Binary search and time complexity
2. Process vs thread
3. Database normalization
4. OOP pillars
5. Deadlock prevention
6. HashMap internals
7. SQL vs NoSQL
8. SOLID principles
9. Stack vs heap memory
10. RESTful APIs
11. Big O notation
12. CAP theorem

## 🧪 Testing

```bash
# Test determinism
python3 -c "
import sys; sys.path.insert(0, 'backend')
from app.evaluator import Evaluator
e = Evaluator()
for i in range(3):
    print(f'Run {i+1}:', e.evaluate('test', ['a'])['score'])
"

# Test inference
python3 inference.py | head -20

# Test API
curl -X POST http://localhost:8000/reset
curl -X POST http://localhost:8000/step -H "Content-Type: application/json" -d '{"action":"test"}'
curl http://localhost:8000/state
```

## 📁 File Structure

```
.
├── openenv.yaml           # OpenEnv specification
├── inference.py           # Inference script with exact logging
├── Dockerfile             # Container configuration
├── backend/
│   ├── app/
│   │   ├── environment.py # RL environment (reset, step, state)
│   │   ├── evaluator.py   # Deterministic grading
│   │   ├── agent.py       # LLM agent
│   │   └── dataset.json   # 12 tasks
│   └── main.py            # FastAPI server
└── frontend/              # React UI (optional)
```

## ✅ Validation

See `OPENENV_VALIDATION.md` for complete validation guide.

Quick check:
```bash
# All should pass
python3 inference.py >/dev/null && echo "✅ Inference works"
docker build -t test . && echo "✅ Docker builds"
curl -X POST http://localhost:8000/reset | grep question && echo "✅ API works"
```

## 📄 License

MIT License - Free for educational and commercial use

## 🙏 Credits

Built for OpenEnv Hackathon 2026
- FastAPI backend
- React frontend  
- HuggingFace LLM integration
- Deterministic keyword-based evaluation
