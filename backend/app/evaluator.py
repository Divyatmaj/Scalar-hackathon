"""
Advanced Evaluator with Hybrid Scoring System
Evaluates interview answers using multiple metrics

Features:
- Keyword-based scoring (primary)
- AI-based scoring (placeholder/mock - extensible)
- Structured feedback generation
- Reward computation for RL
- Text normalization for robust matching

Design Philosophy:
- Modular: Easy to swap keyword logic or add LLM judge
- Extensible: Hybrid scoring allows future AI integration
- Explainable: Returns detailed feedback and matched/missing keywords
"""

import re
from typing import Dict, List, Any, Tuple

from .score_utils import clamp_open_score, MAX_OPEN_SCORE


class Evaluator:
    """
    Hybrid Answer Evaluator
    
    Evaluates answers using:
    1. Keyword matching (primary metric)
    2. AI scoring (placeholder for LLM-as-judge)
    
    Final score = 0.7 * keyword_score + 0.3 * ai_score
    
    This allows:
    - Fast, deterministic evaluation (keywords)
    - Future semantic understanding (AI judge)
    - Explainable results (specific missing concepts)
    """
    
    def __init__(self, keyword_weight: float = 0.8, ai_weight: float = 0.2):
        """
        Initialize evaluator with scoring weights
        
        Args:
            keyword_weight: Weight for keyword-based score (default 0.8)
            ai_weight: Weight for length-based score (default 0.2)
            
        Weights should sum to 1.0 for normalized scoring
        """
        self.keyword_weight = keyword_weight
        self.ai_weight = ai_weight
        
        # Validate weights
        if not abs((keyword_weight + ai_weight) - 1.0) < 0.01:
            print(f"⚠️  Warning: Weights don't sum to 1.0 ({keyword_weight + ai_weight})")
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for robust keyword matching
        
        Steps:
        1. Convert to lowercase
        2. Remove special characters (keep alphanumeric, spaces, hyphens, parens)
        3. Collapse multiple spaces
        """
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s\-\(\)]', ' ', text)
        text = ' '.join(text.split())
        return text
    
    def evaluate_keywords(self, answer: str, keywords: List[str]) -> Tuple[float, List[str], List[str]]:
        if not answer or not answer.strip():
            return clamp_open_score(0.0001), [], keywords
        
        normalized_answer = self.normalize_text(answer)
        matched_keywords = []
        missing_keywords = []
        
        for keyword in keywords:
            normalized_keyword = self.normalize_text(keyword)
            if normalized_keyword in normalized_answer:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        if len(keywords) == 0:
            keyword_score = 0.5
        else:
            keyword_score = len(matched_keywords) / len(keywords)
            keyword_score = clamp_open_score(keyword_score)
        
        return keyword_score, matched_keywords, missing_keywords
    
    def evaluate_ai(self, answer: str, question: str = None) -> float:
        if not answer or len(answer.strip()) < 10:
            return clamp_open_score(0.2)
        
        answer_length = len(answer.strip())
        
        if 100 <= answer_length <= 300:
            return clamp_open_score(0.89)
        elif answer_length < 100:
            return clamp_open_score(0.5 + 0.5 * (answer_length / 100.0))
        else:
            excess = answer_length - 300
            penalty = min(excess / 500.0, 0.2)
            return clamp_open_score(max(0.7, MAX_OPEN_SCORE - penalty))
    
    def evaluate(self, answer: str, keywords: List[str], question: str = None) -> Dict[str, Any]:
        keyword_score, matched, missing = self.evaluate_keywords(answer, keywords)
        ai_score = self.evaluate_ai(answer, question)
        
        final_score = (self.keyword_weight * keyword_score) + (self.ai_weight * ai_score)
        final_score = clamp_open_score(final_score)

        # 🔥 FIX: Clamp intermediate scores as well
        keyword_score = clamp_open_score(keyword_score)
        ai_score = clamp_open_score(ai_score)
        
        feedback = self._generate_feedback(
            score=final_score,
            keyword_score=keyword_score,
            matched=matched,
            missing=missing
        )
        
        return {
            "score": final_score,
            "keyword_score": keyword_score,
            "ai_score": ai_score,
            "matched_keywords": matched,
            "missing_keywords": missing,
            "feedback": feedback
        }
    
    def _generate_feedback(
        self, 
        score: float, 
        keyword_score: float,
        matched: List[str], 
        missing: List[str]
    ) -> str:
        total_keywords = len(matched) + len(missing)
        
        if score >= 0.8:
            base = f"✅ Excellent answer! "
            base += f"Covered {len(matched)}/{total_keywords} key concepts."
            if matched:
                base += f"\n   ✓ Mentioned: {', '.join(matched)}"
            return base
        
        elif score >= 0.5:
            base = f"👍 Good answer. "
            base += f"Covered {len(matched)}/{total_keywords} concepts."
            if matched:
                base += f"\n   ✓ Covered: {', '.join(matched)}"
            if missing:
                base += f"\n   ⚠ Consider adding: {', '.join(missing[:3])}"
            return base
        
        elif score >= 0.3:
            base = f"⚠️  Partial answer. "
            base += f"Only {len(matched)}/{total_keywords} concepts covered."
            if matched:
                base += f"\n   ✓ Included: {', '.join(matched)}"
            if missing:
                base += f"\n   ✗ Missing: {', '.join(missing)}"
            return base
        
        else:
            base = f"❌ Weak answer. "
            base += f"Missing {len(missing)}/{total_keywords} critical concepts."
            if missing:
                base += f"\n   ✗ Must include: {', '.join(missing)}"
            base += "\n   💡 Tip: Cover fundamental concepts first"
            return base
    
    def compute_reward(self, score: float) -> float:
        return clamp_open_score(score)
    
    def set_weights(self, keyword_weight: float, ai_weight: float):
        self.keyword_weight = keyword_weight
        self.ai_weight = ai_weight
