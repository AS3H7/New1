#!/bin/bash
# =============================================================================
# VINCI Bug Bounty - CORS Misconfiguration Checker
# =============================================================================
# Usage: ./cors_checker.sh <target_url>
# Example: ./cors_checker.sh https://www.vinci.com/api/endpoint
#
# Tests for common CORS misconfigurations on a single endpoint.
# Low traffic - sends only a few requests.
# =============================================================================

UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 -BugBounty-vinci-31337 "

if [ -z "$1" ]; then
    echo "Usage: $0 <target_url>"
    echo "Example: $0 https://www.vinci.com/api/endpoint"
    exit 1
fi

TARGET="$1"

echo "============================================"
echo " CORS Check - Target: $TARGET"
echo "============================================"
echo ""

# Test origins
ORIGINS=(
    "https://evil.com"
    "https://attacker.vinci.com"
    "https://vinci.com.attacker.com"
    "null"
    "https://www.vinci.com"
    "http://www.vinci.com"
)

for origin in "${ORIGINS[@]}"; do
    echo "[*] Testing Origin: $origin"
    
    RESPONSE=$(curl -s -I -A "$UA" -H "Origin: $origin" "$TARGET" 2>/dev/null)
    
    ACAO=$(echo "$RESPONSE" | grep -i "access-control-allow-origin" | tr -d '\r')
    ACAC=$(echo "$RESPONSE" | grep -i "access-control-allow-credentials" | tr -d '\r')
    
    if [ -n "$ACAO" ]; then
        echo "    $ACAO"
        if [ -n "$ACAC" ]; then
            echo "    $ACAC"
        fi
        
        # Check for dangerous combinations
        if echo "$ACAO" | grep -qi "$origin" && echo "$ACAC" | grep -qi "true"; then
            echo "    [!!!] POTENTIALLY VULNERABLE - Origin reflected with credentials!"
            echo "         Origin '$origin' is reflected AND credentials are allowed."
            echo ""
        elif echo "$ACAO" | grep -qi "\*"; then
            echo "    [!] Wildcard ACAO - check if credentials are also allowed"
            echo ""
        else
            echo "    [-] Not exploitable with this origin"
            echo ""
        fi
    else
        echo "    [-] No ACAO header returned"
        echo ""
    fi
done

echo "============================================"
echo " CORS check complete"
echo "============================================"
echo ""
echo "If a vulnerability was found, create a PoC HTML file:"
echo ""
echo '<html>'
echo '<script>'
echo 'fetch("TARGET_URL", {credentials: "include"})'
echo '  .then(r => r.text())'
echo '  .then(d => { document.getElementById("out").innerText = d; })'
echo '</script>'
echo '<div id="out"></div>'
echo '</html>'
