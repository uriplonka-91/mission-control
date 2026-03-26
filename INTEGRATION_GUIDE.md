# Integration Guide - Using the Smart Router

## Quick Start

### 1. Use it in Python
```python
from router import TaskRouter

router = TaskRouter()

# Execute a task
result = router.execute(
    "Analyze our recruiting pipeline and recommend improvements",
    log=True  # Optional: log to ROUTING.md
)

print(result['output'])
print(f"Model: {result['model']}")
print(f"Cost: ${result['cost']:.4f}")
```

### 2. Check Logs
```bash
# See all routing decisions
cat ~/.openclaw/workspace/.learnings/ROUTING.md

# See classification cache
cat ~/.openclaw/workspace/.learnings/CLASSIFICATION_CACHE.json
```

---

## Integration into Mission Control (Web Dashboard)

### Backend (Python API)

Create `api/routes.py`:
```python
from flask import Flask, request, jsonify
from router import TaskRouter

app = Flask(__name__)
router = TaskRouter()

@app.route('/api/execute-task', methods=['POST'])
def execute_task():
    """Execute a task and return result"""
    data = request.json
    
    result = router.execute(
        task_description=data['task'],
        force_claude=data.get('force_claude', False),
        log=True
    )
    
    return jsonify({
        'output': result['output'],
        'model': result['model'],
        'cost': result['cost'],
        'complexity': result['routing']['complexity'],
        'risk': result['routing']['risk'],
        'uncertainty': result['routing']['uncertainty'],
        'method': result['routing']['method']
    })

@app.route('/api/classify-task', methods=['POST'])
def classify_task():
    """Just classify a task without executing"""
    data = request.json
    
    routing = router.route(data['task'])
    
    return jsonify(routing)
```

### Frontend (React Component)

Create `components/TaskExecutor.js`:
```javascript
import React, { useState } from 'react';

export default function TaskExecutor() {
  const [task, setTask] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [forceClaude, setForceClaude] = useState(false);

  const handleExecute = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/execute-task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task,
          force_claude: forceclaude
        })
      });
      const data = await response.json();
      setResult(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Task Executor</h2>
      
      <textarea
        value={task}
        onChange={(e) => setTask(e.target.value)}
        placeholder="Describe the task..."
        className="w-full p-3 border rounded mb-4"
        rows="3"
      />
      
      <label className="flex items-center mb-4">
        <input
          type="checkbox"
          checked={forceClause}
          onChange={(e) => setForceClause(e.target.checked)}
          className="mr-2"
        />
        Force Claude execution
      </label>
      
      <button
        onClick={handleExecute}
        disabled={loading || !task}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Executing...' : 'Execute Task'}
      </button>
      
      {result && (
        <div className="mt-6 p-4 bg-gray-100 rounded">
          <p className="font-bold mb-2">Result:</p>
          <p className="mb-4">{result.output}</p>
          
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>Model: <strong>{result.model}</strong></div>
            <div>Cost: <strong>${result.cost.toFixed(4)}</strong></div>
            <div>Complexity: <strong>{result.complexity}/10</strong></div>
            <div>Risk: <strong>{result.risk}</strong></div>
            <div>Uncertainty: <strong>{result.uncertainty}%</strong></div>
            <div>Method: <strong>{result.method}</strong></div>
          </div>
        </div>
      )}
    </div>
  );
}
```

### Add to Mission Control Dashboard

In `pages/index.js`:
```javascript
import TaskExecutor from '../components/TaskExecutor';

export default function Dashboard() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Dashboard />
      <TaskExecutor />  {/* NEW */}
    </div>
  );
}
```

---

## Command-Line Usage

### Execute a Task
```bash
python -c "
from router import TaskRouter
router = TaskRouter()
result = router.execute('Summarize meeting notes into bullet points', log=True)
print(result['output'])
"
```

### Check Classification for a Task
```bash
python -c "
from router import TaskRouter
router = TaskRouter()
routing = router.route('Your task here')
print(f\"Complexity: {routing['complexity']}/10\")
print(f\"Risk: {routing['risk']}\")
print(f\"Route: {routing['model'].upper()}\")
"
```

### View Cache Stats
```bash
python -c "
import json
from pathlib import Path
cache_path = Path.home() / '.openclaw/workspace/.learnings/CLASSIFICATION_CACHE.json'
with open(cache_path) as f:
    cache = json.load(f)
print(f'Cached classifications: {len(cache)}')
"
```

---

## Monitoring & Observability

### Key Metrics to Track

1. **Classification Cache Hit Rate**
   - How many tasks reuse cached classifications?
   - Target: >70% after 2 weeks

2. **Routing Accuracy**
   - Monitor ROUTING.md for misroutes
   - Track if Phi output quality is acceptable
   - Adjust thresholds if needed

3. **Cost per Task**
   - Should be <$0.001 after cache hits
   - Monitor actual costs vs estimates

4. **Model Distribution**
   - % of tasks going to Phi vs Claude
   - Target: ~70% Phi, ~30% Claude

### Sample Monitoring Script
```python
import json
from pathlib import Path
from datetime import datetime, timedelta

# Load cache
cache_path = Path.home() / '.openclaw/workspace/.learnings/CLASSIFICATION_CACHE.json'
with open(cache_path) as f:
    cache = json.load(f)

# Load routing log
log_path = Path.home() / '.openclaw/workspace/.learnings/ROUTING.md'
lines = log_path.read_text().split('\n')[2:]  # Skip header

# Parse log
phi_count = 0
claude_count = 0
total_cost = 0.0

for line in lines:
    if '|' in line:
        parts = [p.strip() for p in line.split('|')]
        if len(parts) > 5:
            model = parts[5].upper()
            cost = float(parts[8].replace('$', ''))
            
            phi_count += 1 if model == 'PHI' else 0
            claude_count += 1 if model == 'CLAUDE' else 0
            total_cost += cost

# Report
total_tasks = phi_count + claude_count
print(f"Total tasks: {total_tasks}")
print(f"Phi: {phi_count} ({100*phi_count/total_tasks:.0f}%)")
print(f"Claude: {claude_count} ({100*claude_count/total_tasks:.0f}%)")
print(f"Total cost: ${total_cost:.4f}")
print(f"Cache size: {len(cache)} classifications")
print(f"Cache hit potential: ~${total_tasks * 0.0001:.4f} (if all were cache hits)")
```

---

## Troubleshooting

### "Claude classification failed"
This is OK—router falls back to keyword-based classification.

To use Claude again:
1. Ensure `ANTHROPIC_API_KEY` is set
2. Restart the process
3. Try again

### Classification seems wrong
1. Check the reasoning in cache:
   ```python
   import json
   cache = json.load(open('...CLASSIFICATION_CACHE.json'))
   # Find your task and check 'reasoning' field
   ```

2. Check the routing log for decisions:
   ```bash
   grep "your task" ~/.openclaw/workspace/.learnings/ROUTING.md
   ```

3. Adjust keyword lists in `_keyword_classify()` if needed

### Cache growing too large
Cache file should stay <10MB. To reset:
```bash
rm ~/.openclaw/workspace/.learnings/CLASSIFICATION_CACHE.json
```

---

## Advanced: Custom Classification

If you want to manually classify a task:

```python
from router import TaskRouter

router = TaskRouter()

# Manual classification override
result = router.execute(
    "Some task",
    complexity=8,  # Override
    risk="high",   # Override
    uncertainty=50 # Override
)
```

Or force to specific model:
```python
result = router.execute(
    "Some task",
    force_claude=True  # Always use Claude
)
```

---

## Performance Notes

- **Classification time:** ~500ms (Claude Haiku)
- **Cache lookup:** <1ms
- **Phi execution:** 1-5s depending on task
- **Claude execution:** 2-10s depending on task

With caching, you're mainly paying for Phi/Claude execution, not classification.

---

## Next Phase

When ready:
1. Integrate into Mission Control dashboard
2. Add "Force Claude" button for manual overrides
3. Build analytics dashboard showing routing stats
4. Set up alerts if cost exceeds threshold
5. Implement A/B testing for routing thresholds

---

## Support

For issues:
1. Check ROUTING.md for decision logs
2. Check CLASSIFICATION_CACHE.json for cached decisions
3. Check router.py source code (well-commented)
4. Review test cases in test_smart_router.py
