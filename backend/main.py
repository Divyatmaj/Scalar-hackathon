"""
FastAPI Backend for AI Interview Preparation RL Environment
OpenEnv-compliant API implementation
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🚀 Server starting...")

# ✅ SAFE SCORING (ONLY TARGET SCORE FIELDS)
def safe_score(x):
    return max(0.001, min(float(x), 0.999))


def selective_safe(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k in ["score", "reward", "ai_score", "keyword_score", "improvement", "average_score", "average_reward"]:
                new_obj[k] = safe_score(v)
            else:
                new_obj[k] = selective_safe(v)
        return new_obj
    elif isinstance(obj, list):
        return [selective_safe(x) for x in obj]
    return obj


# Import from app package
from backend.app.environment import InterviewEnv
from backend.app.evaluator import Evaluator
from backend.app.agent import InterviewAgent


# Initialize FastAPI app
app = FastAPI(title="AI Interview Prep RL Environment")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
evaluator = Evaluator()

# Resolve dataset path
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "app" / "dataset.json"

try:
    env = InterviewEnv(questions_path=str(DATA_PATH), evaluator=evaluator)
    if not env.questions:
        raise RuntimeError(f"Dataset loaded but 0 questions found at {DATA_PATH}")
except Exception as e:
    print(f"ENV INIT FAILED: {e}")
    raise

# Agent init
try:
    agent = InterviewAgent(mode="api")
except Exception:
    agent = InterviewAgent(mode="mock")

# Global state
current_state = None
current_config = {
    "api_key": None,
    "model": "Qwen/Qwen3-Coder-Next:novita"
}


# Models
class StepRequest(BaseModel):
    action: str


class AnswerRequest(BaseModel):
    answer: str


class AutoRunRequest(BaseModel):
    use_retry: bool = True


class ConfigRequest(BaseModel):
    api_key: str
    model: str = "Qwen/Qwen3-Coder-Next:novita"


@app.get("/")
def read_root():
    return selective_safe({
        "message": "AI Interview Preparation RL Environment (OpenEnv Compliant)",
        "status": "running",
        "endpoints": ["/reset", "/step", "/state", "/question", "/answer", "/auto-run", "/stats", "/config"]
    })


@app.post("/reset")
def reset():
    global current_state
    current_state = env.reset()
    return selective_safe({
        "question": current_state["question"],
        "difficulty": current_state["difficulty"],
        "attempt": current_state["attempt"]
    })


@app.post("/step")
def step(request: StepRequest):
    global current_state

    if current_state is None:
        raise HTTPException(status_code=400, detail="Call /reset first")

    result = env.step(request.action)
    state_data = env.state()

    return selective_safe({
        "reward": result["reward"],
        "done": result["done"],
        "state": state_data
    })


@app.get("/state")
def get_state():
    if current_state is None:
        raise HTTPException(status_code=400, detail="Call /reset first")

    return selective_safe(env.state())


@app.get("/question")
def get_question():
    global current_state
    current_state = env.reset()
    return selective_safe({
        "status": "success",
        "state": current_state
    })


@app.post("/answer")
def submit_answer(request: AnswerRequest):
    global current_state

    if current_state is None:
        raise HTTPException(status_code=400, detail="Call /question first")

    result = env.step(request.answer)

    return selective_safe({
        "status": "success",
        "result": result
    })


@app.post("/auto-run")
def auto_run(request: AutoRunRequest):
    global current_state

    current_state = env.reset()
    question = current_state["question"]

    answer = agent.generate_answer(question)
    result = env.step(answer)

    episode_data = {
        "question": question,
        "difficulty": current_state["difficulty"],
        "attempt_1": {
            "answer": answer,
            "score": result["score"],
            "reward": result["reward"],
            "feedback": result["feedback"]
        }
    }

    if request.use_retry and env.should_retry(result["reward"]):
        improved_answer = agent.generate_answer(
            question,
            feedback=result["feedback"],
            missing_keywords=result.get("missing_keywords", [])
        )

        retry_result = env.step(improved_answer)

        episode_data["attempt_2"] = {
            "answer": improved_answer,
            "score": retry_result["score"],
            "reward": retry_result["reward"],
            "feedback": retry_result["feedback"]
        }

        episode_data["improvement"] = retry_result["score"] - result["score"]

    return selective_safe({
        "status": "success",
        "episode": episode_data
    })


@app.post("/config")
def update_config(request: ConfigRequest):
    global agent, current_config

    current_config["api_key"] = request.api_key
    current_config["model"] = request.model

    agent = InterviewAgent(mode="api", api_key=request.api_key, model=request.model)

    return selective_safe({
        "status": "success",
        "message": "Configuration updated",
        "config": {
            "model": request.model,
            "api_key_set": True
        }
    })


@app.get("/config")
def get_config():
    return selective_safe({
        "status": "success",
        "config": {
            "model": current_config["model"],
            "api_key_set": bool(current_config["api_key"])
        }
    })


@app.get("/stats")
def get_stats():
    history = env.get_history()

    if not history:
        return selective_safe({
            "status": "success",
            "stats": {
                "total_attempts": 0,
                "average_score": 0.001,
                "average_reward": 0.001
            }
        })

    avg_score = sum(h["score"] for h in history) / len(history)
    avg_reward = sum(h["reward"] for h in history) / len(history)

    return selective_safe({
        "status": "success",
        "stats": {
            "total_attempts": len(history),
            "average_score": avg_score,
            "average_reward": avg_reward,
            "history": history
        }
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))