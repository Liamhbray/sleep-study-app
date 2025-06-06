#!/usr/bin/env python3
"""
Development helper scripts for AI-assisted workflow
"""

import subprocess
import sys
import os


def check_docstring_coverage():
    """Analyze docstring coverage in app.py and report gaps"""
    print("🔍 Checking docstring coverage...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Simple check for functions without docstrings
    lines = content.split('\n')
    functions = []
    missing_docs = []
    
    for i, line in enumerate(lines):
        if (line.strip().startswith('def ') and 
                not line.strip().startswith('def __')):
            func_name = line.strip().split('(')[0].replace('def ', '')
            functions.append((func_name, i+1))
            
            # Check if next few lines contain docstring
            has_docstring = False
            for j in range(i+1, min(i+5, len(lines))):
                if '"""' in lines[j] or "'''" in lines[j]:
                    has_docstring = True
                    break
            
            if not has_docstring:
                missing_docs.append((func_name, i+1))
    
    print(f"📊 Found {len(functions)} functions")
    if missing_docs:
        print(f"⚠️  Missing docstrings in {len(missing_docs)} functions:")
        for func, line in missing_docs:
            print(f"   - {func} (line {line})")
    else:
        print("✅ All functions have docstrings!")
    
    return missing_docs


def generate_ai_context_summary():
    """Report recent work and basic code metrics for AI agent context"""
    
    print("🤖 Current Context...")
    
    # Get recently modified files
    recent_files = []
    try:
        result = subprocess.run(['git', 'ls-files', '--modified'],
                                capture_output=True, text=True)
        if result.stdout:
            recent_files = result.stdout.strip().split('\n')
    except subprocess.SubprocessError:
        pass
    
    print("\n📋 Recent Work:")
    if recent_files:
        for file in recent_files[:5]:  # Show up to 5 recent files
            print(f"   - {file}")
    else:
        print("   - No modified files")
    
    # Basic code metrics from app.py
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        func_count = len([line for line in lines 
                         if line.strip().startswith('def ')])
        
        metrics = {
            'routes': content.count('@app.route'),
            'functions': func_count,
            'render_template': content.count('render_template'),
            'session_usage': content.count('session['),
            'role_checks': content.count("user.get('role')"),
            'sleep_studies_refs': content.count("'sleep_studies'")
        }
        
        print("\nCode Metrics:")
        for pattern, count in metrics.items():
            print(f"   - {pattern}: {count}")
    
    result_metrics = metrics if 'metrics' in locals() else {}
    return {'recent_files': recent_files, 'metrics': result_metrics}


def analyze_security_patterns():
    """Report security-related patterns found in code for AI analysis"""
    
    print("🔍 Security Pattern Analysis...")
    
    patterns = {}
    
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            content = f.read()
        
        patterns['session_usage'] = content.count('session[')
        patterns['role_checks'] = content.count("user.get('role')")
        patterns['csrf_mentions'] = content.lower().count('csrf')
        patterns['try_blocks'] = content.count('try:')
        patterns['error_logging'] = content.count('print(f"Error')
    
    print("📊 Security Pattern Counts:")
    for pattern, count in patterns.items():
        print(f"   - {pattern}: {count}")
    
    return patterns


def main():
    """Run development helper based on command line argument"""
    
    if len(sys.argv) < 2:
        print("""
🛠️  Codebase Analysis for AI Agents

Usage: python dev-helpers.py <command>

Commands:
  docs      - Report docstring coverage metrics
  context   - Report architectural insights and recent activity
  security  - Report security pattern counts
  all       - Run all analysis reports
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'docs':
        check_docstring_coverage()
    elif command == 'context':
        generate_ai_context_summary()
    elif command == 'security':
        analyze_security_patterns()
    elif command == 'all':
        print("🚀 Running all development checks...\n")
        check_docstring_coverage()
        print("\n" + "="*50 + "\n")
        generate_ai_context_summary()
        print("\n" + "="*50 + "\n")
        analyze_security_patterns()
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main() 