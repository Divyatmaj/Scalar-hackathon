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
        
        Args:
            text: Raw text string
            
        Returns:
            Normalized text string
            
        Examples:
            "O(log n)" -> "o(log n)"
            "Process!!!" -> "process"
            "REST  API" -> "rest api"
        """
        text = text.lower()
        
        # Keep alphanumeric, spaces, hyphens, and parentheses
        # This preserves "O(log n)", "client-server", etc.
        text = re.sub(r'[^a-z0-9\s\-\(\)]', ' ', text)
        
        # Collapse multiple spaces
        text = ' '.join(text.split())
        
        return text
    
    def evaluate_keywords(self, answer: str, keywords: List[str]) -> Tuple[float, List[str], List[str]]:
        """
        Evaluate answer based on keyword coverage
        
        This is the primary evaluation metric.
        
        Args:
            answer: Candidate's answer text
            keywords: List of expected keywords/phrases
            
        Returns:
            Tuple of (score, matched_keywords, missing_keywords)
            - score: Proportion of keywords found (0.0 to 1.0)
            - matched_keywords: Keywords found in answer
            - missing_keywords: Keywords not found in answer
            
        Algorithm:
        1. Normalize both answer and keywords
        2. Check if each keyword appears in answer (substring match)
        3. Calculate score as ratio: matched / total
        """
        if not answer or not answer.strip():
            return 0.0001, [], keywords
        
        normalized_answer = self.normalize_text(answer)
        matched_keywords = []
        missing_keywords = []
        
        # Check each keyword
        for keyword in keywords:
            normalized_keyword = self.normalize_text(keyword)
            
            # Use substring matching for flexibility
            # "O(log n)" matches "time complexity is O(log n)"
            if normalized_keyword in normalized_answer:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate proportional score
        if len(keywords) == 0:
            keyword_score = 0.5  # Neutral score if no keywords defined
        else:
            keyword_score = len(matched_keywords) / len(keywords)
            keyword_score = max(0.0001, keyword_score)
        
        return keyword_score, matched_keywords, missing_keywords
    
    def evaluate_ai(self, answer: str, question: str = None) -> float:
        """
        Length-based evaluation (deterministic)
        
        DETERMINISTIC implementation for OpenEnv compliance.
        Scores based on answer length relative to ideal length.
        
        Current implementation:
        - Deterministic scoring based on answer length
        - No randomness - same input always gives same output
        - Considers completeness via length heuristic
        
        Args:
            answer: Candidate's answer
            question: Original question (for context)
            
        Returns:
            Length score between 0.0 and 1.0
        """
        # DETERMINISTIC IMPLEMENTATION for OpenEnv compliance
        
        # Ideal answer length: 100-300 characters
        # Score based on how close to ideal range
        if not answer or len(answer.strip()) < 10:
            return 0.2
        
        answer_length = len(answer.strip())
        
        # Optimal range: 100-300 characters
        if 100 <= answer_length <= 300:
            return 0.999
        elif answer_length < 100:
            # Scale from 0.5 to 1.0 as length approaches 100
            return 0.5 + 0.5 * (answer_length / 100.0)
        else:
            # Penalize excessively long answers (diminishing returns)
            excess = answer_length - 300
            penalty = min(excess / 500.0, 0.3)  # Max 0.3 penalty
            return max(0.7, 1.0 - penalty)
        

    
    def evaluate(self, answer: str, keywords: List[str], question: str = None) -> Dict[str, Any]:
        """
        Complete hybrid evaluation
        
        Combines keyword-based and AI-based scoring with configurable weights.
        
        Args:
            answer: Candidate's answer
            keywords: Expected keywords for this question
            question: Original question (optional, for AI judge)
            
        Returns:
            Dictionary containing:
                - score: Final hybrid score (0.0 to 1.0)
                - keyword_score: Keyword-based score
                - ai_score: AI-based score
                - matched_keywords: Keywords found
                - missing_keywords: Keywords not found
                - feedback: Human-readable feedback string
        """
        # Evaluate using both methods
        keyword_score, matched, missing = self.evaluate_keywords(answer, keywords)
        ai_score = self.evaluate_ai(answer, question)
        
        # Compute weighted hybrid score
        final_score = (self.keyword_weight * keyword_score) + (self.ai_weight * ai_score)
        final_score = max(0.0001, min(final_score, 0.9999))
        
        # Clamp to exclusive (0, 1) range for OpenEnv compliance
        final_score = max(0.001, min(final_score, 0.999))
        # Round to 3 decimal places for clean output
        final_score = round(final_score, 3)
        # Re-clamp after rounding to guarantee strict (0, 1)
        final_score = max(0.001, min(final_score, 0.999))
        
        # Generate structured feedback
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
        """
        Generate structured, actionable feedback
        
        Feedback is designed to be:
        - Clear and specific
        - Actionable (tells what to add)
        - Encouraging (positive framing)
        - Machine-parseable (for agent improvement)
        
        Args:
            score: Final score
            keyword_score: Keyword coverage score
            matched: Matched keywords
            missing: Missing keywords
            
        Returns:
            Formatted feedback string
        """
        total_keywords = len(matched) + len(missing)
        
        # Score-based feedback tier
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
                # Show up to 3 missing keywords for actionable feedback
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
        """
        Convert score to RL reward signal
        
        OpenEnv-compliant reward function:
        - Reward is IDENTICAL to score (0.0 to 1.0 range)
        - Deterministic: same score always gives same reward
        - Continuous: allows fine-grained learning signals
        
        Args:
            score: Evaluation score (0.0 to 1.0)
            
        Returns:
            Float reward value (0.0 to 1.0)
        """
        # OpenEnv compliance: reward = score (0.0 to 1.0)
        return float(score)
    
    def set_weights(self, keyword_weight: float, ai_weight: float):
        """
        Update scoring weights
        
        Allows runtime adjustment of hybrid scoring balance.
        
        Args:
            keyword_weight: New keyword weight
            ai_weight: New AI weight
        """
        self.keyword_weight = keyword_weight
        self.ai_weight = ai_weight
