"""
OpenEnv-compliant inference script
Runs complete episode over all tasks with exact logging format
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.environment import InterviewEnv
from app.evaluator import Evaluator
from app.agent import InterviewAgent


def run_inference():
    """
    Run inference over all tasks with OpenEnv-compliant logging
    
    Environment variables:
    - API_BASE_URL: LLM API endpoint
    - MODEL_NAME: Model identifier
    - HF_TOKEN: API authentication token
    """
    
    # Get environment variables
    api_base_url = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
    model_name = os.getenv("MODEL_NAME", "Qwen/Qwen3-Coder-Next:novita")
    hf_token = os.getenv("HF_TOKEN")
    
    # Initialize components
    evaluator = Evaluator()
    questions_path = Path(__file__).parent / "backend" / "app" / "dataset.json"
    env = InterviewEnv(questions_path=str(questions_path), evaluator=evaluator)
    
    # Initialize agent (will use mock mode if no token)
    if hf_token:
        agent = InterviewAgent(mode="api", api_key=hf_token, model=model_name)
    else:
        print("⚠️  No HF_TOKEN found, using mock mode")
        agent = InterviewAgent(mode="mock")
    
    # Load all tasks
    with open(questions_path, 'r') as f:
        tasks = json.load(f)
    
    print(f"Running inference on {len(tasks)} tasks")
    print(f"API Base URL: {api_base_url}")
    print(f"Model: {model_name}")
    print("-" * 80)
    
    # Run inference on each task
    for task_idx, task in enumerate(tasks):
        task_id = f"task_{task_idx}"
        
        # Print START marker
        print(f"[START]")
        print(f"task_id={task_id}")
        
        # Reset environment to this specific task
        env.current_question = task
        env.episode_history = []
        env.retry_count = 0
        
        question = task["question"]
        
        # Generate answer
        answer = agent.generate_answer(question)
        
        # Print STEP marker with action
        print(f"[STEP]")
        print(f"action={answer}")
        
        # Evaluate
        result = env.step(answer)

        score = result["score"]

        # Print score (NOT reward)
        print(f"score={score}")
        
        # Print END marker
        print(f"[END]")
        print()
    
    print("-" * 80)
    print(f"✅ Inference complete: {len(tasks)} tasks processed")


if __name__ == "__main__":
    run_inference()
