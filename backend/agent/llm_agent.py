"""
LLM Agent for generating interview answers
Uses OpenAI API (can be swapped with HuggingFace)
"""

import os
from typing import Optional


class LLMAgent:
    """Agent that generates answers using LLM"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize LLM agent
        
        Args:
            api_key: OpenAI API key (defaults to env variable)
            model: Model name to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("Warning: openai package not installed. Install with: pip install openai")
    
    def generate_answer(self, question: str, feedback: Optional[str] = None) -> str:
        """
        Generate answer to interview question
        
        Args:
            question: The interview question
            feedback: Optional feedback from previous attempt (for retry)
            
        Returns:
            Generated answer string
        """
        if not self.client:
            return self._generate_mock_answer(question)
        
        # Build prompt
        if feedback:
            prompt = f"""You are a technical interview candidate. You previously gave an answer that was weak.

Feedback on previous answer: {feedback}

Please provide an IMPROVED answer to the following question. Be clear, concise, and cover all key concepts:

Question: {question}

Answer:"""
        else:
            prompt = f"""You are a technical interview candidate. Answer the following question clearly and concisely, covering all key technical concepts:

Question: {question}

Answer:"""
        
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
            print(f"Error calling OpenAI API: {e}")
            return self._generate_mock_answer(question)
    
    def _generate_mock_answer(self, question: str) -> str:
        """
        Generate a mock answer when API is not available
        Used for testing without API key
        """
        mock_answers = {
            "binary search": "Binary search is an efficient algorithm for finding an item in a sorted array. It works by repeatedly dividing the search interval in half, comparing the middle element with the target. Time complexity is O(log n).",
            "process": "A process is an independent program in execution with its own memory space. A thread is a lightweight unit of execution within a process that shares memory with other threads.",
            "normalization": "Database normalization is the process of organizing data to reduce redundancy and improve data integrity. It involves dividing tables and defining relationships using normal forms.",
            "oop": "The four pillars of OOP are: Encapsulation (bundling data and methods), Abstraction (hiding complexity), Inheritance (code reuse), and Polymorphism (multiple forms).",
            "deadlock": "A deadlock occurs when processes wait for each other's resources in a circular manner. Prevention strategies include avoiding circular wait and using resource ordering.",
            "hashmap": "A hashmap uses a hash function to map keys to array indices (buckets). Collisions are handled using techniques like chaining with linked lists. Average lookup is O(1).",
            "sql": "SQL databases are structured with fixed schemas and ACID properties. NoSQL databases are more flexible, schema-less, and designed for horizontal scaling.",
            "solid": "SOLID principles are: Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion.",
            "memory": "Stack memory is used for static allocation with LIFO structure. Heap memory is for dynamic allocation with manual management and longer lifetime.",
            "rest": "RESTful APIs follow constraints like statelessness, client-server architecture, cacheability, and uniform interface using HTTP methods on resources.",
            "big o": "Big O notation describes algorithm time/space complexity in terms of input size, focusing on worst-case growth rate for efficiency analysis.",
            "cap": "CAP theorem states distributed systems can only guarantee two of three: Consistency, Availability, and Partition tolerance. Trade-offs must be made."
        }
        
        # Find best matching mock answer
        question_lower = question.lower()
        for key, answer in mock_answers.items():
            if key in question_lower:
                return answer
        
        return "This is a mock answer. Please set OPENAI_API_KEY environment variable to use real LLM."
