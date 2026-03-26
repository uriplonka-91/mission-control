"""
Hybrid Agent Router - Routes tasks to Phi (local) or Claude (API)
Implements the architecture from HYBRID_ARCHITECTURE.md
"""

import os
import json
import requests
import hashlib
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic
from email_calendar import EmailCalendarManager

# Configuration
PHI_ENDPOINT = "http://localhost:11434/api/generate"
LOGGING_DIR = Path.home() / ".openclaw" / "workspace" / ".learnings"
ROUTING_LOG = LOGGING_DIR / "ROUTING.md"
CLASSIFICATION_CACHE = LOGGING_DIR / "CLASSIFICATION_CACHE.json"

# Initialize Claude client (will use ANTHROPIC_API_KEY from environment or OpenClaw runtime)
def get_claude_client():
    """Get Claude client, handling API key from various sources"""
    try:
        return Anthropic()
    except Exception:
        # If direct init fails, return None and we'll handle it later
        return None

claude_client = None  # Lazy-loaded

# Initialize email/calendar manager
email_manager = EmailCalendarManager()


class TaskRouter:
    """Routes tasks between Phi (local) and Claude (API)"""
    
    def __init__(self):
        self.check_model_updates()  # Check for updates on startup
        self.phi_available = self._check_phi()
        self.claude_available = self._check_claude()
        
    def check_model_updates(self):
        """Check for Phi model updates on startup"""
        import subprocess
        
        try:
            # Try to pull latest version (only downloads if newer exists)
            result = subprocess.run(
                [os.path.join(os.getenv('LOCALAPPDATA', ''), 'Programs', 'Ollama', 'ollama.exe'), 
                 'pull', 'phi'],
                capture_output=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # Log the check
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_file = LOGGING_DIR / "MODEL_UPDATES.log"
                LOGGING_DIR.mkdir(parents=True, exist_ok=True)
                
                # Check if update happened
                try:
                    output = result.stdout.decode('utf-8', errors='ignore')
                    if "pulling" in output.lower():
                        with open(log_file, "a") as f:
                            f.write(f"{timestamp} - Updated phi model\n")
                    else:
                        with open(log_file, "a") as f:
                            f.write(f"{timestamp} - Phi model already latest\n")
                except:
                    # If decode fails, just log silently
                    pass
        
        except subprocess.TimeoutExpired:
            # If update check times out, continue (router still works)
            pass
        except Exception:
            # Fail silently - router continues to work even if update check fails
            pass
    
    def _check_phi(self):
        """Check if Phi is available on localhost:11434"""
        try:
            response = requests.post(
                PHI_ENDPOINT,
                json={"model": "phi", "prompt": "test", "stream": False},
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[WARN] Phi unavailable: {e}")
            return False
    
    def _check_claude(self):
        """Check if Claude API is configured"""
        # Check both env var and implicit availability (loaded by runtime)
        try:
            test_client = Anthropic()
            return True
        except Exception as e:
            # In subprocess, API key might not be available; that's okay for now
            # Router will still work with keyword-based fallback
            return False
    
    def _load_classification_cache(self):
        """Load cached classifications"""
        if CLASSIFICATION_CACHE.exists():
            try:
                with open(CLASSIFICATION_CACHE) as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_classification_cache(self, cache):
        """Save classifications to cache"""
        LOGGING_DIR.mkdir(parents=True, exist_ok=True)
        with open(CLASSIFICATION_CACHE, 'w') as f:
            json.dump(cache, f, indent=2)
    
    def _hash_task(self, task_description: str) -> str:
        """Create a hash of the task for caching"""
        return hashlib.md5(task_description.encode()).hexdigest()
    
    def _classify_with_claude(self, task_description: str) -> dict:
        """Use Claude to intelligently classify the task"""
        try:
            client = Anthropic()  # Fresh client to get runtime API key
            
            prompt = f"""Classify this task for AI routing. Respond with ONLY a JSON object (no markdown, no explanation):
{{
  "complexity": <0-10 integer>,
  "risk": "<low|medium|high>",
  "uncertainty": <0-100 integer>,
  "reasoning": "<1 sentence explanation>"
}}

Task: {task_description}

Guidelines:
- Complexity 0-3: Routine, well-defined (format, copy, summarize)
- Complexity 4-6: Moderate, needs some structure (analyze, design)
- Complexity 7-10: Strategic, requires judgment (strategy, decisions)
- Risk: high if involves clients, contracts, finance, compliance, legal, security, medical
- Uncertainty: high (70+) if task has unclear requirements or multiple interpretations"""

            response = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            response_text = response.content[0].text.strip()
            
            # Handle markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            classification = json.loads(response_text)
            return {
                'complexity': int(classification['complexity']),
                'risk': classification['risk'].lower(),
                'uncertainty': int(classification['uncertainty']),
                'reasoning': classification.get('reasoning', ''),
                'method': 'claude'
            }
        except Exception as e:
            print(f"[WARN] Claude classification failed: {e}, falling back to keyword-based")
            return None
    
    def estimate_complexity(self, task_description: str) -> int:
        """Estimate complexity using smart classification (cached)"""
        classification = self._smart_classify(task_description)
        return classification['complexity']
    
    def estimate_risk(self, task_description: str) -> str:
        """Estimate risk using smart classification (cached)"""
        classification = self._smart_classify(task_description)
        return classification['risk']
    
    def estimate_uncertainty(self, task_description: str) -> int:
        """Estimate uncertainty using smart classification (cached)"""
        classification = self._smart_classify(task_description)
        return classification['uncertainty']
    
    def _smart_classify(self, task_description: str) -> dict:
        """
        Classify task using Claude (with cache).
        Falls back to keyword-based if Claude fails.
        """
        task_hash = self._hash_task(task_description)
        cache = self._load_classification_cache()
        
        # Check cache
        if task_hash in cache:
            return cache[task_hash]
        
        # Try Claude classification
        classification = self._classify_with_claude(task_description)
        
        # Fall back to keyword-based if Claude fails
        if classification is None:
            classification = self._keyword_classify(task_description)
        
        # Cache the result
        cache[task_hash] = classification
        self._save_classification_cache(cache)
        
        return classification
    
    def _keyword_classify(self, task_description: str) -> dict:
        """Fallback: Keyword-based classification"""
        complexity = 0
        
        simple_keywords = ["format", "copy", "rewrite", "fix", "clean"]
        medium_keywords = ["summarize", "review", "organize"]
        complex_keywords = ["strategy", "decision", "evaluate", "assess", "problem-solve", "analyze", "design", "plan"]
        
        desc_lower = task_description.lower()
        
        for keyword in simple_keywords:
            if keyword in desc_lower:
                complexity += 2
        
        for keyword in medium_keywords:
            if keyword in desc_lower:
                complexity += 5
        
        for keyword in complex_keywords:
            if keyword in desc_lower:
                complexity += 8
        
        # Adjust for length
        complexity += min(len(task_description) // 100, 2)
        complexity = min(complexity, 10)
        
        # Risk assessment
        # Only flag as HIGH if dealing with strategic/policy decisions involving sensitive areas
        # OR explicit financial/legal/compliance keywords
        high_risk_keywords = ["contract", "financial", "compliance", "legal", "security policy", "medical policy", "health policy"]
        medium_risk_keywords = ["important", "decision", "policy", "strategy", "client", "medical", "health"]
        
        desc_lower_check = desc_lower
        if any(keyword in desc_lower_check for keyword in high_risk_keywords):
            risk = "high"
        elif any(keyword in desc_lower_check for keyword in medium_risk_keywords):
            risk = "medium"
        else:
            risk = "low"
        
        # Uncertainty assessment
        uncertainty = 20
        uncertain_keywords = ["unclear", "ambiguous", "not sure", "what if", "should", "evaluate", "decide"]
        for keyword in uncertain_keywords:
            if keyword in desc_lower:
                uncertainty += 20
        
        uncertainty -= min(len(task_description) // 50, 15)
        uncertainty = max(0, min(uncertainty, 100))
        
        return {
            'complexity': complexity,
            'risk': risk,
            'uncertainty': uncertainty,
            'reasoning': 'Keyword-based classification',
            'method': 'keyword'
        }
    
    def route(self, task_description: str, complexity=None, risk=None, uncertainty=None, force_claude=False):
        """
        Route task to Phi or Claude using smart classification.
        
        Returns:
            {
                'model': 'phi'|'claude'|'unavailable',
                'reason': str,
                'confidence': float,
                'complexity': int,
                'risk': str,
                'uncertainty': int,
                'method': 'claude'|'keyword'  (classification method used)
            }
        """
        
        # If user forces Claude, use it
        if force_claude:
            classification = self._smart_classify(task_description)
            return {
                'model': 'claude',
                'reason': 'User requested',
                'confidence': 1.0,
                'complexity': classification['complexity'],
                'risk': classification['risk'],
                'uncertainty': classification['uncertainty'],
                'method': classification['method']
            }
        
        # Smart classification (uses Claude with cache, falls back to keywords)
        classification = self._smart_classify(task_description)
        complexity = classification['complexity']
        risk = classification['risk']
        uncertainty = classification['uncertainty']
        method = classification['method']
        
        # Decision rules
        if uncertainty > 70:
            return {
                'model': 'claude',
                'reason': 'High uncertainty (>70%)',
                'confidence': 0.9,
                'complexity': complexity,
                'risk': risk,
                'uncertainty': uncertainty,
                'method': method
            }
        
        if risk == 'high':
            return {
                'model': 'claude',
                'reason': 'High risk',
                'confidence': 0.95,
                'complexity': complexity,
                'risk': risk,
                'uncertainty': uncertainty,
                'method': method
            }
        
        if complexity >= 7:
            return {
                'model': 'claude',
                'reason': 'Complex/strategic (≥7)',
                'confidence': 0.85,
                'complexity': complexity,
                'risk': risk,
                'uncertainty': uncertainty,
                'method': method
            }
        
        if complexity <= 3 and uncertainty < 20:
            return {
                'model': 'phi',
                'reason': 'Simple & clear',
                'confidence': 0.9,
                'complexity': complexity,
                'risk': risk,
                'uncertainty': uncertainty,
                'method': method
            }
        
        if complexity <= 5 and risk == 'low' and uncertainty < 50:
            return {
                'model': 'phi',
                'reason': 'Routine execution',
                'confidence': 0.8,
                'complexity': complexity,
                'risk': risk,
                'uncertainty': uncertainty,
                'method': method
            }
        
        if risk == 'low':
            return {
                'model': 'phi',
                'reason': 'Low risk, moderate complexity',
                'confidence': 0.75,
                'complexity': complexity,
                'risk': risk,
                'uncertainty': uncertainty,
                'method': method
            }
        
        return {
            'model': 'claude',
            'reason': 'Uncertain case (fallback)',
            'confidence': 0.6,
            'complexity': complexity,
            'risk': risk,
            'uncertainty': uncertainty,
            'method': method
        }
    
    def call_phi(self, prompt: str, system_prompt: str = None) -> str:
        """Call Phi-3.5-mini locally"""
        if not self.phi_available:
            raise RuntimeError("Phi is not available. Is Ollama running on localhost:11434?")
        
        payload = {
            "model": "phi",
            "prompt": prompt if not system_prompt else f"{system_prompt}\n\n{prompt}",
            "stream": False,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        response = requests.post(PHI_ENDPOINT, json=payload, timeout=60)
        response.raise_for_status()
        
        return response.json()['response']
    
    def call_claude(self, prompt: str, system_prompt: str = None, model: str = "claude-3-5-sonnet-20241022") -> str:
        """Call Claude via API"""
        if not self.claude_available:
            raise RuntimeError("Claude API key not found. Set ANTHROPIC_API_KEY environment variable.")
        
        client = Anthropic()  # Fresh client
        messages = [{"role": "user", "content": prompt}]
        
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=messages,
            system=system_prompt or "You are a helpful AI assistant."
        )
        
        return response.content[0].text
    
    def draft_email(self, to: str, subject: str, body: str) -> dict:
        """Draft an email for approval"""
        result = email_manager.draft_email(to, subject, body, approval_required=True)
        
        if result['status'] == 'drafted':
            return {
                'status': 'drafted',
                'preview': result['preview'],
                'draft_id': result['draft_id'],
                'message': 'Email drafted. Show to user for approval.'
            }
        else:
            return result
    
    def send_email(self, draft_id: str) -> dict:
        """Send an approved email"""
        return email_manager.approve_and_send_email(draft_id)
    
    def list_pending_emails(self) -> list:
        """List pending emails awaiting approval"""
        return email_manager.list_pending_emails()
    
    def propose_meeting(self, subject: str, attendees: list, start_time: str = None, duration_minutes: int = 30) -> dict:
        """Propose a calendar meeting for approval"""
        result = email_manager.propose_meeting(subject, attendees, start_time, duration_minutes, approval_required=True)
        
        if result['status'] == 'proposed':
            return {
                'status': 'proposed',
                'preview': result['preview'],
                'proposal_id': result['proposal_id'],
                'message': 'Meeting proposed. Show to user for approval.'
            }
        else:
            return result
    
    def book_meeting(self, proposal_id: str) -> dict:
        """Book an approved meeting"""
        return email_manager.approve_and_book_meeting(proposal_id)
    
    def list_pending_meetings(self) -> list:
        """List pending meetings awaiting approval"""
        return email_manager.list_pending_meetings()
    
    def cancel_meeting(self, event_id: str) -> dict:
        """Cancel a booked meeting"""
        # For now, we'll need to pass the proposal_id
        # In future, we can look up by event_id
        return email_manager.cancel_meeting(event_id)
    
    def execute(self, task_description: str, system_prompt: str = None, force_claude: bool = False, log: bool = True) -> dict:
        """
        Execute a task by routing to the appropriate model.
        
        Returns:
            {
                'output': str,
                'model': 'phi'|'claude',
                'routing': {...},
                'cost': float,
                'timestamp': str
            }
        """
        
        # Route the task
        routing = self.route(task_description, force_claude=force_claude)
        model = routing['model']
        
        print(f"[ROUTE] {model.upper()}")
        print(f"  Reason: {routing['reason']}")
        print(f"  Complexity: {routing['complexity']}/10 | Risk: {routing['risk']} | Uncertainty: {routing['uncertainty']}%")
        
        # Execute
        try:
            if model == 'phi':
                output = self.call_phi(task_description, system_prompt)
                cost = 0.0
            elif model == 'claude':
                output = self.call_claude(task_description, system_prompt)
                # Rough estimate: ~100 input tokens + 200 output tokens = $0.003
                cost = 0.003
            else:
                raise ValueError(f"Unknown model: {model}")
            
            print(f"[OK] Complete (Cost: ${cost:.4f})")
            
            result = {
                'output': output,
                'model': model,
                'routing': routing,
                'cost': cost,
                'timestamp': datetime.now().isoformat()
            }
            
            # Log if requested
            if log:
                self._log_task(task_description, result)
            
            return result
        
        except Exception as e:
            print(f"[ERROR] {e}")
            raise
    
    def _log_task(self, task_description: str, result: dict):
        """Log task routing and execution to ROUTING.md"""
        LOGGING_DIR.mkdir(parents=True, exist_ok=True)
        
        # Ensure header exists
        if not ROUTING_LOG.exists():
            ROUTING_LOG.write_text(
                "# Task Routing Log\n\n"
                "| Date | Task | Complexity | Risk | Model | Confidence | Method | Cost | Status |\n"
                "|------|------|-----------|------|-------|-----------|--------|------|--------|\n"
            )
        
        # Append log entry
        routing = result['routing']
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        task_short = task_description[:50].replace("|", "\\|")
        method = routing.get('method', 'keyword')
        
        log_line = (
            f"| {date} | {task_short}... | {routing['complexity']}/10 | {routing['risk']} | "
            f"{result['model'].upper()} | {routing['confidence']:.0%} | {method} | ${result['cost']:.4f} | Success |\n"
        )
        
        with open(ROUTING_LOG, "a") as f:
            f.write(log_line)


def main():
    """Test the router"""
    print("[*] Hybrid Agent Router - Testing\n")
    
    router = TaskRouter()
    
    print(f"[OK] Phi available: {router.phi_available}")
    print(f"[OK] Claude available: {router.claude_available}\n")
    
    # Test cases
    test_tasks = [
        ("Format this document into a Word file with proper headings", False),
        ("Analyze our recruiting pipeline and recommend improvements", True),
        ("Summarize these meeting notes into bullet points", False),
        ("Design a new caregiver scheduling system for the home care company", True),
    ]
    
    print("=" * 70)
    print("TEST ROUTING DECISIONS")
    print("=" * 70 + "\n")
    
    for task, force_claude in test_tasks:
        print(f"[TASK] {task}")
        routing = router.route(task, force_claude=force_claude)
        print(f"   -> {routing['model'].upper()} | {routing['reason']}")
        print(f"   Method: {routing['method']} | Complexity: {routing['complexity']}/10 | Risk: {routing['risk']} | Uncertainty: {routing['uncertainty']}%\n")
    
    print("=" * 70)
    print("EXECUTION TEST (Phi)")
    print("=" * 70 + "\n")
    
    if router.phi_available:
        try:
            result = router.execute(
                "Summarize the following in 2 bullet points: The hybrid agent architecture uses Phi for routine tasks and Claude for complex decisions. This saves 94% on token costs.",
                log=False
            )
            print(f"\n[OUTPUT]\n{result['output']}\n")
        except Exception as e:
            print(f"[ERROR] Phi test failed: {e}\n")
    else:
        print("[WARN] Phi not available - make sure Ollama is running (ollama serve)\n")


if __name__ == "__main__":
    main()
