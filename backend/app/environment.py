import json
import random
from typing import Dict, Any, List
from pathlib import Path
from .score_utils import clamp_open_score

class InterviewEnv:
    def __init__(self, questions_path: str, evaluator):
        self.questions_path = questions_path
        self.evaluator = evaluator
        self.questions = self._load_questions()
        self.current_question = None
        self.episode_history = []
        self.retry_count = 0

    def _load_questions(self) -> List[Dict[str, Any]]:
        try:
            with open(self.questions_path, "r") as f:
                questions = json.load(f)
            return questions
        except Exception:
            return []

    def reset(self) -> Dict[str, Any]:
        if not self.questions:
            raise ValueError("No questions available")

        self.current_question = random.choice(self.questions)
        self.episode_history = []
        self.retry_count = 0

        return {
            "question": self.current_question.get("question", ""),
            "keywords": self.current_question.get("keywords", []),
            "difficulty": self.current_question.get("difficulty", "medium"),
        }

    def step(self, answer: str) -> Dict[str, Any]:
        if not self.current_question:
            raise ValueError("Environment not initialized. Call reset() first.")

        keywords = self.current_question.get("keywords", [])
        question = self.current_question.get("question", "")

        evaluation = self.evaluator.evaluate(answer, keywords, question)

        # Ensure evaluation exists and get the score
        try:
            score = float(evaluation.get("score", 0.5))
        except (TypeError, ValueError):
            score = 0.5

        # Clamp score strictly to [0.1, 0.9] using central utility
        score = clamp_open_score(score)

        result = {
            "score": score,
            "reward": clamp_open_score(score),
            "feedback": evaluation.get("feedback", ""),
            "matched_keywords": evaluation.get("matched_keywords", []),
            "missing_keywords": evaluation.get("missing_keywords", []),
        }

        self.episode_history.append(result)

        return result

    def should_retry(self, reward: float) -> bool:
        """
        Determines if the agent should attempt the question again.
        """
        if self.retry_count >= 1:
            return False

        if reward < 0.5:
            self.retry_count += 1
            return True

        return False

    def state(self) -> Dict[str, Any]:
        """
        Get current environment state
        """
        if not self.current_question:
            raise ValueError("Environment not initialized. Call reset() first.")
        
        return {
            "question": self.current_question.get("question", ""),
            "keywords": self.current_question.get("keywords", []),
            "difficulty": self.current_question.get("difficulty", "medium"),
            "attempt": len(self.episode_history) + 1,
        }

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get episode history for stats
        """
        return self.episode_history