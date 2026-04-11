import os
import sys
import json
import re
from pathlib import Path

# Add backend to path
# Note: Changed **file** to __file__
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.environment import InterviewEnv
from app.evaluator import Evaluator
from app.agent import InterviewAgent

def _format_action_for_log(action: str) -> str:
    """
    Clean action text to avoid breaking parser
    """
    text = "" if action is None else str(action)

    # Remove newlines/tabs
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Remove dangerous tokens
    replacements = {
        "[START]": "(START)",
        "[STEP]": "(STEP)",
        "[END]": "(END)",
        "task_id=": "task_id\\u003d",
        "score=": "score\\u003d",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text

def run_inference():
    hf_token = os.getenv("HF_TOKEN")

    evaluator = Evaluator()
    questions_path = Path(__file__).parent / "backend" / "app" / "dataset.json"
    env = InterviewEnv(questions_path=str(questions_path), evaluator=evaluator)

    # Initialize agent safely (NO prints allowed)
    if hf_token:
        agent = InterviewAgent(mode="api", api_key=hf_token)
    else:
        agent = InterviewAgent(mode="mock")

    if not questions_path.exists():
        return

    with open(questions_path, "r") as f:
        tasks = json.load(f)

    for task_idx, task in enumerate(tasks):
        task_id = f"task_{task_idx}"

        # STRICT OUTPUT START
        sys.__stdout__.write("[START]\n")
        sys.__stdout__.write(f"task_id={task_id}\n")

        env.current_question = task
        env.episode_history = []
        env.retry_count = 0

        question = task.get("question", "")

        # Generate answer
        answer = agent.generate_answer(question)
        action = _format_action_for_log(answer)

        sys.__stdout__.write("[STEP]\n")
        sys.__stdout__.write(f"action={action}\n")

        # Evaluate
        result = env.step(answer)

        # FINAL SAFE SCORE (STRICTLY BETWEEN 0 AND 1)
        try:
            raw_score = float(result.get("score", 0.5))
        except (TypeError, ValueError):
            raw_score = 0.5

        epsilon = 1e-6
        score = max(epsilon, min(raw_score, 1 - epsilon))

        sys.__stdout__.write(f"score={score}\n")
        sys.__stdout__.write("[END]\n")
        sys.__stdout__.flush() # Ensure logs are sent immediately

if __name__ == "__main__":
    run_inference()