# OpenEnv Validation Guide

This document provides step-by-step instructions to validate OpenEnv compliance.

## ✅ Phase 1: Schema Validation

### Check openenv.yaml exists
```bash
ls openenv.yaml
```
**Expected**: File exists ✅

### Validate schema
```bash
# Manual check: Ensure endpoints match
cat openenv.yaml | grep -A 2 "endpoints:"
```

**Expected output**:
- /reset (POST)
- /step (POST)
- /state (GET)

---

## ✅ Phase 2: Docker Build & Run

### Build Docker image
```bash
docker build -t ai-interview-env .
```

**Expected**: Build succeeds without errors ✅

### Run container
```bash
docker run -d -p 8000:8000 --name interview-env \
  -e HF_TOKEN=your_token_here \
  ai-interview-env
```

**Expected**: Container starts successfully ✅

### Test endpoints
```bash
# Test reset
curl -X POST http://localhost:8000/reset

# Expected response:
# {
#   "question": "...",
#   "difficulty": "easy",
#   "attempt": 0
# }

# Test step
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"action": "This is a test answer"}'

# Expected response:
# {
#   "reward": 0.45,
#   "done": false,
#   "state": {
#     "question": "...",
#     "difficulty": "...",
#     "attempt": 1
#   }
# }

# Test state
curl http://localhost:8000/state

# Expected response:
# {
#   "question": "...",
#   "difficulty": "...",
#   "attempt": 1
# }
```

**Stop container**:
```bash
docker stop interview-env
docker rm interview-env
```

---

## ✅ Phase 3: Inference Script

### Run inference
```bash
# Set environment variables (optional, has defaults)
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen3-Coder-Next:novita
export HF_TOKEN=your_token_here  # Optional, will use mock mode if not set

# Run inference
python inference.py
```

**Expected output format**:
```
[START]
task_id=task_0
[STEP]
action=Binary search is an algorithm...
reward=0.75
[END]

[START]
task_id=task_1
[STEP]
action=A process is...
reward=0.65
[END]

...
```

**Validation checks**:
- ✅ Completes in < 20 minutes
- ✅ No errors or crashes
- ✅ All 12 tasks processed
- ✅ Exact logging format ([START], [STEP], [END])
- ✅ Rewards between 0.0 and 1.0

---

## ✅ Determinism Check

### Test same input gives same output
```bash
# Start server
cd backend
source venv/bin/activate
python main.py &
SERVER_PID=$!

# Test determinism
curl -X POST http://localhost:8000/reset > /tmp/reset1.json
curl -X POST http://localhost:8000/step -H "Content-Type: application/json" \
  -d '{"action": "Test answer"}' > /tmp/step1.json

curl -X POST http://localhost:8000/reset > /tmp/reset2.json
curl -X POST http://localhost:8000/step -H "Content-Type: application/json" \
  -d '{"action": "Test answer"}' > /tmp/step2.json

# Compare rewards
diff /tmp/step1.json /tmp/step2.json

# Clean up
kill $SERVER_PID
```

**Expected**: Rewards are identical (deterministic) ✅

---

## ✅ Reward Range Check

### Verify all rewards in [0.0, 1.0]
```bash
python inference.py 2>&1 | grep "reward=" | awk -F'=' '{print $2}' | \
  awk '{if ($1 < 0.0 || $1 > 1.0) {print "FAIL: "$1; exit 1}} END {print "PASS: All rewards in [0.0, 1.0]"}'
```

**Expected**: PASS: All rewards in [0.0, 1.0] ✅

---

## ✅ Task Count Check

### Verify ≥3 tasks
```bash
python -c "import json; tasks = json.load(open('backend/app/dataset.json')); print(f'Tasks: {len(tasks)}'); exit(0 if len(tasks) >= 3 else 1)"
```

**Expected**: Tasks: 12 ✅

---

## 🎯 Full Validation Checklist

- [x] openenv.yaml exists and valid
- [x] Docker builds successfully
- [x] Docker container runs on port 8000
- [x] /reset endpoint returns correct schema
- [x] /step endpoint returns correct schema
- [x] /state endpoint returns correct schema
- [x] Rewards always in range [0.0, 1.0]
- [x] Grading is deterministic
- [x] ≥3 tasks present (12 total)
- [x] inference.py runs without errors
- [x] inference.py completes in < 20 minutes
- [x] Exact logging format with [START]/[STEP]/[END]

---

## 🚀 Quick Validation Commands

### Full validation in one script
```bash
#!/bin/bash
set -e

echo "=== OpenEnv Validation ==="
echo ""

echo "1. Checking openenv.yaml..."
test -f openenv.yaml && echo "✅ openenv.yaml exists"

echo ""
echo "2. Building Docker image..."
docker build -t ai-interview-env . && echo "✅ Docker build successful"

echo ""
echo "3. Running Docker container..."
docker run -d -p 8000:8000 --name interview-env ai-interview-env
sleep 5
docker ps | grep interview-env && echo "✅ Container running"

echo ""
echo "4. Testing /reset endpoint..."
curl -s -X POST http://localhost:8000/reset | grep -q "question" && echo "✅ /reset works"

echo ""
echo "5. Testing /step endpoint..."
curl -s -X POST http://localhost:8000/step -H "Content-Type: application/json" \
  -d '{"action": "test"}' | grep -q "reward" && echo "✅ /step works"

echo ""
echo "6. Testing /state endpoint..."
curl -s http://localhost:8000/state | grep -q "question" && echo "✅ /state works"

echo ""
echo "7. Cleaning up container..."
docker stop interview-env && docker rm interview-env && echo "✅ Cleanup done"

echo ""
echo "8. Running inference..."
python inference.py | head -20 && echo "✅ Inference runs"

echo ""
echo "=== ✅ ALL VALIDATIONS PASSED ==="
```

Save as `validate.sh`, make executable (`chmod +x validate.sh`), and run (`./validate.sh`).

---

## 📝 Notes

- **Mock Mode**: If HF_TOKEN is not set, agent runs in mock mode (deterministic, no API calls)
- **API Mode**: Set HF_TOKEN to use real LLM (requires valid HuggingFace token)
- **Environment Variables**: All configurable via env vars (API_BASE_URL, MODEL_NAME, HF_TOKEN)
- **Backward Compatibility**: Legacy endpoints (/question, /answer) still work for existing frontend
