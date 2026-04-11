import os
import sys
import json
import re
from pathlib import Path

# 🔥 BLOCK ALL UNWANTED PRINTS
sys.stdout = open(os.devnull, 'w')

# Import modules
from backend.app.environment import InterviewEnv
from backend.app.evaluator import Evaluator
from backend.app.agent import InterviewAgent


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

        # START
        sys.__stdout__.write("[START]\n")
        sys.__stdout__.write(f"task_id={task_id}\n")

        env.current_question = task
        env.episode_history = []
        env.retry_count = 0

        question = task["question"]

        # ===== STEP 1 =====
        answer = agent.generate_answer(question)
        action1 = _format_action(answer)

        sys.__stdout__.write("[STEP]\n")
        sys.__stdout__.write(f"action={action1}\n")

        result1 = env.step(answer)

        epsilon = 1e-6
        score1 = max(epsilon, min(float(result1.get("score", 0.5)), 1 - epsilon))
        score1 = "{:.6f}".format(score1)

        sys.__stdout__.write(f"score={score1}\n")

        # ===== STEP 2 (RETRY) =====
        improved_answer = answer + " with more explanation"
        action2 = _format_action(improved_answer)

        sys.__stdout__.write("[STEP]\n")
        sys.__stdout__.write(f"action={action2}\n")

        result2 = env.step(improved_answer)

        score2 = max(epsilon, min(float(result2.get("score", 0.5)), 1 - epsilon))
        score2 = "{:.6f}".format(score2)

        sys.__stdout__.write(f"score={score2}\n")

        # END
        sys.__stdout__.write("[END]\n\n")


if __name__ == "__main__":
    run_inference()