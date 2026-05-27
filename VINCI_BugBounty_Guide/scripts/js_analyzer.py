#!/usr/bin/env python3
"""
VINCI Bug Bounty - JavaScript Endpoint & Secret Analyzer
=========================================================
Usage: python3 js_analyzer.py <target_domain>
Example: python3 js_analyzer.py www.vinci.com

Downloads JS files from a target and extracts:
- API endpoints
- Potential secrets/keys
- Hidden routes
- Interesting strings
=========================================================
"""

import re
import sys
import requests
from urllib.parse import urljoin, urlparse


UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
      "-BugBounty-vinci-31337 ")

# Regex patterns for interesting content in JS files
PATTERNS = {
    "API Endpoints": [
        r'["\']/(api|v[0-9]|graphql)[^"\']*["\']',
        r'["\']https?://[^"\']+/api[^"\']*["\']',
        r'fetch\(["\'][^"\']+["\']',
        r'axios\.(get|post|put|delete)\(["\'][^"\']+["\']',
        r'\.ajax\(\{[^}]*url:\s*["\'][^"\']+["\']',
    ],
    "Potential Secrets": [
        r'["\']?api[_-]?key["\']?\s*[:=]\s*["\'][^"\']{10,}["\']',
        r'["\']?secret["\']?\s*[:=]\s*["\'][^"\']{10,}["\']',
        r'["\']?token["\']?\s*[:=]\s*["\'][^"\']{10,}["\']',
        r'["\']?password["\']?\s*[:=]\s*["\'][^"\']{5,}["\']',
        r'["\']?auth["\']?\s*[:=]\s*["\'][^"\']{10,}["\']',
        r'Bearer\s+[A-Za-z0-9\-._~+/]+=*',
    ],
    "Hidden Routes": [
        r'path:\s*["\']/?[^"\']+["\']',
        r'route:\s*["\']/?[^"\']+["\']',
        r'navigate\(["\'][^"\']+["\']',
        r'redirect\(["\'][^"\']+["\']',
        r'window\.location\s*=\s*["\'][^"\']+["\']',
    ],
    "Sensitive URLs": [
        r'["\']https?://[^"\']*admin[^"\']*["\']',
        r'["\']https?://[^"\']*internal[^"\']*["\']',
        r'["\']https?://[^"\']*staging[^"\']*["\']',
        r'["\']https?://[^"\']*dev\.[^"\']*["\']',
        r'["\']https?://[^"\']*test\.[^"\']*["\']',
    ],
    "Interesting Strings": [
        r'TODO[:\s][^\n]{5,50}',
        r'FIXME[:\s][^\n]{5,50}',
        r'HACK[:\s][^\n]{5,50}',
        r'//\s*(bug|vuln|security|danger|warning)[^\n]*',
    ],
}



def fetch_page(url):
    """Fetch page content."""
    headers = {"User-Agent": UA}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        return resp.text
    except Exception as e:
        print(f"[!] Error fetching {url}: {e}")
        return ""


def extract_js_urls(html, base_url):
    """Extract JavaScript file URLs from HTML."""
    js_pattern = r'<script[^>]+src=["\']([^"\']+)["\']'
    matches = re.findall(js_pattern, html, re.IGNORECASE)
    
    js_urls = []
    for match in matches:
        full_url = urljoin(base_url, match)
        js_urls.append(full_url)
    
    return list(set(js_urls))


def analyze_js(content, filename):
    """Analyze JS content for interesting patterns."""
    findings = {}
    
    for category, patterns in PATTERNS.items():
        category_findings = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                cleaned = match.strip()
                if cleaned and len(cleaned) < 200:
                    category_findings.append(cleaned)
        
        if category_findings:
            findings[category] = list(set(category_findings))
    
    return findings



def main():
    if len(sys.argv) < 2:
        print("Usage: python3 js_analyzer.py <target_domain>")
        print("Example: python3 js_analyzer.py www.vinci.com")
        sys.exit(1)
    
    target = sys.argv[1]
    if not target.startswith("http"):
        target = f"https://{target}"
    
    print("=" * 60)
    print(f" VINCI JS Analyzer")
    print(f" Target: {target}")
    print("=" * 60)
    
    # Fetch main page
    print(f"\n[*] Fetching main page...")
    html = fetch_page(target)
    if not html:
        print("[!] Could not fetch target page")
        sys.exit(1)
    
    # Extract JS URLs
    js_urls = extract_js_urls(html, target)
    print(f"[*] Found {len(js_urls)} JavaScript files:")
    for url in js_urls:
        print(f"    → {url}")
    
    # Analyze each JS file
    all_findings = {}
    for js_url in js_urls:
        print(f"\n[*] Analyzing: {js_url}")
        content = fetch_page(js_url)
        if content:
            findings = analyze_js(content, js_url)
            if findings:
                all_findings[js_url] = findings
                for category, items in findings.items():
                    print(f"    [{category}] {len(items)} found")
    
    # Print summary
    print(f"\n\n{'=' * 60}")
    print(f" DETAILED FINDINGS")
    print(f"{'=' * 60}")
    
    for js_file, findings in all_findings.items():
        print(f"\n--- {js_file} ---")
        for category, items in findings.items():
            print(f"\n  [{category}]:")
            for item in items[:10]:
                print(f"    • {item}")
            if len(items) > 10:
                print(f"    ... and {len(items)-10} more")
    
    if not all_findings:
        print("\n[-] No interesting patterns found.")
        print("    Try manually reviewing inline scripts.")


if __name__ == "__main__":
    main()
