"""
Test script to verify the RL environment works correctly
Run this before starting the full application
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from env.interview_env import InterviewEnv
from evaluator.evaluator import Evaluator
from agent.llm_agent import LLMAgent


def test_environment():
    """Test the RL environment"""
    print("=" * 60)
    print("🧪 TESTING RL ENVIRONMENT")
    print("=" * 60)
    
    # Initialize components
    evaluator = Evaluator()
    env = InterviewEnv(evaluator=evaluator)
    agent = LLMAgent()
    
    print("\n✅ Components initialized successfully\n")
    
    # Test 1: Reset environment
    print("📝 Test 1: Environment Reset")
    print("-" * 60)
    state = env.reset()
    print(f"Question: {state['question']}")
    print(f"Difficulty: {state['difficulty']}")
    print(f"Keywords: {', '.join(state['keywords'])}")
    print("✅ Reset successful\n")
    
    # Test 2: Evaluate a good answer
    print("📝 Test 2: Evaluate Good Answer")
    print("-" * 60)
    good_answer = " ".join(state['keywords'][:3])  # Include some keywords
    result = env.step(good_answer)
    print(f"Answer: {good_answer}")
    print(f"Score: {result['score']:.2%}")
    print(f"Reward: {result['reward']}")
    print(f"Feedback: {result['feedback']}")
    print("✅ Evaluation successful\n")
    
    # Test 3: Generate AI answer
    print("📝 Test 3: AI Agent Answer Generation")
    print("-" * 60)
    env.reset()  # Get new question
    question = env.current_question['question']
    ai_answer = agent.generate_answer(question)
    print(f"Question: {question}")
    print(f"AI Answer: {ai_answer}")
    result = env.step(ai_answer)
    print(f"Score: {result['score']:.2%}")
    print(f"Reward: {result['reward']}")
    print(f"Feedback: {result['feedback']}")
    print("✅ AI generation successful\n")
    
    # Test 4: Retry mechanism
    print("📝 Test 4: Retry Mechanism")
    print("-" * 60)
    if env.should_retry(result['reward']):
        print("⚠️  Low reward detected - initiating retry")
        improved_answer = agent.generate_answer(question, result['feedback'])
        
        # Reset to same question for retry
        env.current_question = {
            "question": question,
            "keywords": state['keywords'],
            "difficulty": state['difficulty']
        }
        
        retry_result = env.step(improved_answer)
        print(f"Improved Answer: {improved_answer}")
        print(f"New Score: {retry_result['score']:.2%}")
        print(f"New Reward: {retry_result['reward']}")
        improvement = retry_result['score'] - result['score']
        print(f"Improvement: {improvement:+.2%}")
        print("✅ Retry successful\n")
    else:
        print("✅ Score was good - no retry needed\n")
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYou can now start the FastAPI server with:")
    print("  python main.py")


if __name__ == "__main__":
    test_environment()
