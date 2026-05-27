#!/usr/bin/env python3
"""
VINCI Bug Bounty - Parameter Discovery & Input Testing Helper
=============================================================================
Usage: python3 param_miner.py <target_url>
Example: python3 param_miner.py https://www.vinci.com/search

This script helps identify hidden parameters and test input handling.
It sends minimal requests (one per parameter tested).
=============================================================================
"""

import sys
import requests
import time
from urllib.parse import urlparse, urlencode

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 -BugBounty-vinci-31337 "

# Common parameter names to check
COMMON_PARAMS = [
    # Standard
    "id", "page", "q", "search", "query", "s", "keyword",
    "lang", "language", "locale", "l",
    "redirect", "url", "next", "return", "redir", "dest", "destination",
    "file", "path", "doc", "document", "template", "tpl",
    "action", "cmd", "command", "do", "func", "function",
    "user", "username", "email", "name", "uid", "user_id",
    "token", "key", "api_key", "apikey", "secret",
    "callback", "cb", "jsonp",
    "format", "type", "output", "content_type",
    "sort", "order", "orderby", "sortby", "dir", "direction",
    "limit", "offset", "count", "per_page", "page_size",
    "filter", "category", "cat", "tag", "status", "state",
    "debug", "test", "verbose", "dev", "admin",
    "include", "require", "load", "read", "fetch",
    "view", "display", "show", "render", "preview",
    "edit", "update", "modify", "delete", "remove",
    "upload", "import", "export", "download",
    "config", "settings", "options", "prefs",
    "version", "v", "ver",
    "year", "month", "date", "from", "to",
]

# XSS canary for reflection detection
CANARY = "k1r0t3st<>\"'&"

def check_reflection(target_url, params_to_test):
    """Check which parameters reflect input in the response."""
    print(f"\n[*] Testing parameter reflection on: {target_url}")
    print(f"[*] Canary string: {CANARY}")
    print(f"[*] Testing {len(params_to_test)} parameters...")
    print("-" * 60)
    
    headers = {"User-Agent": UA}
    reflected = []
    
    # Get baseline response
    try:
        baseline = requests.get(target_url, headers=headers, timeout=10, allow_redirects=True)
        baseline_length = len(baseline.text)
    except Exception as e:
        print(f"[!] Error connecting to target: {e}")
        return []
    
    for param in params_to_test:
        try:
            params = {param: CANARY}
            response = requests.get(target_url, params=params, headers=headers, timeout=10, allow_redirects=True)
            
            # Check if canary is reflected
            if CANARY in response.text:
                reflected.append({
                    "param": param,
                    "reflected": True,
                    "encoded": "&lt;" not in response.text.split(CANARY.replace("<>\"'&", ""))[0] if CANARY.replace("<>\"'&", "") in response.text else None,
                    "status": response.status_code,
                    "length_diff": len(response.text) - baseline_length
                })
                print(f"    [REFLECTED] ?{param}={CANARY} (Status: {response.status_code})")
            elif len(response.text) != baseline_length:
                # Parameter accepted (response changed) but not reflected
                diff = len(response.text) - baseline_length
                print(f"    [ACCEPTED]  ?{param}= (Status: {response.status_code}, Size diff: {diff:+d})")
            
            # Be respectful - small delay between requests
            time.sleep(0.5)
            
        except requests.exceptions.Timeout:
            print(f"    [TIMEOUT]   ?{param}= (possible blind injection point!)")
        except Exception as e:
            continue
    
    return reflected


def check_special_chars(target_url, param_name):
    """Test how special characters are handled in a specific parameter."""
    print(f"\n[*] Testing special character handling for parameter: {param_name}")
    print("-" * 60)
    
    headers = {"User-Agent": UA}
    
    test_chars = [
        ("Single Quote", "'"),
        ("Double Quote", '"'),
        ("Less Than", "<"),
        ("Greater Than", ">"),
        ("Ampersand", "&"),
        ("Backslash", "\\"),
        ("Forward Slash", "/"),
        ("Null Byte", "%00"),
        ("CRLF", "%0d%0a"),
        ("Semicolon", ";"),
        ("Pipe", "|"),
        ("Backtick", "`"),
        ("Dollar Brace", "${7*7}"),
        ("Double Brace", "{{7*7}}"),
        ("Script Tag", "<script>"),
    ]
    
    for name, char in test_chars:
        try:
            test_value = f"test{char}test"
            params = {param_name: test_value}
            response = requests.get(target_url, params=params, headers=headers, timeout=10, allow_redirects=True)
            
            if test_value in response.text:
                print(f"    [RAW]      {name:15s} ({char:10s}) - Reflected WITHOUT encoding!")
            elif char in response.text:
                print(f"    [PARTIAL]  {name:15s} ({char:10s}) - Character present in response")
            elif response.status_code >= 400:
                print(f"    [BLOCKED]  {name:15s} ({char:10s}) - Status {response.status_code}")
            elif response.status_code == 200:
                print(f"    [ENCODED]  {name:15s} ({char:10s}) - Encoded or stripped")
            
            time.sleep(0.3)
            
        except Exception as e:
            print(f"    [ERROR]    {name:15s} - {e}")


def check_http_methods(target_url):
    """Check which HTTP methods are allowed."""
    print(f"\n[*] Checking HTTP methods on: {target_url}")
    print("-" * 60)
    
    headers = {"User-Agent": UA}
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE"]
    
    for method in methods:
        try:
            response = requests.request(method, target_url, headers=headers, timeout=10, allow_redirects=False)
            status = response.status_code
            
            if method == "OPTIONS":
                allow = response.headers.get("Allow", "Not specified")
                acao = response.headers.get("Access-Control-Allow-Methods", "Not specified")
                print(f"    [{status}] {method:8s} - Allow: {allow} | ACAM: {acao}")
            else:
                print(f"    [{status}] {method:8s} - Length: {len(response.content)}")
            
            time.sleep(0.3)
            
        except Exception as e:
            print(f"    [ERR] {method:8s} - {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 param_miner.py <target_url> [--param <param_name>]")
        print("")
        print("Modes:")
        print("  python3 param_miner.py https://target.com/page")
        print("      → Discover reflected parameters")
        print("")
        print("  python3 param_miner.py https://target.com/page --param q")
        print("      → Deep-test specific parameter for injection")
        print("")
        print("  python3 param_miner.py https://target.com/page --methods")
        print("      → Check allowed HTTP methods")
        sys.exit(1)
    
    target_url = sys.argv[1]
    
    # Validate URL
    parsed = urlparse(target_url)
    if not parsed.scheme or not parsed.netloc:
        print("[!] Please provide a full URL (https://...)")
        sys.exit(1)
    
    # Check if target is in scope
    valid_domains = [
        "vinci.com", "fondation-vinci.com", "lab-recherche-environnement.org",
        "vinci-vie.fr", "trajeoh.com", "vinci-groupe.profils.org",
        "chaire-arpenter.fr", "habileoh.com"
    ]
    in_scope = any(d in parsed.netloc for d in valid_domains)
    if not in_scope:
        print(f"[!] WARNING: {parsed.netloc} may not be in scope for VINCI program!")
        response = input("    Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    print("=" * 60)
    print(f" VINCI Parameter Miner")
    print(f" Target: {target_url}")
    print(f" UA: ...{UA[-40:]}")
    print("=" * 60)
    
    if "--methods" in sys.argv:
        check_http_methods(target_url)
    elif "--param" in sys.argv:
        idx = sys.argv.index("--param")
        if idx + 1 < len(sys.argv):
            param_name = sys.argv[idx + 1]
            check_special_chars(target_url, param_name)
        else:
            print("[!] Please specify parameter name after --param")
    else:
        reflected = check_reflection(target_url, COMMON_PARAMS)
        
        if reflected:
            print(f"\n{'=' * 60}")
            print(f" SUMMARY: {len(reflected)} reflected parameters found!")
            print(f"{'=' * 60}")
            for r in reflected:
                print(f"  → {r['param']} (Status: {r['status']})")
            print("\n[*] Next steps:")
            print("    Run with --param <name> to test injection handling")
            print("    Example: python3 param_miner.py", target_url, "--param", reflected[0]['param'])
        else:
            print("\n[-] No reflected parameters found with common names.")
            print("    Try:")
            print("    1. Browse the target manually and note parameter names from URLs/forms")
            print("    2. Check JavaScript files for hidden API parameters")
            print("    3. Review Burp Suite history for parameters in POST bodies")


if __name__ == "__main__":
    main()
