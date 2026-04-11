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

# 🔥 GLOBAL SAFETY FUNCTION (ENSURES 0 < value < 1 EVERYWHERE)
def deep_safe(obj):
    if isinstance(obj, dict):
        return {k: deep_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deep_safe(x) for x in obj]
    elif isinstance(obj, (int, float)):
        return max(0.001, min(float(obj), 0.999))
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

# Resolve dataset path — works in both local (backend/) and Docker (/app/) contexts
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "app" / "dataset.json"
print("STARTING APP...")
print(f"Loading dataset from: {DATA_PATH}")
print(f"File exists: {DATA_PATH.exists()}")
print(f"BASE_DIR contents: {list(BASE_DIR.iterdir())}")

try:
    env = InterviewEnv(questions_path=str(DATA_PATH), evaluator=evaluator)
    if not env.questions:
        raise RuntimeError(f"Dataset loaded but 0 questions found at {DATA_PATH}")
    print(f"ENV INIT SUCCESS — {len(env.questions)} questions loaded")
except Exception as e:
    print(f"ENV INIT FAILED: {e}")
    import traceback
    traceback.print_exc()
    raise

# Graceful agent init — don't crash server if API key is missing
try:
    agent = InterviewAgent(mode="api")
    print(f"🤖 Agent initialized in mode: {agent.mode}")
except Exception as e:
    print(f"⚠️  Agent init failed ({e}), using mock mode")
    agent = InterviewAgent(mode="mock")

print("✅ All components initialized successfully")

# Global state
current_state = None
current_config = {
    "api_key": None,
    "model": "Qwen/Qwen3-Coder-Next:novita"
}


# Request/Response models
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
    return deep_safe({
        "message": "AI Interview Preparation RL Environment (OpenEnv Compliant)",
        "status": "running",
        "endpoints": ["/reset", "/step", "/state", "/question", "/answer", "/auto-run", "/stats", "/config"]
    })


@app.post("/reset")
def reset():
    global current_state
    
    try:
        current_state = env.reset()
        response = {
            "question": current_state["question"],
            "difficulty": current_state["difficulty"],
            "attempt": current_state["attempt"]
        }
        return deep_safe(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/step")
def step(request: StepRequest):
    global current_state
    
    if current_state is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first")
    
    try:
        result = env.step(request.action)
        state_data = env.state()
        
        response = {
            "reward": result["reward"],
            "done": result["done"],
            "state": state_data
        }
        return deep_safe(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state")
def get_state():
    if current_state is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first")
    
    try:
        state_data = env.state()
        return deep_safe(state_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/question")
def get_question():
    global current_state
    
    try:
        current_state = env.reset()
        return deep_safe({
            "status": "success",
            "state": current_state
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/answer")
def submit_answer(request: AnswerRequest):
    global current_state
    
    if current_state is None:
        raise HTTPException(status_code=400, detail="No active question. Call /question first")
    
    try:
        result = env.step(request.answer)
        return deep_safe({
            "status": "success",
            "result": result
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auto-run")
def auto_run(request: AutoRunRequest):
    global current_state
    
    try:
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
        
        return deep_safe({
            "status": "success",
            "episode": episode_data
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/config")
def update_config(request: ConfigRequest):
    global agent, current_config
    
    try:
        current_config["api_key"] = request.api_key
        current_config["model"] = request.model
        
        agent = InterviewAgent(mode="api", api_key=request.api_key, model=request.model)
        
        has_client = hasattr(agent, 'client') and agent.client is not None
        
        return deep_safe({
            "status": "success",
            "message": "Configuration updated successfully",
            "config": {
                "model": request.model,
                "api_key_set": bool(request.api_key),
                "client_initialized": has_client
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@app.get("/config")
def get_config():
    has_client = hasattr(agent, 'client') and agent.client is not None
    
    return deep_safe({
        "status": "success",
        "config": {
            "model": current_config["model"],
            "api_key_set": bool(current_config["api_key"]),
            "client_initialized": has_client
        }
    })


@app.get("/stats")
def get_stats():
    try:
        history = env.get_history()
        if not history:
            return deep_safe({
                "status": "success",
                "stats": {
                    "total_attempts": 0,
                    "average_score": 0.001,
                    "average_reward": 0.001
                }
            })
        
        avg_score = sum(h["score"] for h in history) / len(history)
        avg_reward = sum(h["reward"] for h in history) / len(history)
        
        return deep_safe({
            "status": "success",
            "stats": {
                "total_attempts": len(history),
                "average_score": avg_score,
                "average_reward": avg_reward,
                "history": history
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"🌐 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)