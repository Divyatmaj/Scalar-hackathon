"""
Evaluation Engine for Interview Answers
Computes score based on keyword matching and generates feedback
"""

import re
from typing import Tuple, List


class Evaluator:
    """Evaluates interview answers based on keyword coverage"""
    
    def __init__(self):
        pass
    
    def normalize_text(self, text: str) -> str:
        """Normalize text by lowercasing and removing extra punctuation"""
        text = text.lower()
        # Keep alphanumeric and basic punctuation
        text = re.sub(r'[^a-z0-9\s\-\(\)]', ' ', text)
        # Remove extra spaces
        text = ' '.join(text.split())
        return text
    
    def evaluate(self, answer: str, keywords: List[str]) -> Tuple[float, str, List[str]]:
        """
        Evaluate answer against expected keywords
        
        Args:
            answer: The candidate's answer
            keywords: List of expected keywords/phrases
            
        Returns:
            (score, feedback, missing_keywords)
            - score: float between 0 and 1
            - feedback: detailed feedback string
            - missing_keywords: list of keywords not found
        """
        if not answer or not answer.strip():
            return 0.0, "No answer provided", keywords
        
        normalized_answer = self.normalize_text(answer)
        matched_keywords = []
        missing_keywords = []
        
        # Check each keyword
        for keyword in keywords:
            normalized_keyword = self.normalize_text(keyword)
            if normalized_keyword in normalized_answer:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate score
        if len(keywords) == 0:
            score = 0.5  # Default score if no keywords
        else:
            score = len(matched_keywords) / len(keywords)
        
        # Generate feedback
        feedback = self._generate_feedback(score, matched_keywords, missing_keywords)
        
        return score, feedback, missing_keywords
    
    def _generate_feedback(self, score: float, matched: List[str], missing: List[str]) -> str:
        """Generate human-readable feedback based on evaluation"""
        if score >= 0.8:
            return f"✅ Excellent answer! Covered {len(matched)}/{len(matched) + len(missing)} key concepts: {', '.join(matched)}"
        elif score >= 0.5:
            feedback = f"👍 Good answer. Covered: {', '.join(matched)}."
            if missing:
                feedback += f" Consider adding: {', '.join(missing[:3])}"
            return feedback
        elif score >= 0.3:
            feedback = f"⚠️ Partial answer. Covered: {', '.join(matched) if matched else 'none'}."
            if missing:
                feedback += f" Missing key concepts: {', '.join(missing)}"
            return feedback
        else:
            return f"❌ Weak answer. Missing critical concepts: {', '.join(missing)}. Please cover the fundamental ideas."
    
    def compute_reward(self, score: float) -> int:
        """
        Compute RL reward based on score
        
        Reward structure:
        - score >= 0.8: +10 (excellent)
        - score >= 0.5: +5  (good)
        - score >= 0.3: 0   (needs improvement)
        - score < 0.3:  -5  (poor)
        """
        if score >= 0.8:
            return 10
        elif score >= 0.5:
            return 5
        elif score >= 0.3:
            return 0
        else:
            return -5
