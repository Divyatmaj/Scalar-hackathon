"""
AI Interview Preparation Environment
OpenAI Gym-style RL Environment for Interview Practice

This module implements the core environment following the standard RL interface:
- reset() -> returns initial state (question)
- step(action) -> executes action and returns (reward, state, done, info)

Features:
- Random question selection from dataset
- Episode history tracking
- Configurable retry thresholds
- Support for multi-turn episodes (extensible)
"""

import json
import random
from typing import Dict, Any, List
from pathlib import Path

from .score_utils import clamp_open_score


class InterviewEnv:
    """
    Interview Preparation Environment
    
    This environment simulates a technical interview scenario where:
    - State: Interview question with metadata (keywords, difficulty)
    - Action: Candidate's answer (text string)
    - Reward: Score-based reward computed by evaluator
    
    Design Decisions:
    - Single question per episode (can be extended to multi-question)
    - Stateful: maintains current question and episode history
    - Delegated evaluation: uses injected evaluator for scoring
    """
    
    def __init__(self, questions_path: str = None, evaluator=None):
        """
        Initialize the interview environment
        
        Args:
            questions_path: Path to questions.json (defaults to ../data/questions.json)
            evaluator: Evaluator instance for scoring answers (must implement evaluate())
        """
        # Set default path if not provided
        if questions_path is None:
            questions_path = Path(__file__).parent.parent / "data" / "questions.json"
        
        self.questions_path = questions_path
        self.evaluator = evaluator
        self.questions = self._load_questions()
        
        # State tracking
        self.current_question = None
        self.episode_history = []  # Stores all attempts in current episode
        self.retry_count = 0
        self.max_retries = 3  # Configurable retry limit
        
    def _load_questions(self) -> List[Dict[str, Any]]:
        """
        Load questions from JSON dataset
        
        Returns:
            List of question dictionaries with structure:
            {
                "question": str,
                "keywords": List[str],
                "difficulty": str
            }
        """
        try:
            with open(self.questions_path, 'r') as f:
                questions = json.load(f)
            print(f"✅ Loaded {len(questions)} questions from {self.questions_path}")
            return questions
        except FileNotFoundError:
            print(f"❌ Questions file not found: {self.questions_path}")
            return []
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in questions file")
            return []
    
    def reset(self) -> Dict[str, Any]:
        """
        Reset environment to initial state
        
        Selects a new random question and clears episode history.
        This follows the Gym API convention.
        
        Returns:
            state: Dictionary containing:
                - question: The interview question text
                - keywords: Expected keywords for evaluation
                - difficulty: Question difficulty level
                - attempt: Current attempt number (always 0 after reset)
        """
        # Select random question from dataset
        if not self.questions:
            raise ValueError("No questions loaded. Check questions.json")
        
        self.current_question = random.choice(self.questions)
        self.episode_history = []
        self.retry_count = 0
        
        # Return state representation
        state = {
            "question": self.current_question["question"],
            "keywords": self.current_question["keywords"],
            "difficulty": self.current_question["difficulty"],
            "attempt": 0
        }
        
        print(f"\n{'='*60}")
        print(f"📝 NEW QUESTION [{state['difficulty'].upper()}]")
        print(f"{'='*60}")
        print(f"{state['question']}")
        print(f"{'='*60}\n")
        
        return state
    
    def step(self, action: str) -> Dict[str, Any]:
        """
        Execute one environment step
        
        Takes the candidate's answer, evaluates it, and returns feedback.
        This is the core of the RL loop.
        
        Args:
            action: The candidate's answer (string)
            
        Returns:
            Dictionary containing:
                - reward: Integer reward signal (+10, +5, 0, -5)
                - score: Float score (0.0 to 1.0)
                - feedback: Structured feedback message
                - matched_keywords: List of correctly mentioned keywords
                - missing_keywords: List of missed keywords
                - done: Boolean indicating if episode is complete
                - attempt: Current attempt number
                
        Raises:
            ValueError: If environment not initialized (call reset() first)
        """
        # Validation
        if self.current_question is None:
            raise ValueError("Environment not initialized. Call reset() first.")
        
        if self.evaluator is None:
            raise ValueError("Evaluator not set. Pass evaluator to constructor.")
        
        # Evaluate the answer using injected evaluator
        evaluation = self.evaluator.evaluate(
            answer=action,
            keywords=self.current_question["keywords"]
        )
        
        # Extract evaluation results
        score = clamp_open_score(evaluation["score"])
        feedback = evaluation["feedback"]
        matched_keywords = evaluation["matched_keywords"]
        missing_keywords = evaluation["missing_keywords"]
        
        # Compute reward signal
        reward = clamp_open_score(self.evaluator.compute_reward(score))
        
        # Increment retry counter
        self.retry_count += 1
        
        # Store in episode history for memory/analysis
        self.episode_history.append({
            "attempt": self.retry_count,
            "answer": action,
            "score": score,
            "reward": reward,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "feedback": feedback
        })
        
        # Determine if episode is done
        # Done if: high score OR max retries reached
        done = (score >= 0.999) or (self.retry_count >= self.max_retries)
        
        # Return full step information
        return {
            "reward": reward,
            "score": score,
            "feedback": feedback,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "done": done,
            "attempt": self.retry_count,
            "question": self.current_question["question"]
        }
    
    def should_retry(self, reward: float) -> bool:
        """
        Determine if agent should attempt to improve answer
        
        Args:
            reward: Current reward value (0.0 to 1.0)
            
        Returns:
            True if agent should retry (low reward and retries available)
        """
        can_retry = self.retry_count < self.max_retries
        needs_retry = reward < 0.7  # Threshold for improvement
        
        return can_retry and needs_retry
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get complete episode history
        
        Returns:
            List of all attempts in current episode with full details
        """
        return self.episode_history
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get episode statistics
        
        Returns:
            Dictionary with:
                - total_attempts: Number of attempts made
                - best_score: Highest score achieved
                - improvement: Score improvement from first to last
                - final_reward: Final reward value
        """
        if not self.episode_history:
            return {
                "total_attempts": 0,
                "best_score": 0.001,
                "improvement": 0.001,
                "final_reward": 0.001
            }
        
        scores = [h["score"] for h in self.episode_history]
        rewards = [h["reward"] for h in self.episode_history]
        
        return {
            "total_attempts": len(self.episode_history),
            "best_score": max(scores),
            "improvement": scores[-1] - scores[0] if len(scores) > 1 else 0.0,
            "final_reward": rewards[-1]
        }
    
    def set_max_retries(self, max_retries: int):
        """
        Configure maximum retry attempts
        
        Args:
            max_retries: Maximum number of attempts allowed
        """
        self.max_retries = max_retries
    
    def state(self) -> Dict[str, Any]:
        """
        Get current environment state
        
        OpenEnv-compliant state getter.
        Returns current question and attempt information.
        
        Returns:
            Dictionary containing:
                - question: Current question text
                - difficulty: Question difficulty level
                - attempt: Current attempt number
                
        Raises:
            ValueError: If environment not initialized (call reset() first)
        """
        if self.current_question is None:
            raise ValueError("Environment not initialized. Call reset() first.")
        
        return {
            "question": self.current_question["question"],
            "difficulty": self.current_question["difficulty"],
            "attempt": self.retry_count
        }
