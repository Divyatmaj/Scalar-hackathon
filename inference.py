"""
OpenEnv-compliant inference script
Runs complete episode over all tasks with exact logging format
"""

import os
import sys
import json
import re
import io
import contextlib
from pathlib import Path

# Add backend to path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.environment import InterviewEnv
from app.evaluator import Evaluator
from app.agent import InterviewAgent
from app.score_utils import clamp_open_score, format_open_score

def _format_action_for_log(action: str) -> str:
    """
    Format model output to keep OpenEnv logs parser-safe.
    """
    text = "" if action is None else str(action)
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Neutralize parser-sensitive markers regardless of case/spacing.
    text = re.sub(r"(?i)\[(start|step|end)\]", r"(\1)", text)
    text = re.sub(r"(?i)\btask_id\s*=", r"task_id\\u003d", text)
    text = re.sub(r"(?i)\bscore\s*=", r"score\\u003d", text)
    text = re.sub(r"(?i)\breward\s*=", r"reward\\u003d", text)

    # Defang any score/reward numeric patterns and remove bare numbers to avoid parser collisions.
    text = re.sub(r"(?i)\b(score|reward)\s*[:=]?\s*[+-]?\d+(?:\.\d+)?\b", r"\1 <masked>", text)
    text = re.sub(r"\b[+-]?\d+(?:\.\d+)?\b", "<num>", text)

    return text


def run_inference():
    # Environment variables
    api_base_url = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
    model_name = os.getenv("MODEL_NAME", "Qwen/Qwen3-Coder-Next:novita")
    hf_token = os.getenv("HF_TOKEN")


    # Initialize components quietly so inference stdout remains parser-stable.
    questions_path = Path(__file__).parent / "backend" / "app" / "dataset.json"
    with contextlib.redirect_stdout(io.StringIO()):
        evaluator = Evaluator()
        env = InterviewEnv(questions_path=str(questions_path), evaluator=evaluator)

    # Initialize agent
    if hf_token:
        with contextlib.redirect_stdout(io.StringIO()):
            agent = InterviewAgent(mode="api", api_key=hf_token, model=model_name)
    else:
        agent = InterviewAgent(mode="mock")

    # Load dataset
    with open(questions_path, 'r') as f:
        tasks = json.load(f)

    # Run inference
    for task_idx, task in enumerate(tasks):
        task_id = f"task_{task_idx}"

        # START
        print("[START]")
        print(f"task_id={task_id}")

        # Set environment state
        env.current_question = task
        env.episode_history = []
        env.retry_count = 0

        question = task["question"]

        # Generate answer
        # Keep inference stdout parser-stable even if API client prints runtime warnings/errors.
        with contextlib.redirect_stdout(io.StringIO()):
            answer = agent.generate_answer(question)
        # Keep action line parser-safe and deterministic.
        action_for_log = "answer_submitted"

        # STEP
        print("[STEP]")
        print(f"action={action_for_log}")

        # Evaluate
        result = env.step(answer)

        raw_score = result.get("score", 0.5)
        try:
            score = clamp_open_score(raw_score)
        except Exception:
            score = 0.5
        print(f"score={format_open_score(score, decimals=1)}")

        # END
        print("[END]")


if __name__ == "__main__":
    run_inference()
