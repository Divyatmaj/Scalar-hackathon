# AI Interview Preparation Environment - Complete Documentation

## 📋 Table of Contents
1. [Architecture](#architecture)
2. [Core Components](#core-components)
3. [Features](#features)
4. [API Reference](#api-reference)
5. [Development Guide](#development-guide)
6. [Extension Points](#extension-points)

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                   FRONTEND (React)                       │
│         User Interface + Model Configuration             │
└─────────────────────────────────────────────────────────┘
                          ↕ REST API
┌─────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                       │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Environment   │  │  Evaluator   │  │    Agent     │ │
│  │  (RL Logic)   │  │  (Scoring)   │  │  (LLM API)   │ │
│  └───────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Backend**: Python 3.8+, FastAPI, Pydantic
- **Frontend**: React, Vite, Axios
- **LLM**: HuggingFace (OpenAI-compatible API)
- **Evaluation**: Hybrid (Keyword + AI scoring)

---

## Core Components

### 1. Environment (`app/environment.py`)

**Purpose**: Implements OpenAI Gym-style RL environment

**Key Methods**:
- `reset()` → Returns new question state
- `step(action)` → Evaluates answer, returns reward
- `get_history()` → Returns episode attempts
- `should_retry(reward)` → Determines if retry needed

**State Representation**:
```python
{
    "question": str,
    "keywords": List[str],
    "difficulty": str,
    "attempt": int
}
```

**Step Output**:
```python
{
    "reward": int,           # +10, +5, 0, -5
    "score": float,          # 0.0 to 1.0
    "feedback": str,
    "matched_keywords": List[str],
    "missing_keywords": List[str],
    "done": bool
}
```

### 2. Evaluator (`app/evaluator.py`)

**Purpose**: Hybrid scoring system (keyword + AI)

**Scoring Formula**:
```python
final_score = (0.7 × keyword_score) + (0.3 × ai_score)
```

**Keyword Evaluation**:
- Text normalization (lowercase, punctuation removal)
- Substring matching for flexibility
- Proportional scoring: matched / total

**Reward Structure**:
| Score | Reward | Meaning |
|-------|--------|---------|
| ≥ 80% | +10 | Excellent |
| ≥ 50% | +5 | Good |
| ≥ 30% | 0 | Needs improvement |
| < 30% | -5 | Poor |

**Feedback Format**:
- ✅ "Covered: X, Y, Z"
- ⚠️ "Consider adding: A, B"
- ❌ "Missing: P, Q, R"

### 3. Agent (`app/agent.py`)

**Purpose**: LLM-powered agent with retry mechanism

**Modes**:
- `api`: Real HuggingFace LLM integration
- `mock`: Simulated answers for testing

**Key Features**:
- **Memory System**: Tracks all attempts
- **Retry Logic**: Improves using feedback
- **Prompt Engineering**: Different prompts for initial vs retry

**API Integration**:
```python
# Uses OpenAI-compatible HuggingFace API
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)
```

**Retry Strategy**:
1. Initial attempt generates base answer
2. If score < threshold, receives feedback
3. Constructs improved prompt with missing keywords
4. Generates enhanced answer
5. Repeat up to max_retries (default: 3)

---

## Features

### 1. Keyword-Based Scoring

**Problem**: Binary rewards don't show progress

**Solution**: Proportional scoring
```python
score = len(matched_keywords) / len(total_keywords)
```

**Example**:
```
Question: "What is binary search?"
Keywords: ["sorted array", "divide", "O(log n)", "logarithmic"]
Answer: "Binary search divides a sorted array..."
→ Matched: ["sorted array", "divide"]
→ Missing: ["O(log n)", "logarithmic"]
→ Score: 50% (2/4)
```

### 2. Structured Feedback

**Benefits**:
- Agent knows what to add
- User sees clear gaps
- Systematic improvement

**Format**:
```
⚠️ Partial answer. Covered 2/4 concepts.
   ✓ Covered: sorted array, divide
   ✗ Missing: O(log n), logarithmic
```

### 3. Retry Mechanism

**Flow**:
```
Attempt 1: Partial answer (50%) 
    → Feedback: "Missing: O(log n), logarithmic"
Attempt 2: Improved answer (90%)
    → Success!
```

**Implementation**:
- Agent remembers previous feedback
- Prompt explicitly asks for missing concepts
- Max 3 retries to avoid infinite loops

### 4. Memory System

**Two Levels**:
- **Episode Memory**: Current question attempts
- **Global Memory**: All questions across sessions

**Statistics Tracked**:
- Total attempts
- Average score
- Improvement rate
- Retry count

### 5. Hybrid Evaluation

**Why Hybrid?**
- Keywords: Fast, deterministic, explainable
- AI scoring: Semantic understanding (future)

**Current Implementation**:
- Keyword: 70% weight (implemented)
- AI: 30% weight (placeholder for LLM-as-judge)

**Future Extension**:
```python
def evaluate_ai(answer, question):
    # Call GPT-4/Claude to judge quality
    response = llm.judge(question, answer)
    return score  # 0.0 to 1.0
```

### 6. Dynamic Configuration

**UI-Based**:
- Click ⚙️ button
- Enter HuggingFace token
- Select model
- Changes apply immediately

**API-Based**:
```bash
curl -X POST http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "hf_...",
    "model": "Qwen/Qwen3-Coder-Next:novita"
  }'
```

---

## API Reference

### Endpoints

#### GET /question
Get new random question

**Response**:
```json
{
  "status": "success",
  "state": {
    "question": "What is binary search?",
    "keywords": ["sorted", "divide", "O(log n)"],
    "difficulty": "easy"
  }
}
```

#### POST /answer
Submit answer for evaluation

**Request**:
```json
{
  "answer": "Binary search divides a sorted array..."
}
```

**Response**:
```json
{
  "status": "success",
  "result": {
    "reward": 5,
    "score": 0.65,
    "feedback": "Good answer. Consider adding: O(log n)",
    "matched_keywords": ["sorted", "divide"],
    "missing_keywords": ["O(log n)"],
    "done": false
  }
}
```

#### POST /auto-run
Auto-generate answer with retry

**Request**:
```json
{
  "use_retry": true
}
```

**Response**:
```json
{
  "status": "success",
  "episode": {
    "question": "...",
    "attempt_1": {
      "answer": "...",
      "score": 0.5,
      "reward": 5
    },
    "attempt_2": {
      "answer": "...",
      "score": 0.9,
      "reward": 10
    },
    "improvement": 0.4
  }
}
```

#### GET /config
Get current configuration

**Response**:
```json
{
  "status": "success",
  "config": {
    "model": "Qwen/Qwen3-Coder-Next:novita",
    "api_key_set": true,
    "client_initialized": true
  }
}
```

#### POST /config
Update configuration

**Request**:
```json
{
  "api_key": "hf_...",
  "model": "meta-llama/Llama-3.3-70B-Instruct"
}
```

#### GET /stats
Get episode statistics

**Response**:
```json
{
  "status": "success",
  "stats": {
    "total_attempts": 5,
    "average_score": 0.72,
    "average_reward": 6.5,
    "history": [...]
  }
}
```

---

## Development Guide

### Setup Development Environment

```bash
# Clone repository
git clone <repo-url>
cd ai-interview-env

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install

# Environment variables
echo "HF_TOKEN=your_token_here" > backend/.env
```

### Run in Development Mode

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Add New Questions

Edit `backend/app/dataset.json`:
```json
{
  "question": "Explain the CAP theorem.",
  "keywords": ["consistency", "availability", "partition tolerance"],
  "difficulty": "hard"
}
```

### Customize Evaluation

Adjust scoring weights in `backend/app/evaluator.py`:
```python
evaluator = Evaluator(
    keyword_weight=0.8,  # 80% keyword-based
    ai_weight=0.2        # 20% AI-based
)
```

### Modify Retry Behavior

In `backend/app/environment.py`:
```python
env.set_max_retries(5)  # Allow 5 attempts
```

In `backend/app/environment.py` (should_retry method):
```python
def should_retry(self, reward: int) -> bool:
    return reward < 10  # Retry until perfect score
```

---

## Extension Points

### 1. Add Real AI Scoring

In `app/evaluator.py`, replace `evaluate_ai()`:
```python
def evaluate_ai(self, answer: str, question: str = None) -> float:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "system",
            "content": "Rate this interview answer 0-10"
        }, {
            "role": "user",
            "content": f"Q: {question}\nA: {answer}"
        }]
    )
    return float(response.choices[0].message.content) / 10.0
```

### 2. Add Difficulty Progression

```python
class InterviewEnv:
    def select_next_question(self):
        if self.get_stats()["best_score"] > 0.8:
            return self.get_question(difficulty="hard")
        else:
            return self.get_question(difficulty="easy")
```

### 3. Add Multi-Turn Episodes

```python
# In main.py
max_questions_per_episode = 5
for i in range(max_questions_per_episode):
    state = env.reset()
    # ... answer question ...
```

### 4. Add User Profiles

```python
# Track per-user progress
class UserProfile:
    def __init__(self, user_id):
        self.user_id = user_id
        self.history = []
        self.weak_areas = []
    
    def update_from_episode(self, episode_data):
        # Identify weak keyword areas
        # Recommend focused practice
```

### 5. Add Voice Interface

```python
# Frontend integration with Web Speech API
const recognition = new webkitSpeechRecognition();
recognition.onresult = (event) => {
    const answer = event.results[0][0].transcript;
    submitAnswer(answer);
};
```

---

## Troubleshooting

### Backend Won't Start

```bash
# Check dependencies
pip install -r requirements.txt

# Check port availability
lsof -i :8000

# Check environment variables
python -c "import os; print(os.getenv('HF_TOKEN'))"
```

### Frontend Won't Connect

1. Verify backend is running on port 8000
2. Check CORS settings in `main.py`
3. Verify API_URL in frontend `App.jsx`

### LLM Not Working

1. Verify HF_TOKEN is set correctly
2. Check HuggingFace API status
3. Try mock mode: `agent = InterviewAgent(mode="mock")`
4. Check API quota and rate limits

### Low Scores

1. Add more specific keywords to dataset
2. Adjust keyword matching in evaluator
3. Lower retry threshold
4. Use better LLM model

---

## Performance Optimization

### Caching

```python
# Cache LLM responses
from functools import lru_cache

@lru_cache(maxsize=100)
def get_llm_response(question, prompt_hash):
    return agent.generate_answer(question)
```

### Async Processing

```python
# Use async for parallel evaluation
async def evaluate_multiple_answers(answers):
    tasks = [evaluator.evaluate(a, keywords) for a in answers]
    return await asyncio.gather(*tasks)
```

### Database Integration

```python
# Store questions and results in database
from sqlalchemy import create_engine

engine = create_engine('postgresql://...')
# Store episodes, track long-term progress
```

---

## Security Considerations

### API Keys
- ✅ Store in environment variables
- ✅ Never commit to git (.gitignore)
- ✅ Use .env file for local development
- ⚠️ Rotate keys regularly
- ⚠️ Use key management service in production

### CORS
```python
# Production: Specify exact origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.get("/question")
@limiter.limit("10/minute")
def get_question():
    ...
```

---

## Deployment

### Docker

```dockerfile
# backend/Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Environment Variables

Production:
```bash
HF_TOKEN=prod_token_here
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
CORS_ORIGINS=https://yourdomain.com
```

### Monitoring

```python
# Add logging
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/question")
def get_question():
    logger.info("Question requested")
    ...
```

---

## Contributing

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings
- Add comments for complex logic

### Testing
```bash
# Run tests
pytest

# Coverage
pytest --cov=app
```

### Pull Requests
1. Create feature branch
2. Write tests
3. Update documentation
4. Submit PR with description

---

## License

MIT License - Free for educational and commercial use.

---

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review API reference

---

**Last Updated**: April 2026
**Version**: 2.0.0
