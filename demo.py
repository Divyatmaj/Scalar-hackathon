"""
Demo script showing API usage
Run this after starting the FastAPI server to see the RL loop in action
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def demo_rl_loop():
    """Demonstrate the complete RL loop"""
    
    print_section("🤖 AI INTERVIEW PREP - RL LOOP DEMONSTRATION")
    
    # Check server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print("✅ Server is running!\n")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Backend server not running!")
        print("Please start the server first:")
        print("  cd backend && python main.py\n")
        return
    
    # Step 1: Get a question (env.reset())
    print_section("STEP 1: Get Question (env.reset())")
    response = requests.get(f"{BASE_URL}/question")
    data = response.json()
    state = data['state']
    
    print(f"Question: {state['question']}")
    print(f"Difficulty: {state['difficulty'].upper()}")
    print(f"Expected Keywords: {', '.join(state['keywords'])}")
    
    time.sleep(2)
    
    # Step 2: Auto-run with AI agent
    print_section("STEP 2: AI Agent Generates Answer & Gets Evaluated")
    print("Running automatic RL episode with retry enabled...\n")
    
    response = requests.post(f"{BASE_URL}/auto-run", json={"use_retry": True})
    episode = response.json()['episode']
    
    # Show attempt 1
    print("📝 ATTEMPT 1:")
    print("-" * 70)
    attempt1 = episode['attempt_1']
    print(f"Answer: {attempt1['answer']}\n")
    print(f"Score: {attempt1['score']:.1%}")
    print(f"Reward: {attempt1['reward']}")
    print(f"Feedback: {attempt1['feedback']}")
    
    # Show attempt 2 if exists
    if 'attempt_2' in episode:
        time.sleep(2)
        print("\n🔄 LOW SCORE DETECTED - RETRYING WITH FEEDBACK\n")
        
        print("📝 ATTEMPT 2 (Improved):")
        print("-" * 70)
        attempt2 = episode['attempt_2']
        print(f"Answer: {attempt2['answer']}\n")
        print(f"Score: {attempt2['score']:.1%}")
        print(f"Reward: {attempt2['reward']}")
        print(f"Feedback: {attempt2['feedback']}")
        print(f"\n🎯 Improvement: {episode['improvement']:+.1%}")
    
    time.sleep(2)
    
    # Step 3: Get statistics
    print_section("STEP 3: Episode Statistics")
    response = requests.get(f"{BASE_URL}/stats")
    stats = response.json()['stats']
    
    print(f"Total Attempts: {stats['total_attempts']}")
    print(f"Average Score: {stats['average_score']:.3f}")
    print(f"Average Reward: {stats['average_reward']:.2f}")
    
    # Summary
    print_section("✅ RL LOOP COMPLETE!")
    print("The system demonstrated:")
    print("  1. STATE: Interview question with metadata")
    print("  2. ACTION: AI-generated answer")
    print("  3. REWARD: Score-based reward signal")
    print("  4. IMPROVEMENT: Feedback-driven retry mechanism\n")
    print("This is a complete Reinforcement Learning environment! 🎉\n")


def demo_manual_answer():
    """Demonstrate manual answer submission"""
    
    print_section("📝 MANUAL ANSWER DEMO")
    
    # Get question
    response = requests.get(f"{BASE_URL}/question")
    state = response.json()['state']
    print(f"Question: {state['question']}\n")
    
    # Submit a manual answer
    manual_answer = "This is a test answer with some " + " and ".join(state['keywords'][:2])
    print(f"Submitting answer: {manual_answer}\n")
    
    response = requests.post(f"{BASE_URL}/answer", json={"answer": manual_answer})
    result = response.json()['result']
    
    print(f"Score: {result['score']:.1%}")
    print(f"Reward: {result['reward']}")
    print(f"Feedback: {result['feedback']}\n")


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     AI INTERVIEW PREPARATION - RL ENVIRONMENT DEMO            ║
    ║                                                               ║
    ║  This demo shows the complete Reinforcement Learning loop:   ║
    ║     STATE → ACTION → REWARD → NEXT STATE                     ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Run main demo
    demo_rl_loop()
    
    # Optional: Run manual demo
    print("\n" + "=" * 70)
    run_manual = input("Run manual answer demo? (y/n): ").lower().strip()
    if run_manual == 'y':
        demo_manual_answer()
    
    print("\n" + "=" * 70)
    print("Demo complete! Open http://localhost:3000 to try the UI")
    print("=" * 70 + "\n")
