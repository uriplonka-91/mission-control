#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive audit of mission-control setup
Checks code quality, architecture, security, and best practices
"""

import os
import json
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

print("=" * 70)
print("MISSION CONTROL AUDIT")
print("=" * 70)

# Check project structure
print("\n1. PROJECT STRUCTURE")
print("-" * 70)

project_root = Path(".")
py_files = list(project_root.glob("*.py"))
js_files = list(project_root.glob("pages/*.js")) + list(project_root.glob("components/*.js"))
config_files = list(project_root.glob("*.json"))

print(f"Python files: {len(py_files)}")
for f in sorted(py_files):
    print(f"  - {f.name}")

print(f"\nJavaScript files: {len(js_files)}")
for f in sorted(js_files):
    print(f"  - {f}")

print(f"\nConfig files: {len(config_files)}")
for f in sorted(config_files):
    if f.name != 'package-lock.json':
        print(f"  - {f.name}")

# Check router.py for issues
print("\n2. ROUTER.PY ANALYSIS")
print("-" * 70)

with open("router.py") as f:
    router_content = f.read()

issues = []

# Check for hardcoded credentials
if "api_key" in router_content and "=" in router_content:
    print("WARNING: Check for hardcoded credentials")
    issues.append("Potential hardcoded credentials")

# Check for proper error handling
if "try:" not in router_content:
    print("WARNING: No error handling found")
    issues.append("Insufficient error handling")
else:
    print("[OK] Error handling present")

# Check for lazy loading
if "def get_" in router_content and "global" in router_content:
    print("✓ Lazy loading pattern detected")
else:
    print("WARNING: Check lazy loading implementation")
    issues.append("May not use lazy loading properly")

# Check imports
if "from email_calendar import" in router_content:
    print("WARNING: Direct email_calendar import (should be lazy-loaded)")
    issues.append("email_calendar not lazy-loaded")
elif "# DISABLED: email_calendar import" in router_content:
    print("✓ email_calendar properly disabled/lazy-loaded")

# Check model configuration
if "PHI_ENDPOINT" in router_content and "localhost:11434" in router_content:
    print("✓ Phi endpoint configured correctly")
else:
    print("WARNING: Phi endpoint not found")
    issues.append("Phi endpoint configuration missing")

if "claude-3-5-haiku" in router_content:
    print("✓ Using Haiku model (cost-efficient)")
else:
    print("WARNING: Check Claude model selection")
    issues.append("May not be using cost-efficient model")

# Check for logging
if "ROUTING_LOG" in router_content or "CLASSIFICATION_CACHE" in router_content:
    print("✓ Logging and caching configured")
else:
    print("WARNING: No logging/caching found")
    issues.append("Logging/caching not configured")

# Check Next.js configuration
print("\n3. NEXT.JS CONFIGURATION")
print("-" * 70)

if os.path.exists("next.config.js"):
    with open("next.config.js") as f:
        next_config = f.read()
    print("✓ next.config.js present")
    if "python" in next_config.lower():
        print("✓ Python API routing configured")
else:
    print("⚠ next.config.js not found (may use defaults)")

if os.path.exists("package.json"):
    with open("package.json") as f:
        pkg = json.load(f)
    print(f"✓ Next.js version: {pkg.get('dependencies', {}).get('next', 'unknown')}")
    print(f"✓ React version: {pkg.get('dependencies', {}).get('react', 'unknown')}")
    if "vercel" in pkg.get("dependencies", {}):
        print("✓ Vercel SDK installed")
else:
    print("ERROR: package.json not found")
    issues.append("package.json missing")

# Check environment setup
print("\n4. ENVIRONMENT & DEPENDENCIES")
print("-" * 70)

required_tools = {
    "Ollama": "ollama.exe",
    "Python": "python.exe",
    "Node.js": "node.exe",
    "npm": "npm.cmd",
    "Vercel CLI": "vercel.cmd"
}

for tool, exe in required_tools.items():
    found = os.system(f"where {exe} >nul 2>&1") == 0
    status = "✓" if found else "⚠"
    print(f"{status} {tool}")
    if not found and tool != "Vercel CLI":
        issues.append(f"{tool} not in PATH")

# Check Vercel deployment config
print("\n5. VERCEL DEPLOYMENT")
print("-" * 70)

if os.path.exists(".vercel"):
    print("✓ .vercel directory exists (project linked)")
else:
    print("⚠ .vercel directory not found")

if os.path.exists(".vercelignore"):
    print("✓ .vercelignore configured")
else:
    print("⚠ .vercelignore not found (using defaults)")

# Check for sensitive files in git
print("\n6. SECURITY - GIT CONFIGURATION")
print("-" * 70)

if os.path.exists(".gitignore"):
    with open(".gitignore") as f:
        gitignore = f.read()
    
    important_ignores = [".env", "node_modules", ".next", "__pycache__", ".vercel"]
    for pattern in important_ignores:
        if pattern in gitignore:
            print(f"✓ {pattern} ignored")
        else:
            print(f"⚠ {pattern} not in .gitignore")
            issues.append(f"{pattern} not properly ignored")
else:
    print("ERROR: .gitignore missing")
    issues.append(".gitignore not found")

# Summary
print("\n" + "=" * 70)
print("AUDIT SUMMARY")
print("=" * 70)

if issues:
    print(f"\nFound {len(issues)} issue(s):")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
else:
    print("\n✓ No critical issues found")

print("\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)

recommendations = [
    "1. Review router.py for any hardcoded values or secrets",
    "2. Ensure all Python dependencies are in requirements.txt",
    "3. Add API rate limiting to prevent token abuse",
    "4. Implement request logging for cost tracking",
    "5. Add health check endpoints for monitoring",
    "6. Use environment variables for all configuration",
    "7. Document API endpoints and response formats",
    "8. Set up monitoring/alerting for cost anomalies",
    "9. Implement caching layer for expensive operations",
    "10. Add unit tests for router logic"
]

for rec in recommendations:
    print(f"  {rec}")

print("\n" + "=" * 70)
