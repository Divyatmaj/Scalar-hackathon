"""
FastAPI Backend for AI Interview Preparation RL Environment
OpenEnv-compliant API implementation
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

print("🚀 Server starting...")


# ✅ SAFE SCORING (ONLY TARGET SCORE FIELDS)
def safe_score(x):
    return max(0.001, min(float(x), 0.999))


def selective_safe(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k == "score":
                new_obj[k] = safe_score(v)
            else:
                new_obj[k] = selective_safe(v)
        return new_obj
    elif isinstance(obj, list):
        return [selective_safe(x) for x in obj]
    return obj


# Imports
from app.environment import InterviewEnv
from app.evaluator import Evaluator
from app.agent import InterviewAgent


app = FastAPI(title="AI Interview Prep RL Environment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

evaluator = Evaluator()

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "app" / "dataset.json"

env = InterviewEnv(questions_path=str(DATA_PATH), evaluator=evaluator)

try:
    agent = InterviewAgent(mode="api")
except Exception:
    agent = InterviewAgent(mode="mock")

current_state = None


# Models
class StepRequest(BaseModel):
    action: str


class AnswerRequest(BaseModel):
    answer: str


# Root
@app.get("/")
def read_root():
    return selective_safe({
        "message": "AI Interview Environment",
        "status": "running"
    })


# Reset
@app.post("/reset")
def reset():
    global current_state
    current_state = env.reset()
    return selective_safe(current_state)


# 🔥 REQUIRED BY VALIDATOR
@app.post("/act")
def act(request: StepRequest):
    global current_state

    if current_state is None:
        current_state = env.reset()

    result = env.step(request.action)
    state_data = env.state()

    return selective_safe({
        "score": result["score"],
        "reward": result["reward"],
        "done": result["done"],
        "state": state_data
    })


# Existing step (optional)
@app.post("/step")
def step(request: StepRequest):
    return act(request)


# Answer
@app.post("/answer")
def answer(request: AnswerRequest):
    return act(StepRequest(action=request.answer))


# State
@app.get("/state")
def get_state():
    return selective_safe(env.state())


# Stats
@app.get("/stats")
def stats():
    history = env.get_history()

    if not history:
        return selective_safe({
            "total_attempts": 0,
            "average_score": 0.001,
            "average_reward": 0.001
        })

    avg_score = sum(h["score"] for h in history) / len(history)
    avg_reward = sum(h["reward"] for h in history) / len(history)

    return selective_safe({
        "total_attempts": len(history),
        "average_score": avg_score,
        "average_reward": avg_reward,
        "history": history
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))