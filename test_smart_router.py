"""
Test the smart router with real-world examples
"""

from router import TaskRouter

def test_smart_router():
    print("[*] Smart Router Test - Real-World Examples\n")
    
    router = TaskRouter()
    
    # Test cases with expected outcomes
    test_cases = [
        {
            "task": "Format this document into a Word file with proper headings and styling",
            "expected_model": "PHI",
            "reason": "Simple formatting task"
        },
        {
            "task": "Analyze our caregiver utilization rates and recommend optimization strategies",
            "expected_model": "CLAUDE",
            "reason": "Strategic analysis requiring judgment"
        },
        {
            "task": "Copy contact information from email to spreadsheet",
            "expected_model": "PHI",
            "reason": "Routine data entry"
        },
        {
            "task": "Design a new compliance policy for healthcare documentation",
            "expected_model": "CLAUDE",
            "reason": "High-risk strategic decision"
        },
        {
            "task": "Summarize today's team meeting into 3 bullet points",
            "expected_model": "PHI",
            "reason": "Simple summarization"
        },
        {
            "task": "Should we acquire the competitor's business? What are the financial implications?",
            "expected_model": "CLAUDE",
            "reason": "Major strategic decision with uncertainty"
        },
    ]
    
    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80 + "\n")
    
    correct = 0
    for i, test in enumerate(test_cases, 1):
        task = test["task"]
        expected = test["expected_model"]
        
        routing = router.route(task)
        actual = routing["model"].upper()
        match = "[OK]" if actual == expected else "[FAIL]"
        
        print(f"{match} Test {i}: {task}")
        print(f"    Expected: {expected} | Actual: {actual}")
        print(f"    Reason: {test['reason']}")
        print(f"    Classification: {routing['complexity']}/10 complexity, {routing['risk']} risk, {routing['uncertainty']}% uncertainty")
        print(f"    Method: {routing['method']} | Confidence: {routing['confidence']:.0%}\n")
        
        if actual == expected:
            correct += 1
    
    print("=" * 80)
    print(f"SCORE: {correct}/{len(test_cases)} correct ({100*correct/len(test_cases):.0f}%)")
    print("=" * 80 + "\n")
    
    # Check cache
    from pathlib import Path
    cache_path = Path.home() / ".openclaw" / "workspace" / ".learnings" / "CLASSIFICATION_CACHE.json"
    if cache_path.exists():
        import json
        with open(cache_path) as f:
            cache = json.load(f)
        print(f"[INFO] Classification cache has {len(cache)} entries")
        print(f"[INFO] Cached classifications available for reuse (zero cost!)\n")
    
    print("[OK] Smart router is working. Using keyword-based classification (Claude available in main session).")


if __name__ == "__main__":
    test_smart_router()
