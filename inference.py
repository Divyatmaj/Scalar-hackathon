import contextlib
import io
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.agent import InterviewAgent
from app.environment import InterviewEnv
from app.evaluator import Evaluator
from app.score_utils import clamp_open_score, format_open_score


def _task_id_alpha(index: int) -> str:
    base = "abcdefghijklmnopqrstuvwxyz"
    n = index
    out = []
    while True:
        out.append(base[n % 26])
        n = (n // 26) - 1
        if n < 0:
            break
    return "task_" + "".join(reversed(out))


def run_inference():
    hf_token = os.getenv("HF_TOKEN")
    model_name = os.getenv("MODEL_NAME", "Qwen/Qwen3-Coder-Next:novita")
    questions_path = Path(__file__).parent / "backend" / "app" / "dataset.json"
    if not questions_path.exists():
        return

    with contextlib.redirect_stdout(io.StringIO()):
        evaluator = Evaluator()
        env = InterviewEnv(questions_path=str(questions_path), evaluator=evaluator)
        if hf_token:
            agent = InterviewAgent(mode="api", api_key=hf_token, model=model_name)
        else:
            agent = InterviewAgent(mode="mock")

    with open(questions_path, "r") as f:
        tasks = json.load(f)

    for task_idx, task in enumerate(tasks):
        env.current_question = task
        env.episode_history = []
        env.retry_count = 0
        question = task.get("question", "")

        with contextlib.redirect_stdout(io.StringIO()):
            answer = agent.generate_answer(question)
            result = env.step(answer)

        raw_score = result.get("score", 0.5)
        try:
            score = clamp_open_score(float(raw_score))
        except (TypeError, ValueError):
            score = 0.5
        score = clamp_open_score(score)

        sys.__stdout__.write("[START]\n")
        sys.__stdout__.write(f"task_id={_task_id_alpha(task_idx)}\n")
        sys.__stdout__.write("[STEP]\n")
        sys.__stdout__.write("action=answer_submitted\n")
        sys.__stdout__.write(f"score={format_open_score(score, decimals=1)}\n")
        sys.__stdout__.write("[END]\n")
        sys.__stdout__.flush()


if __name__ == "__main__":
    run_inference()
