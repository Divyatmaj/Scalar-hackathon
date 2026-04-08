"""
AI Agent with Retry and Memory Capabilities
Uses HuggingFace LLM via OpenAI-compatible API

Features:
- Real LLM integration (HuggingFace Qwen model)
- Retry mechanism with feedback integration
- Memory of previous attempts
- Mock fallback when API unavailable
"""

import os
from typing import List, Dict, Any, Optional


class InterviewAgent:
    """
    AI Agent for Interview Preparation
    
    Simulates a candidate that:
    1. Generates answers to questions
    2. Receives feedback on answers
    3. Improves answers using feedback
    4. Tracks performance over time
    
    The agent can use:
    - Mock/simulated answers (for testing)
    - Real LLM API (GPT-4, Claude, etc.)
    """
    
    def __init__(self, mode: str = "mock", api_key: str = None, model: str = None):
        """
        Initialize the AI agent
        
        Args:
            mode: "mock" for simulated answers or "api" for real LLM
            api_key: API key for HuggingFace (or from HF_TOKEN env variable)
            model: Model name (or from MODEL_NAME env variable)
        """
        self.mode = mode
        self.api_key = api_key or os.getenv("HF_TOKEN")
        self.model = model or os.getenv("MODEL_NAME", "Qwen/Qwen3-Coder-Next:novita")
        self.base_url = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
        self.memory = []
        self.current_question_memory = []
        self.client = None
        
        # Initialize API client if using real LLM
        if mode == "api" and self.api_key:
            self._init_api_client()
        elif mode == "api":
            print("⚠️  API mode selected but no API key provided. Falling back to mock mode.")
            self.mode = "mock"
    
    def _init_api_client(self):
        """Initialize LLM client via OpenAI-compatible API"""
        try:
            from openai import OpenAI
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
            print(f"🔌 API client initialized")
            print(f"   Base URL: {self.base_url}")
            print(f"   Model: {self.model}")
        except ImportError:
            print("⚠️  openai package not installed. Install with: pip install openai")
            print("⚠️  Falling back to mock mode")
            self.mode = "mock"
        except Exception as e:
            print(f"⚠️  Error initializing API client: {e}")
            print("⚠️  Falling back to mock mode")
            self.mode = "mock"
    
    def generate_answer(
        self, 
        question: str, 
        feedback: Optional[str] = None,
        missing_keywords: Optional[List[str]] = None,
        previous_attempts: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate an answer to the interview question
        
        Uses different strategies based on whether this is:
        - Initial attempt: Generate fresh answer
        - Retry attempt: Improve using feedback and missing keywords
        
        Args:
            question: The interview question
            feedback: Feedback from previous attempt (if retry)
            missing_keywords: Keywords that were missing (if retry)
            previous_attempts: List of previous attempts (for context)
            
        Returns:
            Generated answer string
        """
        if self.mode == "mock":
            return self._generate_mock_answer(
                question, 
                feedback, 
                missing_keywords,
                previous_attempts
            )
        else:
            return self._generate_api_answer(
                question, 
                feedback, 
                missing_keywords,
                previous_attempts
            )
    
    def _generate_mock_answer(
        self, 
        question: str, 
        feedback: Optional[str] = None,
        missing_keywords: Optional[List[str]] = None,
        previous_attempts: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate simulated answer (for testing without API costs)
        
        Mock Logic:
        - Initial attempt: Returns partial answer (simulates incomplete knowledge)
        - Retry attempt: Adds missing keywords to answer (simulates learning)
        
        This allows testing the retry/feedback loop without LLM API calls.
        
        Args:
            question: Interview question
            feedback: Previous feedback
            missing_keywords: Keywords to add
            previous_attempts: History
            
        Returns:
            Simulated answer
        """
        # Database of mock answers for common topics
        # These are intentionally partial to trigger retry mechanism
        mock_knowledge_base = {
            "binary search": "Binary search is an algorithm that finds items in a sorted array by dividing the search space.",
            "process": "A process is a program in execution. A thread is a unit of execution within a process.",
            "normalization": "Database normalization organizes data to reduce redundancy using normal forms.",
            "oop": "The pillars of OOP include encapsulation and inheritance.",
            "deadlock": "A deadlock is when processes wait for each other's resources.",
            "hashmap": "A hashmap stores key-value pairs using a hash function.",
            "sql": "SQL databases use structured schemas. NoSQL databases are more flexible.",
            "solid": "SOLID includes Single Responsibility and Open-Closed principles.",
            "stack": "Stack uses LIFO. Heap is for dynamic allocation.",
            "rest": "REST is an architectural style for web services using HTTP.",
            "big o": "Big O notation describes algorithm complexity.",
            "cap": "CAP theorem states you can only achieve two of three properties in distributed systems."
        }
        
        # Find relevant base answer
        question_lower = question.lower()
        base_answer = None
        
        for key, answer in mock_knowledge_base.items():
            if key in question_lower:
                base_answer = answer
                break
        
        if base_answer is None:
            base_answer = "This is a complex topic in computer science."
        
        # If this is a retry, improve the answer by adding missing keywords
        if feedback and missing_keywords:
            improved_answer = base_answer
            
            # Add missing keywords to answer (simulating learning)
            if missing_keywords:
                improved_answer += " Important concepts include: "
                improved_answer += ", ".join(missing_keywords[:4]) + "."
            
            # Add some variety
            attempt_count = len(previous_attempts) if previous_attempts else 1
            if attempt_count > 1:
                improved_answer += f" Additionally, this relates to fundamental principles of the domain."
            
            return improved_answer
        
        # Return initial (incomplete) answer
        return base_answer
    
    def _generate_api_answer(
        self, 
        question: str, 
        feedback: Optional[str] = None,
        missing_keywords: Optional[List[str]] = None,
        previous_attempts: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate answer using HuggingFace LLM API
        
        Constructs different prompts based on:
        - Initial attempt: Clear, structured question
        - Retry attempt: Includes feedback and missing concepts
        """
        if not self.client:
            return self._generate_mock_answer(question, feedback, missing_keywords, previous_attempts)
        
        # Build prompt
        if feedback and missing_keywords:
            # Retry prompt with feedback
            prompt = f"""You are a technical interview candidate who received feedback on your previous answer.

Question: {question}

Previous Feedback: {feedback}

Missing Concepts: {', '.join(missing_keywords)}

Please provide an IMPROVED answer that addresses the feedback and includes the missing concepts. Be clear, concise, and comprehensive."""
        else:
            # Initial prompt
            prompt = f"""You are a technical interview candidate. Answer the following question clearly and comprehensively, covering all key concepts:

Question: {question}

Provide a well-structured answer:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a knowledgeable technical interview candidate."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling HuggingFace API: {e}")
            return self._generate_mock_answer(question, feedback, missing_keywords, previous_attempts)
    
    def remember_attempt(
        self, 
        question: str, 
        answer: str, 
        score: float, 
        feedback: str,
        attempt: int
    ):
        """
        Store attempt in memory for learning and analysis
        
        Memory allows agent to:
        - Track improvement over time
        - Analyze common mistakes
        - Build knowledge base
        
        Args:
            question: The question asked
            answer: Answer provided
            score: Score received
            feedback: Feedback received
            attempt: Attempt number
        """
        memory_entry = {
            "question": question,
            "answer": answer,
            "score": score,
            "feedback": feedback,
            "attempt": attempt
        }
        
        # Add to both global and question-specific memory
        self.memory.append(memory_entry)
        self.current_question_memory.append(memory_entry)
    
    def reset_question_memory(self):
        """
        Clear memory for current question
        
        Called when starting a new question/episode.
        Keeps global memory but clears question-specific memory.
        """
        self.current_question_memory = []
    
    def get_improvement_stats(self) -> Dict[str, Any]:
        """
        Calculate improvement statistics from memory
        
        Returns:
            Dictionary with:
                - total_attempts: Total questions attempted
                - average_score: Average score across all attempts
                - improvement_rate: How much scores improved on retries
                - total_retries: Number of retry attempts made
        """
        if not self.memory:
            return {
                "total_attempts": 0,
                "average_score": 0.0,
                "improvement_rate": 0.0,
                "total_retries": 0
            }
        
        scores = [m["score"] for m in self.memory]
        retries = [m for m in self.memory if m["attempt"] > 1]
        
        # Calculate improvement rate
        improvement_rate = 0.0
        if len(self.current_question_memory) > 1:
            first_score = self.current_question_memory[0]["score"]
            last_score = self.current_question_memory[-1]["score"]
            improvement_rate = last_score - first_score
        
        return {
            "total_attempts": len(self.memory),
            "average_score": sum(scores) / len(scores),
            "improvement_rate": improvement_rate,
            "total_retries": len(retries)
        }
    
    def get_memory(self) -> List[Dict[str, Any]]:
        """
        Get complete memory
        
        Returns:
            List of all stored attempts
        """
        return self.memory
    
    def get_current_question_memory(self) -> List[Dict[str, Any]]:
        """
        Get memory for current question only
        
        Returns:
            List of attempts for current question
        """
        return self.current_question_memory
