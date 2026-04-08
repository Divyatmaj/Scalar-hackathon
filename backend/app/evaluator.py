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
    
    def __init__(self, keyword_weight: float = 0.7, ai_weight: float = 0.3):
        """
        Initialize evaluator with scoring weights
        
        Args:
            keyword_weight: Weight for keyword-based score (default 0.7)
            ai_weight: Weight for AI-based score (default 0.3)
            
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
            return 0.0, [], keywords
        
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
        
        return keyword_score, matched_keywords, missing_keywords
    
    def evaluate_ai(self, answer: str, question: str = None) -> float:
        """
        AI-based evaluation (placeholder for future LLM judge)
        
        This is a MOCK implementation. In production, this would:
        - Call GPT-4/Claude to judge answer quality
        - Return semantic understanding score
        - Consider coherence, completeness, clarity
        
        Current implementation:
        - Returns random score between 0.5-0.9
        - Can be replaced with real LLM API call
        
        Args:
            answer: Candidate's answer
            question: Original question (for context)
            
        Returns:
            AI score between 0.0 and 1.0
        """
        # PLACEHOLDER IMPLEMENTATION
        # TODO: Replace with actual LLM-based judging
        
        # Mock: Simple heuristic based on answer length
        # Longer, structured answers get slightly higher scores
        import random
        
        if not answer or len(answer.strip()) < 20:
            return 0.3
        elif len(answer.strip()) < 100:
            return 0.6 + random.uniform(0, 0.2)
        else:
            return 0.7 + random.uniform(0, 0.2)
        
        # FUTURE IMPLEMENTATION:
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[{
        #         "role": "system",
        #         "content": "You are an expert technical interviewer. Rate answers 0-10."
        #     }, {
        #         "role": "user",
        #         "content": f"Question: {question}\nAnswer: {answer}\nScore:"
        #     }]
        # )
        # return float(response.choices[0].message.content) / 10.0
    
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
    
    def compute_reward(self, score: float) -> int:
        """
        Convert score to RL reward signal
        
        Reward structure (reinforcement learning):
        - Excellent (≥0.8): +10 → Strong positive reinforcement
        - Good (≥0.5): +5 → Moderate positive reinforcement
        - Needs improvement (≥0.3): 0 → Neutral (no penalty, no reward)
        - Poor (<0.3): -5 → Negative reinforcement
        
        This encourages:
        - High-quality comprehensive answers (+10)
        - Discourages incomplete answers (-5)
        - Neutral zone for partial attempts (0)
        
        Args:
            score: Evaluation score (0.0 to 1.0)
            
        Returns:
            Integer reward value
        """
        if score >= 0.8:
            return 10
        elif score >= 0.5:
            return 5
        elif score >= 0.3:
            return 0
        else:
            return -5
    
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
