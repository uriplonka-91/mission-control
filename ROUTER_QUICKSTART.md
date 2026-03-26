# Hybrid Agent Router - Quickstart Guide

## What You Have

✅ **TaskRouter** class in `router.py`
- Routes tasks between Phi (local) and Claude (API)
- Estimates complexity, risk, and uncertainty
- Logs all routing decisions
- Cost tracking ($0 for Phi, ~$0.003 per Claude call)

✅ **Phi-3.5-mini** running on Ollama
- `localhost:11434` (must be running: `ollama serve`)
- 1.6GB model, ~3.8B parameters
- Good for: formatting, summarizing, rewriting, routine work

✅ **Claude API** ready
- Just needs `ANTHROPIC_API_KEY` environment variable
- Used for: strategy, complex decisions, ambiguous tasks

---

## Quick Start

### 1. Start Ollama (if not running)

```bash
ollama serve
```

Runs in background. Check if working:
```bash
curl http://localhost:11434/api/generate -d '{"model":"phi","prompt":"test","stream":false}'
```

### 2. Set Claude API Key

Windows (PowerShell):
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

Or set permanently in System Environment Variables.

### 3. Use the Router

```python
from router import TaskRouter

router = TaskRouter()

# Simple usage
result = router.execute(
    "Summarize these meeting notes into bullet points",
    log=True
)

print(result['output'])
print(f"Model used: {result['model']}")
print(f"Cost: ${result['cost']}")
```

### 4. Check Routing Log

After each task, results are logged to `.learnings/ROUTING.md`:

```
| 2026-03-25 22:02 | Summarize meeting notes... | 3/10 | low | PHI | 80% | $0.0000 | Success |
```

---

## Routing Rules (Quick Reference)

| Complexity | Risk | Uncertainty | Route |
|-----------|------|-------------|-------|
| 0-3 | Any | <20% | **PHI** ✓ |
| 4-5 | Low | <50% | **PHI** ✓ |
| 6+ | Any | Any | **CLAUDE** |
| Any | High | Any | **CLAUDE** |
| Any | Any | >70% | **CLAUDE** |

---

## Example Tasks

### Route to PHI (Local, Fast, Free)
```python
# 1. Formatting
router.execute("Convert this text to a proper Word document")

# 2. Summarization
router.execute("Summarize these 10 pages into 3 bullet points")

# 3. Rewriting
router.execute("Make this email more professional")

# 4. Data entry
router.execute("Extract names and emails from this CSV")
```

### Route to CLAUDE (Strategic, Accurate, Costs ~$0.003)
```python
# 1. Strategy
router.execute("Design our new hiring process")

# 2. Analysis
router.execute("Evaluate this acquisition opportunity")

# 3. Decision
router.execute("Should we move the office?")

# 4. Complex reasoning
router.execute("How do we improve our client retention rate?")
```

---

## Integration into Mission Control

Add this to Mission Control dashboard for task execution:

```javascript
// In Mission Control, add an "Execute" button
async function executeTask(description) {
  const response = await fetch('/api/execute-task', {
    method: 'POST',
    body: JSON.stringify({ task: description })
  });
  
  const result = await response.json();
  return {
    output: result.output,
    model: result.model,
    cost: result.cost
  };
}
```

Backend (Python Flask):
```python
from router import TaskRouter

router = TaskRouter()

@app.route('/api/execute-task', methods=['POST'])
def execute_task():
    data = request.json
    result = router.execute(data['task'], log=True)
    return {
        'output': result['output'],
        'model': result['model'],
        'cost': result['cost']
    }
```

---

## Monitoring & Optimization

### Check Routing Log
```bash
cat ~/.openclaw/workspace/.learnings/ROUTING.md
```

### Monthly Analysis
1. How many tasks routed to Phi vs Claude?
2. Did Phi ever need escalation to Claude QA?
3. Total cost vs estimated savings?
4. Are routing thresholds still accurate?

### Adjust Thresholds
If too many tasks going to Claude (costing money):
- Lower complexity threshold for Phi
- Raise uncertainty tolerance

If Phi outputs too low quality:
- Raise complexity threshold for Claude
- Lower uncertainty tolerance

---

## Cost Tracking

**Monthly cost estimate:**
- Phi: $0 (runs locally)
- Claude: ~$0.30-1.00 (depends on strategic task volume)
- **Total: <$1/month** (vs ~$25 without hybrid)

---

## Troubleshooting

### "Phi is not available"
```bash
# Make sure Ollama is running
ollama serve

# Test directly
curl http://localhost:11434/api/generate -d '{"model":"phi","prompt":"test","stream":false}'
```

### "Claude API key not found"
```powershell
# Set the key
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Verify it's set
Write-Output $env:ANTHROPIC_API_KEY
```

### Routing seems wrong
- Increase/decrease complexity scores in `estimate_complexity()`
- Adjust risk keywords in `estimate_risk()`
- Check routing log to see why tasks went where they did

---

## Next Steps

1. ✅ Router created and tested
2. ⏳ Integrate into Mission Control API
3. ⏳ Add Claude API key (when ready)
4. ⏳ Start routing real work tasks
5. ⏳ Monitor cost and adjust thresholds
6. ⏳ Build specialized execution agents (ReportGenerator, EmailDrafter, etc.)

---

## Files

- `router.py` - Main TaskRouter class (500+ lines, fully functional)
- `HYBRID_ARCHITECTURE.md` - Complete system design (reference)
- `.learnings/ROUTING.md` - Auto-generated task log
