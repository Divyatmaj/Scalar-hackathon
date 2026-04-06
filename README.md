# AI Interview Preparation Environment (RL System)

🎯 **A Hackathon-Ready Reinforcement Learning Environment for Interview Practice**

This project implements a complete RL system that simulates technical interview preparation where an AI agent learns to answer interview questions through reward-based feedback.

---

## 🧠 Core Concept

This follows strict **Reinforcement Learning principles**:

```
STATE (Question) → ACTION (Answer) → REWARD (Score) → NEXT STATE
```

**NOT a traditional ML training project** - Focus is on:
- ✅ Environment Design
- ✅ Reward System
- ✅ Evaluation Loop
- ✅ Agent-Environment Interaction

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                     │
│              User Interface + Visualization              │
└─────────────────────────────────────────────────────────┘
                            ↕ REST API
┌─────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                      │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ InterviewEnv  │  │  LLM Agent   │  │  Evaluator   │ │
│  │  (RL Logic)   │  │  (OpenAI)    │  │  (Scoring)   │ │
│  └───────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Components

1. **InterviewEnv** - Core RL environment class
   - `reset()`: Returns new question (state)
   - `step(action)`: Evaluates answer and returns reward

2. **LLM Agent** - AI that generates answers
   - Uses OpenAI API or mock answers
   - Can improve based on feedback (retry loop)

3. **Evaluator** - Scoring engine
   - Keyword-based evaluation
   - Feedback generation
   - Reward computation

4. **Frontend** - Interactive UI
   - Question display
   - Answer submission
   - Score visualization
   - Reward history graph

---

## 📂 Project Structure

```
hackathon/
├── backend/
│   ├── main.py                  # FastAPI server
│   ├── requirements.txt
│   ├── env/
│   │   └── interview_env.py     # RL Environment class
│   ├── evaluator/
│   │   └── evaluator.py         # Evaluation engine
│   ├── agent/
│   │   └── llm_agent.py         # LLM agent
│   └── data/
│       └── questions.json       # Interview questions dataset
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx              # Main app component
│       ├── App.css
│       └── components/
│           ├── QuestionCard.jsx
│           ├── AnswerBox.jsx
│           └── ScoreDisplay.jsx
│
└── README.md
```

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API Key (optional - works with mock answers)

### Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"  # On Windows: set OPENAI_API_KEY=...

# Run the server
python main.py
```

Backend will run on: **http://localhost:8000**

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run on: **http://localhost:3000**

---

## 🎮 How to Use

### Demo Flow

1. **Open the app** at http://localhost:3000

2. **Click "Get New Question"**
   - Environment calls `reset()`
   - Random question selected
   - State returned to UI

3. **Click "Generate AI Answer"**
   - Agent generates answer using LLM
   - Environment evaluates via `step(action)`
   - Reward calculated and displayed
   - If reward < 5, automatic retry with feedback

4. **View Results**
   - See AI answer
   - Score (0-100%)
   - Reward (+10, +5, 0, -5)
   - Detailed feedback
   - Improvement metrics (if retried)

5. **Track Progress**
   - Reward history graph
   - Episode statistics

### Manual Mode

You can also manually type answers:
- Get a question
- Type your answer in the textbox
- Click "Submit Answer"

---

## 🧪 RL Components Explained

### State

```json
{
  "question": "What is a binary search?",
  "keywords": ["sorted array", "divide", "logarithmic"],
  "difficulty": "easy"
}
```

### Action

```
"Binary search is an algorithm that finds items in a sorted array 
by repeatedly dividing the search interval in half..."
```

### Reward Structure

| Score Range | Reward | Meaning |
|-------------|--------|---------|
| ≥ 80% | +10 | Excellent answer |
| ≥ 50% | +5 | Good answer |
| ≥ 30% | 0 | Needs improvement |
| < 30% | -5 | Poor answer |

### Evaluation Logic

```python
1. Normalize text (lowercase, remove punctuation)
2. Check keyword matches
3. Score = matched_keywords / total_keywords
4. Generate feedback based on missing concepts
5. Compute reward from score
```

---

## 🔁 Retry Mechanism (Key RL Feature)

When reward < 5:

```
1. Send feedback to agent: "Missing key concepts: X, Y, Z"
2. Agent generates IMPROVED answer
3. Re-evaluate new answer
4. Compare improvement
```

This simulates **learning through feedback** - a core RL concept!

---

## 📊 API Endpoints

### `GET /question`
Reset environment and get new question

**Response:**
```json
{
  "status": "success",
  "state": {
    "question": "...",
    "keywords": [...],
    "difficulty": "medium"
  }
}
```

### `POST /answer`
Submit answer for evaluation

**Request:**
```json
{
  "answer": "Your answer here..."
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "reward": 5,
    "score": 0.6,
    "feedback": "Good answer. Consider adding: ...",
    "done": true
  }
}
```

### `POST /auto-run`
Automatic RL episode (agent generates answer)

**Request:**
```json
{
  "use_retry": true
}
```

**Response:**
```json
{
  "status": "success",
  "episode": {
    "question": "...",
    "attempt_1": { ... },
    "attempt_2": { ... },  // If retry occurred
    "improvement": 0.25
  }
}
```

### `GET /stats`
Get episode statistics

---

## 🎯 Dataset

12 technical interview questions covering:
- **Data Structures & Algorithms** (Binary Search, Big O, HashMap)
- **Operating Systems** (Process vs Thread, Deadlock, Memory)
- **Databases** (SQL vs NoSQL, Normalization, CAP Theorem)
- **Object-Oriented Programming** (OOP Pillars, SOLID)
- **System Design** (REST APIs)

Each question includes:
- Question text
- Expected keywords
- Difficulty level (easy/medium/hard)

---

## 🔧 Configuration

### Using Different LLM Models

Edit `backend/agent/llm_agent.py`:

```python
# Use GPT-4
agent = LLMAgent(model="gpt-4")

# Or use HuggingFace
# Modify generate_answer() to use HF inference API
```

### Adding More Questions

Edit `backend/data/questions.json`:

```json
{
  "question": "Your question here?",
  "keywords": ["concept1", "concept2", "concept3"],
  "difficulty": "medium"
}
```

### Adjusting Reward Function

Edit `backend/evaluator/evaluator.py`:

```python
def compute_reward(self, score: float) -> int:
    # Customize your reward logic
    if score >= 0.9: return 15
    elif score >= 0.7: return 10
    # ...
```

---

## 🌟 Key Features

✅ **Clean RL Architecture** - Proper separation of Environment, Agent, Evaluator  
✅ **Gym-style Interface** - `reset()` and `step()` methods  
✅ **Reward-based Learning** - Clear reward signals for performance  
✅ **Automatic Retry Loop** - Agent improves based on feedback  
✅ **Full-Stack Demo** - Working frontend + backend  
✅ **Real LLM Integration** - OpenAI API support  
✅ **Mock Mode** - Works without API key for testing  
✅ **Visual Feedback** - Score graphs and metrics  
✅ **Modular Design** - Easy to extend and modify  

---

## 🧩 Extension Ideas

1. **Multi-turn Episodes**
   - Allow multiple questions per episode
   - Track cumulative rewards

2. **LLM-as-Judge**
   - Use GPT-4 for semantic evaluation
   - More nuanced scoring

3. **Difficulty Adaptation**
   - Adjust question difficulty based on performance
   - Curriculum learning

4. **User Profiles**
   - Save progress
   - Track improvement over time

5. **Voice Interface**
   - Speech-to-text for answers
   - Text-to-speech for questions

6. **Competitive Mode**
   - Leaderboards
   - Compare with other users

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is available
lsof -i :8000

# Install dependencies
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### CORS errors
- Make sure backend is running on port 8000
- Check CORS middleware in `main.py`

### OpenAI API errors
- Verify API key is set: `echo $OPENAI_API_KEY`
- Check API quota and billing
- Works with mock answers if no API key

---

## 📝 Technical Notes

### Why RL Structure?

This project demonstrates RL concepts WITHOUT traditional training:
- **Environment**: Provides states and computes rewards
- **Agent**: Takes actions (generates answers)
- **Policy**: Implicit in LLM behavior
- **Reward Signal**: Guides improvement

### Not Included (By Design)

❌ Neural network training  
❌ Gradient descent  
❌ Policy optimization  
❌ Value functions  

These are intentionally omitted to focus on environment design and evaluation.

---

## 🏆 Hackathon Tips

### Demo Presentation

1. **Show the RL loop visually** - Use the UI to demonstrate state→action→reward
2. **Highlight the retry mechanism** - Show how agent improves with feedback
3. **Explain the evaluation** - Show keyword matching and scoring
4. **Compare attempts** - Show improvement metrics
5. **Discuss extensibility** - Mention potential enhancements

### Key Talking Points

- "Clean separation of concerns"
- "Gym-style RL interface"
- "Reward-driven improvement"
- "Production-ready architecture"
- "Easy to extend and customize"

---

## 📜 License

MIT License - Free for hackathon and educational use

---

## 👥 Credits

Built for hackathon demonstration of RL principles in interview preparation.

**Tech Stack:**
- Backend: Python, FastAPI
- Frontend: React, Vite
- AI: OpenAI GPT-3.5
- Evaluation: Custom keyword-based engine

---

## 🚀 Quick Start (TL;DR)

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Open http://localhost:3000
# Click "Get New Question" → "Generate AI Answer"
```

**That's it! You have a working RL interview prep system! 🎉**
