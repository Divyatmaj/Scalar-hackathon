"""
FastAPI Backend for AI Interview Preparation RL Environment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from env.interview_env import InterviewEnv
from evaluator.evaluator import Evaluator
from agent.llm_agent import LLMAgent


# Initialize FastAPI app
app = FastAPI(title="AI Interview Prep RL Environment")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
evaluator = Evaluator()
env = InterviewEnv(evaluator=evaluator)
agent = LLMAgent()

# Global state (in production, use session management)
current_state = None
current_config = {
    "api_key": None,
    "model": "Qwen/Qwen3-Coder-Next:novita"
}


# Request/Response models
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
        "message": "AI Interview Preparation RL Environment",
        "status": "running",
        "endpoints": ["/question", "/answer", "/auto-run", "/stats", "/config"]
    }


@app.get("/question")
def get_question():
    """
    Get a new interview question (calls env.reset())
    
    Returns:
        {
            "question": str,
            "keywords": list,
            "difficulty": str
        }
    """
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
    """
    Submit an answer and get evaluation (calls env.step())
    
    Args:
        answer: The candidate's answer
        
    Returns:
        {
            "reward": int,
            "score": float,
            "feedback": str,
            "missing_keywords": list,
            "done": bool
        }
    """
    global current_state
    
    if current_state is None:
        raise HTTPException(
            status_code=400, 
            detail="No active question. Call /question first"
        )
    
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
    """
    Automatic RL loop: Get question → Agent generates answer → Evaluate → Optional retry
    
    Args:
        use_retry: Whether to retry on low scores
        
    Returns:
        Complete episode results with optional retry
    """
    global current_state
    
    try:
        # Reset environment and get question
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
            improved_answer = agent.generate_answer(question, result["feedback"])
            
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
    """
    Update API configuration (API key and model)
    
    Args:
        api_key: Hugging Face API token
        model: Model name/endpoint to use
        
    Returns:
        Configuration status
    """
    global agent, current_config
    
    try:
        # Update configuration
        current_config["api_key"] = request.api_key
        current_config["model"] = request.model
        
        # Reinitialize agent with new configuration
        agent = LLMAgent(api_key=request.api_key, model=request.model)
        
        return {
            "status": "success",
            "message": "Configuration updated successfully",
            "config": {
                "model": request.model,
                "api_key_set": bool(request.api_key),
                "client_initialized": bool(agent.client)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@app.get("/config")
def get_config():
    """
    Get current API configuration
    
    Returns:
        Current configuration (without exposing full API key)
    """
    return {
        "status": "success",
        "config": {
            "model": current_config["model"],
            "api_key_set": bool(current_config["api_key"]),
            "client_initialized": bool(agent.client)
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
