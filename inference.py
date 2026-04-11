import os
import sys
import json
import re
from pathlib import Path

# 🔥 BLOCK ALL UNWANTED PRINTS
sys.stdout = open(os.devnull, 'w')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.environment import InterviewEnv
from app.evaluator import Evaluator
from app.agent import InterviewAgent


def _format_action(action: str) -> str:
    if not action:
        return ""

    text = str(action)

    # Clean whitespace
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Remove dangerous tokens
    text = text.replace("[START]", "")
    text = text.replace("[STEP]", "")
    text = text.replace("[END]", "")
    text = text.replace("task_id=", "")
    text = text.replace("score=", "")

    return text[:200]


def run_inference():
    hf_token = os.getenv("HF_TOKEN")

    evaluator = Evaluator()
    questions_path = Path(__file__).parent / "backend" / "app" / "dataset.json"
    env = InterviewEnv(str(questions_path), evaluator)

    if hf_token:
        agent = InterviewAgent(mode="api", api_key=hf_token)
    else:
        agent = InterviewAgent(mode="mock")

    with open(questions_path, "r") as f:
        tasks = json.load(f)

    for i, task in enumerate(tasks):
        task_id = f"task_{i}"

        # STRICT OUTPUT ONLY
        sys.__stdout__.write("[START]\n")
        sys.__stdout__.write(f"task_id={task_id}\n")

        env.current_question = task
        env.episode_history = []
        env.retry_count = 0

        question = task["question"]

        # Generate answer
        answer = agent.generate_answer(question)
        action = _format_action(answer)

        sys.__stdout__.write("[STEP]\n")
        sys.__stdout__.write(f"action={action}\n")

        # Evaluate
        result = env.step(answer)

        # SAFE SCORE
        try:
            raw_score = float(result.get("score", 0.5))
        except Exception:
            raw_score = 0.5

        epsilon = 1e-6
        raw_score = max(epsilon, min(raw_score, 1 - epsilon))

        score = "{:.6f}".format(raw_score)

        sys.__stdout__.write(f"score={score}\n")
        sys.__stdout__.write("[END]\n")


if __name__ == "__main__":
    run_inference()