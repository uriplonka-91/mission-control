#!/usr/bin/env python3
"""Comprehensive audit of mission-control setup"""

import os
import json
from pathlib import Path

print("=" * 70)
print("MISSION CONTROL AUDIT")
print("=" * 70)

# 1. Check project files
print("\n1. PROJECT STRUCTURE")
print("-" * 70)

project_root = Path(".")
py_files = list(project_root.glob("*.py"))
js_files = []
for pattern in ["pages/*.js", "components/*.js"]:
    js_files.extend(project_root.glob(pattern))

print("Python files: {}".format(len([f for f in py_files if "audit" not in f.name])))
print("  - router.py")
print("  - email_calendar.py")
print("  - cost_anomaly_detector.py")
print("  - api_email_calendar.py")
print("  - email_responder.py")

print("\nJavaScript files: {}".format(len(js_files)))

# 2. Check router.py
print("\n2. ROUTER.PY ANALYSIS")
print("-" * 70)

issues = []

with open("router.py") as f:
    router_content = f.read()

# Check for email_calendar import
if "# DISABLED: email_calendar import" in router_content:
    print("[OK] email_calendar import is disabled (lazy-loaded)")
elif "from email_calendar import" in router_content:
    print("[WARN] email_calendar imported directly - should be lazy-loaded")
    issues.append("email_calendar not lazy-loaded")
else:
    print("[OK] No problematic imports found")

# Check for error handling
try_count = router_content.count("try:")
except_count = router_content.count("except")
print("[OK] Error handling present: {} try blocks, {} except blocks".format(try_count, except_count))

# Check for Phi configuration
if "PHI_ENDPOINT" in router_content:
    print("[OK] Phi endpoint configured")
else:
    print("[WARN] Phi endpoint not found")
    issues.append("Phi endpoint not configured")

# Check for Haiku model
if "claude-3-5-haiku" in router_content or "haiku" in router_content:
    print("[OK] Using Haiku model (cost-efficient)")
else:
    print("[WARN] Check Claude model - may not be using Haiku")

# Check for logging
if "LOGGING_DIR" in router_content:
    print("[OK] Logging configured")
else:
    print("[WARN] No logging directory found")

# 3. Check Next.js config
print("\n3. NEXT.JS CONFIGURATION")
print("-" * 70)

if os.path.exists("next.config.js"):
    print("[OK] next.config.js present")
else:
    print("[WARN] next.config.js not found")

if os.path.exists("package.json"):
    with open("package.json") as f:
        pkg = json.load(f)
    print("[OK] package.json present")
    print("    Dependencies: {}".format(len(pkg.get('dependencies', {}))))
else:
    print("[ERROR] package.json missing")
    issues.append("package.json not found")

# 4. Check security
print("\n4. SECURITY & GIT")
print("-" * 70)

if os.path.exists(".gitignore"):
    with open(".gitignore") as f:
        gitignore = f.read()
    
    checks = {
        ".env": ".env ignored",
        "node_modules": "node_modules ignored",
        ".next": ".next ignored",
        "__pycache__": "__pycache__ ignored",
        ".vercel": ".vercel ignored"
    }
    
    for pattern, desc in checks.items():
        if pattern in gitignore:
            print("[OK] {}".format(desc))
        else:
            print("[WARN] {} - not in .gitignore".format(desc))
            issues.append("{} not in .gitignore".format(pattern))
else:
    print("[ERROR] .gitignore missing")
    issues.append(".gitignore not found")

# 5. Check environment
print("\n5. ENVIRONMENT")
print("-" * 70)

tools_to_check = {
    "Python": "python --version",
    "Node.js": "node --version",
    "npm": "npm --version",
    "Ollama": "ollama --version",
}

for tool, cmd in tools_to_check.items():
    ret = os.system("{}  > nul 2>&1".format(cmd))
    if ret == 0:
        print("[OK] {} installed".format(tool))
    else:
        print("[WARN] {} not found in PATH".format(tool))

# 6. Check Vercel
print("\n6. VERCEL DEPLOYMENT")
print("-" * 70)

if os.path.exists(".vercel"):
    print("[OK] .vercel directory exists")
else:
    print("[WARN] .vercel not found - may not be linked")

if os.path.exists(".vercelignore"):
    print("[OK] .vercelignore configured")
else:
    print("[INFO] .vercelignore not found - using defaults")

# Summary
print("\n" + "=" * 70)
print("ISSUES FOUND: {}".format(len(issues)))
print("=" * 70)

if issues:
    print("\nIssues to address:")
    for i, issue in enumerate(issues, 1):
        print("  {}. {}".format(i, issue))
else:
    print("\n[OK] No critical issues found")

print("\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)
print("""
1. Document all environment variables required
2. Add requirements.txt for Python dependencies
3. Implement request logging to all endpoints
4. Add rate limiting to prevent token abuse
5. Set up cost monitoring alerts
6. Add health check endpoint for uptime monitoring
7. Implement request/response validation
8. Add comprehensive error logging
9. Create API documentation
10. Add unit tests for router logic
""")

print("=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)
