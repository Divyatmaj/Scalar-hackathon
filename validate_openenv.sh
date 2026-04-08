#!/bin/bash
# OpenEnv Validation Script
# Run this to verify all requirements are met

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║   OpenEnv Hackathon Compliance Validation             ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

PASS=0
FAIL=0

check_pass() {
    echo "✅ $1"
    ((PASS++))
}

check_fail() {
    echo "❌ $1"
    ((FAIL++))
}

# 1. Check openenv.yaml
echo "1️⃣  Checking openenv.yaml..."
if [ -f "openenv.yaml" ]; then
    check_pass "openenv.yaml exists"
else
    check_fail "openenv.yaml missing"
fi

# 2. Check inference.py
echo "2️⃣  Checking inference.py..."
if [ -f "inference.py" ]; then
    check_pass "inference.py exists"
else
    check_fail "inference.py missing"
fi

# 3. Check Dockerfile
echo "3️⃣  Checking Dockerfile..."
if [ -f "Dockerfile" ]; then
    check_pass "Dockerfile exists"
else
    check_fail "Dockerfile missing"
fi

# 4. Check tasks count
echo "4️⃣  Checking task count..."
TASK_COUNT=$(python3 -c "import json; print(len(json.load(open('backend/app/dataset.json'))))" 2>/dev/null || echo "0")
if [ "$TASK_COUNT" -ge 3 ]; then
    check_pass "Task count: $TASK_COUNT (≥3 required)"
else
    check_fail "Task count: $TASK_COUNT (need ≥3)"
fi

# 5. Check determinism
echo "5️⃣  Testing deterministic grading..."
RESULT=$(python3 -c "
import sys
sys.path.insert(0, 'backend')
from app.evaluator import Evaluator
e = Evaluator()
scores = [e.evaluate('test answer', ['test'])['score'] for _ in range(3)]
print('PASS' if len(set(scores)) == 1 else 'FAIL')
" 2>/dev/null || echo "ERROR")

if [ "$RESULT" = "PASS" ]; then
    check_pass "Grading is deterministic"
else
    check_fail "Grading is not deterministic"
fi

# 6. Check reward range
echo "6️⃣  Testing reward range..."
RESULT=$(python3 -c "
import sys
sys.path.insert(0, 'backend')
from app.evaluator import Evaluator
from app.environment import InterviewEnv
e = Evaluator()
env = InterviewEnv(questions_path='backend/app/dataset.json', evaluator=e)
env.reset()
result = env.step('test')
r = result['reward']
print('PASS' if isinstance(r, float) and 0.0 <= r <= 1.0 else 'FAIL')
" 2>/dev/null || echo "ERROR")

if [ "$RESULT" = "PASS" ]; then
    check_pass "Reward in range [0.0, 1.0]"
else
    check_fail "Reward range validation failed"
fi

# 7. Check state() method
echo "7️⃣  Testing state() method..."
RESULT=$(python3 -c "
import sys
sys.path.insert(0, 'backend')
from app.evaluator import Evaluator
from app.environment import InterviewEnv
e = Evaluator()
env = InterviewEnv(questions_path='backend/app/dataset.json', evaluator=e)
env.reset()
state = env.state()
print('PASS' if 'question' in state and 'difficulty' in state else 'FAIL')
" 2>/dev/null || echo "ERROR")

if [ "$RESULT" = "PASS" ]; then
    check_pass "state() method works"
else
    check_fail "state() method failed"
fi

# 8. Check inference runs
echo "8️⃣  Testing inference script..."
if python3 inference.py 2>&1 | grep -q "\[START\]"; then
    check_pass "inference.py runs with correct format"
else
    check_fail "inference.py format incorrect"
fi

# 9. Check endpoints in main.py
echo "9️⃣  Checking API endpoints..."
if python3 -c "
from backend.main import app
routes = [r.path for r in app.routes if hasattr(r, 'path')]
required = ['/reset', '/step', '/state']
print('PASS' if all(r in routes for r in required) else 'FAIL')
" 2>/dev/null | grep -q "PASS"; then
    check_pass "All required endpoints present"
else
    check_fail "Missing required endpoints"
fi

# 10. Check environment variables support
echo "🔟 Checking environment variable support..."
if grep -q "os.getenv.*API_BASE_URL" backend/app/agent.py && \
   grep -q "os.getenv.*MODEL_NAME" backend/app/agent.py; then
    check_pass "Environment variables supported"
else
    check_fail "Environment variables not properly configured"
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════════════"
echo "RESULTS: $PASS passed, $FAIL failed"
echo "═══════════════════════════════════════════════════════"

if [ $FAIL -eq 0 ]; then
    echo ""
    echo "🎉 ALL CHECKS PASSED!"
    echo "✅ Repository is OpenEnv compliant"
    echo ""
    echo "Next steps:"
    echo "  1. Build Docker: docker build -t ai-interview-env ."
    echo "  2. Run server: docker run -p 8000:8000 ai-interview-env"
    echo "  3. Run inference: python3 inference.py"
    echo ""
    exit 0
else
    echo ""
    echo "⚠️  Some checks failed. Review errors above."
    echo ""
    exit 1
fi
