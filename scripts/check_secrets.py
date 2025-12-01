#!/usr/bin/env python3
"""
ZeroSite v7.1 - Secrets Scanner
Scans codebase for hardcoded API keys and secrets
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Patterns to detect secrets
SECRET_PATTERNS = [
    # API Keys
    (r'api[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9]{20,})["\']', "API Key"),
    (r'secret[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9]{20,})["\']', "Secret Key"),
    (r'access[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9]{20,})["\']', "Access Key"),
    
    # Specific API Keys
    (r'kakao[_-]?api[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9]{20,})["\']', "Kakao API Key"),
    (r'AIza[0-9A-Za-z\-_]{35}', "Google API Key"),
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
    
    # OAuth Tokens
    (r'[0-9a-fA-F]{40}', "Generic Token (40 hex)"),
    
    # JWT Tokens
    (r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', "JWT Token"),
    
    # Database URLs with passwords
    (r'(postgres|mysql|mongodb)://[^:]+:([^@]+)@', "Database Password"),
    
    # Private Keys
    (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', "Private Key"),
]

# Files to exclude
EXCLUDE_PATTERNS = [
    r'\.git/',
    r'__pycache__/',
    r'\.pyc$',
    r'node_modules/',
    r'venv/',
    r'\.venv/',
    r'dist/',
    r'build/',
    r'\.egg-info/',
    r'\.env\.example$',  # Template is OK
    r'SECURITY_SETUP\.md$',  # Documentation is OK
    r'check_secrets\.py$',  # This script is OK
    r'test_.*\.py$',  # Test files with test fixtures are OK
    r'conftest\.py$',  # Test configuration is OK
]

# Directories to scan
SCAN_DIRS = [
    'app/',
    'scripts/',
    'tests/',
    'static/',
]


def should_exclude(file_path: str) -> bool:
    """Check if file should be excluded from scanning"""
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, file_path):
            return True
    return False


def scan_file(file_path: str) -> List[Tuple[int, str, str]]:
    """
    Scan a single file for secrets
    
    Returns:
        List of (line_number, secret_type, matched_text)
    """
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for pattern, secret_type in SECRET_PATTERNS:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        findings.append((line_num, secret_type, match.group(0)))
    except Exception as e:
        print(f"⚠️  Error scanning {file_path}: {e}")
    
    return findings


def scan_directory(base_path: str) -> Dict[str, List[Tuple[int, str, str]]]:
    """
    Scan directory for secrets
    
    Returns:
        Dict of {file_path: [(line_number, secret_type, matched_text), ...]}
    """
    results = {}
    
    for scan_dir in SCAN_DIRS:
        dir_path = os.path.join(base_path, scan_dir)
        if not os.path.exists(dir_path):
            continue
        
        for root, dirs, files in os.walk(dir_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, base_path)
                
                # Skip excluded files
                if should_exclude(relative_path):
                    continue
                
                # Only scan text files
                if not (file.endswith(('.py', '.js', '.html', '.css', '.json', '.yaml', '.yml', '.md', '.txt'))):
                    continue
                
                findings = scan_file(file_path)
                if findings:
                    results[relative_path] = findings
    
    return results


def mask_secret(secret: str, show_chars: int = 4) -> str:
    """Mask secret for display"""
    if len(secret) <= show_chars * 2:
        return "****"
    return f"{secret[:show_chars]}{'*' * (len(secret) - show_chars * 2)}{secret[-show_chars:]}"


def print_results(results: Dict[str, List[Tuple[int, str, str]]]):
    """Print scan results"""
    print("\n" + "="*60)
    print("  ZeroSite v7.1 - Secrets Scanner Results")
    print("="*60 + "\n")
    
    if not results:
        print("✅ No secrets found in codebase!")
        print("✅ All API keys are properly externalized")
        return True
    
    print(f"❌ Found {sum(len(v) for v in results.values())} potential secrets in {len(results)} files:\n")
    
    for file_path, findings in results.items():
        print(f"📁 {file_path}")
        for line_num, secret_type, matched_text in findings:
            masked = mask_secret(matched_text)
            print(f"   Line {line_num:4d}: {secret_type:20s} {masked}")
        print()
    
    print("="*60)
    print("⚠️  REMEDIATION REQUIRED:")
    print("   1. Move all secrets to .env file")
    print("   2. Use settings from app.config instead")
    print("   3. Verify with: git secrets --scan")
    print("   4. Run this script again to verify")
    print("="*60 + "\n")
    
    return False


def check_env_file():
    """Check if .env file exists and has proper permissions"""
    print("\n" + "─"*60)
    print("  Checking .env file security")
    print("─"*60 + "\n")
    
    env_path = '.env'
    
    if not os.path.exists(env_path):
        print("⚠️  .env file not found")
        print("💡 This is OK if secrets are in environment variables")
        return
    
    print(f"✅ .env file exists")
    
    # Check permissions (Unix only)
    if os.name != 'nt':  # Not Windows
        import stat
        st = os.stat(env_path)
        mode = oct(st.st_mode)[-3:]
        
        print(f"   Permissions: {mode}")
        
        if mode != '600':
            print(f"⚠️  WARNING: .env has permissions {mode}")
            print(f"💡 Recommended: chmod 600 .env")
        else:
            print(f"✅ Permissions are secure (600)")
    
    # Check if .env is in .gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore = f.read()
        
        if '.env' in gitignore:
            print("✅ .env is in .gitignore")
        else:
            print("❌ .env is NOT in .gitignore!")
            print("💡 Add '.env' to .gitignore immediately!")
    else:
        print("⚠️  .gitignore not found")


def main():
    """Main function"""
    # Get base path
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_path)
    
    print("\n🔍 Starting secrets scan...")
    print(f"📂 Base path: {base_path}")
    print(f"📂 Scanning: {', '.join(SCAN_DIRS)}\n")
    
    # Scan for secrets
    results = scan_directory(base_path)
    
    # Print results
    secrets_found = not print_results(results)
    
    # Check .env file
    check_env_file()
    
    # Exit code
    if secrets_found:
        print("\n❌ Secrets scan FAILED: Hardcoded secrets detected")
        sys.exit(1)
    else:
        print("\n✅ Secrets scan PASSED: No hardcoded secrets found")
        sys.exit(0)


if __name__ == "__main__":
    main()
