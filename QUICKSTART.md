# 🎯 QUICK START GUIDE

## For Judges and Quick Demo

### 1️⃣ Install & Run (5 minutes)

```bash
# Clone/Navigate to project
cd hackathon

# Option A: Automated Setup (Recommended)
./setup.sh

# Option B: Manual Setup
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend (in new terminal)
cd frontend
npm install
```

### 2️⃣ Start Application

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py
# Server running on http://localhost:8000

# Terminal 2: Frontend
cd frontend
npm run dev
# App running on http://localhost:3000
```

### 3️⃣ Demo Flow (2 minutes)

1. Open http://localhost:3000
2. Click **"Get New Question"** → See the STATE
3. Click **"Generate AI Answer"** → See ACTION & REWARD
4. Watch the RL loop complete with feedback!

---

## 🎯 What This Demonstrates

### Core RL Loop
```
┌─────────────┐
│   RESET()   │  → Returns STATE (question)
└─────────────┘
       ↓
┌─────────────┐
│ AGENT Acts  │  → Generates ACTION (answer)
└─────────────┘
       ↓
┌─────────────┐
│   STEP()    │  → Returns REWARD (score)
└─────────────┘
       ↓
┌─────────────┐
│  EVALUATE   │  → Feedback for improvement
└─────────────┘
       ↓
┌─────────────┐
│   RETRY?    │  → If low reward, improve and retry
└─────────────┘
```

### Key Features to Show
1. **Environment Design** - Clean `reset()` and `step()` methods
2. **Reward System** - Score-based rewards (+10, +5, 0, -5)
3. **Feedback Loop** - Agent improves based on feedback
4. **Visual Demo** - Beautiful UI showing entire RL process

---

## 📊 Architecture

```
┌──────────────────────────────────────────────────────┐
│              FRONTEND (React + Vite)                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │ Question   │  │  Answer    │  │   Score    │    │
│  │   Card     │  │    Box     │  │  Display   │    │
│  └────────────┘  └────────────┘  └────────────┘    │
└──────────────────────────────────────────────────────┘
                      ↕ REST API
┌──────────────────────────────────────────────────────┐
│              BACKEND (FastAPI)                        │
│  ┌─────────────────────────────────────────────┐    │
│  │  GET  /question     → env.reset()           │    │
│  │  POST /answer       → env.step(action)      │    │
│  │  POST /auto-run     → Full RL episode       │    │
│  │  GET  /stats        → Episode statistics    │    │
│  └─────────────────────────────────────────────┘    │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ InterviewEnv │  │  LLM Agent   │  │Evaluator │  │
│  │              │  │              │  │          │  │
│  │ • reset()    │  │ • generate() │  │• eval()  │  │
│  │ • step()     │  │ • retry()    │  │• reward()│  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## 🧪 Test Before Demo

```bash
cd backend
source venv/bin/activate
python test_env.py

# Should show:
# ✅ Components initialized
# ✅ Reset successful
# ✅ Evaluation successful
# ✅ AI generation successful
# ✅ Retry successful
```

---

## 🎤 Pitch Points

### Problem
Technical interview preparation lacks:
- Immediate feedback
- Adaptive difficulty
- Structured learning loop

### Solution
RL-based environment that:
- Provides instant evaluation
- Learns from feedback
- Follows proven RL framework

### Innovation
1. **Not traditional ML training** - Focus on environment design
2. **Retry mechanism** - Agent improves with feedback
3. **Full-stack demo** - Working product, not just theory
4. **Extensible** - Easy to add features

### Tech Highlights
- Clean RL abstraction (Gym-style)
- Production-quality code
- Modular architecture
- Real LLM integration

---

## 🚀 5-Minute Demo Script

**[Minute 1]** Show problem
- "Interview prep is hard without feedback"
- "Traditional study is passive"

**[Minute 2]** Explain RL approach
- Show diagram: STATE → ACTION → REWARD
- "We built an environment, not a training loop"

**[Minute 3]** Live demo
- Get question (RESET)
- Generate answer (ACTION)
- See reward (STEP)
- Watch retry if low score

**[Minute 4]** Show code
- `interview_env.py` - Clean RL interface
- `evaluator.py` - Reward logic
- API endpoints

**[Minute 5]** Extensions & Q&A
- Multi-turn episodes
- LLM judge
- Mobile app
- Questions?

---

## 📁 Project Stats

- **Files:** 20+
- **Lines of Code:** ~1500+
- **Components:** 3 backend modules, 3 frontend components
- **API Endpoints:** 4
- **Questions:** 12 (DSA, OS, DB, OOP)
- **Test Coverage:** Core functionality

---

## 🔑 Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `backend/env/interview_env.py` | RL Environment | 118 |
| `backend/evaluator/evaluator.py` | Scoring Engine | 95 |
| `backend/agent/llm_agent.py` | LLM Agent | 104 |
| `backend/main.py` | FastAPI Server | 167 |
| `frontend/src/App.jsx` | Main UI | 187 |

---

## 💡 Extension Ideas (Post-Hackathon)

### Easy (1-2 hours)
- [ ] Add difficulty filter
- [ ] Export results to PDF
- [ ] More questions

### Medium (1 day)
- [ ] User authentication
- [ ] Database integration
- [ ] Progress tracking
- [ ] Leaderboard

### Advanced (1 week)
- [ ] Multi-turn episodes
- [ ] GPT-4 as judge
- [ ] Voice interface
- [ ] Mobile app
- [ ] Curriculum learning

---

## ❓ FAQ

**Q: Does it need OpenAI API key?**
A: No! Works with mock answers for demo. Real API is optional.

**Q: Can I add my own questions?**
A: Yes! Edit `backend/data/questions.json`

**Q: What if I get CORS errors?**
A: Make sure backend is on port 8000, frontend on 3000

**Q: Can I change the reward logic?**
A: Yes! Edit `compute_reward()` in `evaluator.py`

**Q: Is this actual RL training?**
A: No - it's an RL environment. No neural network training involved.

---

## 📞 Troubleshooting

### Backend won't start
```bash
# Check port 8000
lsof -i :8000

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend errors
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

### API connection fails
- Ensure backend is running
- Check URLs match (localhost:8000, localhost:3000)
- Verify CORS is enabled

---

## ✅ Pre-Demo Checklist

- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Test script passes (`python test_env.py`)
- [ ] Backend starts without errors
- [ ] Frontend loads in browser
- [ ] Can get question
- [ ] Can generate answer
- [ ] Retry mechanism works
- [ ] UI is responsive

---

**Ready to impress! 🎉**

For full documentation, see [README.md](README.md)  
For technical details, see [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
