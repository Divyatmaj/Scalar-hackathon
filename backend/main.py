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
    return clamp_open_score(x)


def selective_safe(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if ("score" in k) or ("reward" in k):
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
from app.score_utils import clamp_open_score


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


class AutoRunRequest(BaseModel):
    use_retry: bool = True


class ConfigRequest(BaseModel):
    api_key: str
    model: str = "Qwen/Qwen3-Coder-Next:novita"


# Root
@app.get("/")
def read_root():
    return selective_safe({
        "message": "AI Interview Environment",
        "status": "running",
        "endpoints": [
            "/reset",
            "/step",
            "/state",
            "/question",
            "/answer",
            "/auto-run",
            "/config",
            "/stats",
        ],
    })


# Reset
@app.post("/reset")
def reset():
    global current_state
    current_state = env.reset()
    return selective_safe(current_state)


# Legacy endpoint (frontend compatibility)
@app.get("/question")
def get_question():
    global current_state
    current_state = env.reset()
    return selective_safe({
        "status": "success",
        "state": current_state
    })


# 🔥 REQUIRED BY VALIDATOR
@app.post("/act")
def act(request: StepRequest):
    global current_state

    if current_state is None:
        current_state = env.reset()

    result = env.step(request.action)
    result["reward"] = clamp_open_score(result["reward"])
    result["score"] = clamp_open_score(result["score"])
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
    result = act(StepRequest(action=request.answer))
    return selective_safe({
        "status": "success",
        "result": result,
    })


# Legacy endpoint (frontend compatibility)
@app.post("/auto-run")
def auto_run(request: AutoRunRequest):
    global current_state

    current_state = env.reset()
    question = current_state["question"]
    difficulty = current_state["difficulty"]
    missing_keywords = None
    feedback = None
    attempts = []

    answer_1 = agent.generate_answer(
        question=question,
        feedback=feedback,
        missing_keywords=missing_keywords,
        previous_attempts=attempts,
    )
    result_1 = env.step(answer_1)
    result_1["reward"] = clamp_open_score(result_1["reward"])
    result_1["score"] = clamp_open_score(result_1["score"])
    agent.remember_attempt(
        question=question,
        answer=answer_1,
        score=result_1["score"],
        feedback=result_1["feedback"],
        attempt=result_1["attempt"],
    )
    attempt_1 = {
        "answer": answer_1,
        "score": result_1["score"],
        "reward": result_1["reward"],
        "feedback": result_1["feedback"],
    }

    episode = {
        "question": question,
        "difficulty": difficulty,
        "attempt_1": attempt_1,
    }

    if request.use_retry and env.should_retry(result_1["score"]):
        attempts.append({
            "answer": answer_1,
            "score": result_1["score"],
            "feedback": result_1["feedback"],
        })
        answer_2 = agent.generate_answer(
            question=question,
            feedback=result_1["feedback"],
            missing_keywords=result_1.get("missing_keywords"),
            previous_attempts=attempts,
        )
        result_2 = env.step(answer_2)
        result_2["reward"] = clamp_open_score(result_2["reward"])
        result_2["score"] = clamp_open_score(result_2["score"])
        agent.remember_attempt(
            question=question,
            answer=answer_2,
            score=result_2["score"],
            feedback=result_2["feedback"],
            attempt=result_2["attempt"],
        )
        episode["attempt_2"] = {
            "answer": answer_2,
            "score": result_2["score"],
            "reward": result_2["reward"],
            "feedback": result_2["feedback"],
        }
        episode["improvement"] = result_2["score"] - result_1["score"]

    return selective_safe({
        "status": "success",
        "episode": episode,
    })


# Legacy endpoint (frontend compatibility)
@app.get("/config")
def get_config():
    return selective_safe({
        "status": "success",
        "config": {
            "model": agent.model,
            "api_key_set": bool(agent.api_key),
            "client_initialized": bool(agent.client),
        },
    })


# Legacy endpoint (frontend compatibility)
@app.post("/config")
def update_config(request: ConfigRequest):
    global agent
    if not request.api_key.strip():
        raise HTTPException(status_code=400, detail="api_key cannot be empty")

    agent = InterviewAgent(mode="api", api_key=request.api_key.strip(), model=request.model)
    if agent.mode != "api" or not agent.client:
        raise HTTPException(
            status_code=400,
            detail="Could not initialize API client. Check token/model configuration.",
        )

    return selective_safe({
        "status": "success",
        "message": "Configuration updated successfully",
        "config": {
            "model": agent.model,
            "api_key_set": True,
            "client_initialized": True,
        },
    })


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
            "average_score": 0.1,
            "average_reward": 0.1
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
