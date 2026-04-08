"""
FastAPI Backend for AI Interview Preparation RL Environment
OpenEnv-compliant API implementation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import from app package
from app.environment import InterviewEnv
from app.evaluator import Evaluator
from app.agent import InterviewAgent


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
questions_path = Path(__file__).parent / "app" / "dataset.json"
env = InterviewEnv(questions_path=str(questions_path), evaluator=evaluator)
agent = InterviewAgent(mode="api")  # Will use HF_TOKEN from .env

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
    """Root endpoint"""
    return {
        "message": "AI Interview Preparation RL Environment (OpenEnv Compliant)",
        "status": "running",
        "endpoints": ["/reset", "/step", "/state", "/question", "/answer", "/auto-run", "/stats", "/config"]
    }


# OpenEnv-compliant endpoints

@app.post("/reset")
def reset():
    """OpenEnv: Reset environment and get new question"""
    global current_state
    
    try:
        current_state = env.reset()
        # Return only the required fields for OpenEnv compliance
        return {
            "question": current_state["question"],
            "difficulty": current_state["difficulty"],
            "attempt": current_state["attempt"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/step")
def step(request: StepRequest):
    """OpenEnv: Submit action and get reward"""
    global current_state
    
    if current_state is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first")
    
    try:
        result = env.step(request.action)
        
        # Get current state
        state_data = env.state()
        
        # Return OpenEnv-compliant response
        return {
            "reward": result["reward"],
            "done": result["done"],
            "state": state_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state")
def get_state():
    """OpenEnv: Get current environment state"""
    if current_state is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first")
    
    try:
        state_data = env.state()
        return state_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Legacy endpoints (for backward compatibility with existing frontend)

@app.get("/question")
def get_question():
    """Get a new interview question (calls env.reset())"""
    global current_state
    
    try:
        current_state = env.reset()
        return {
            "status": "success",
            "state": current_state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/answer")
def submit_answer(request: AnswerRequest):
    """Submit an answer and get evaluation (calls env.step())"""
    global current_state
    
    if current_state is None:
        raise HTTPException(status_code=400, detail="No active question. Call /question first")
    
    try:
        result = env.step(request.answer)
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auto-run")
def auto_run(request: AutoRunRequest):
    """Automatic RL episode - agent generates and improves answer"""
    global current_state
    
    try:
        # Reset environment
        current_state = env.reset()
        question = current_state["question"]
        
        # Agent generates initial answer
        answer = agent.generate_answer(question)
        
        # Evaluate
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
        
        # Retry logic if enabled and reward is low
        if request.use_retry and env.should_retry(result["reward"]):
            # Reset for retry
            current_state = {
                "question": question,
                "keywords": current_state["keywords"],
                "difficulty": current_state["difficulty"]
            }
            env.current_question = {
                "question": question,
                "keywords": current_state["keywords"],
                "difficulty": current_state["difficulty"]
            }
            
            # Generate improved answer with feedback
            improved_answer = agent.generate_answer(
                question,
                feedback=result["feedback"],
                missing_keywords=result.get("missing_keywords", [])
            )
            
            # Evaluate again
            retry_result = env.step(improved_answer)
            
            episode_data["attempt_2"] = {
                "answer": improved_answer,
                "score": retry_result["score"],
                "reward": retry_result["reward"],
                "feedback": retry_result["feedback"]
            }
            
            episode_data["improvement"] = retry_result["score"] - result["score"]
        
        return {
            "status": "success",
            "episode": episode_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/config")
def update_config(request: ConfigRequest):
    """Update API configuration (API key and model)"""
    global agent, current_config
    
    try:
        # Update configuration
        current_config["api_key"] = request.api_key
        current_config["model"] = request.model
        
        # Reinitialize agent with new configuration
        agent = InterviewAgent(mode="api", api_key=request.api_key, model=request.model)
        
        # Check if agent has proper client initialization
        has_client = hasattr(agent, 'client') and agent.client is not None
        
        return {
            "status": "success",
            "message": "Configuration updated successfully",
            "config": {
                "model": request.model,
                "api_key_set": bool(request.api_key),
                "client_initialized": has_client
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@app.get("/config")
def get_config():
    """Get current API configuration"""
    has_client = hasattr(agent, 'client') and agent.client is not None
    
    return {
        "status": "success",
        "config": {
            "model": current_config["model"],
            "api_key_set": bool(current_config["api_key"]),
            "client_initialized": has_client
        }
    }


@app.get("/stats")
def get_stats():
    """Get episode statistics"""
    try:
        history = env.get_history()
        if not history:
            return {
                "status": "success",
                "stats": {
                    "total_attempts": 0,
                    "average_score": 0,
                    "average_reward": 0
                }
            }
        
        avg_score = sum(h["score"] for h in history) / len(history)
        avg_reward = sum(h["reward"] for h in history) / len(history)
        
        return {
            "status": "success",
            "stats": {
                "total_attempts": len(history),
                "average_score": round(avg_score, 3),
                "average_reward": round(avg_reward, 2),
                "history": history
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
