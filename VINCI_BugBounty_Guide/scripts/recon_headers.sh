#!/bin/bash
# =============================================================================
# VINCI Bug Bounty - Header & Technology Recon Script
# =============================================================================
# Usage: ./recon_headers.sh <target_domain>
# Example: ./recon_headers.sh www.vinci.com
#
# This script performs passive header analysis on a target.
# It does NOT generate large traffic or perform scanning.
# =============================================================================

UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 -BugBounty-vinci-31337 "

if [ -z "$1" ]; then
    echo "Usage: $0 <target_domain>"
    echo "Example: $0 www.vinci.com"
    exit 1
fi

TARGET="$1"
OUTPUT_DIR="./recon_output/${TARGET}"
mkdir -p "$OUTPUT_DIR"

echo "============================================"
echo " VINCI Recon - Target: $TARGET"
echo " Date: $(date)"
echo "============================================"
echo ""

# --- 1. HTTP Response Headers ---
echo "[*] Fetching HTTP response headers..."
curl -sI -A "$UA" "https://${TARGET}" > "$OUTPUT_DIR/headers.txt" 2>/dev/null
echo "    Saved to: $OUTPUT_DIR/headers.txt"
echo ""
echo "    Key headers:"
grep -i "server\|x-powered-by\|x-aspnet\|x-frame\|content-security-policy\|strict-transport\|x-content-type\|set-cookie" "$OUTPUT_DIR/headers.txt" 2>/dev/null | sed 's/^/    /'
echo ""

# --- 2. robots.txt ---
echo "[*] Fetching robots.txt..."
ROBOTS=$(curl -s -A "$UA" "https://${TARGET}/robots.txt" -o "$OUTPUT_DIR/robots.txt" -w "%{http_code}" 2>/dev/null)
if [ "$ROBOTS" = "200" ]; then
    echo "    Found! Saved to: $OUTPUT_DIR/robots.txt"
    echo "    Disallowed paths:"
    grep -i "disallow" "$OUTPUT_DIR/robots.txt" | head -20 | sed 's/^/    /'
else
    echo "    Not found (HTTP $ROBOTS)"
fi
echo ""

# --- 3. sitemap.xml ---
echo "[*] Fetching sitemap.xml..."
SITEMAP=$(curl -s -A "$UA" "https://${TARGET}/sitemap.xml" -o "$OUTPUT_DIR/sitemap.xml" -w "%{http_code}" 2>/dev/null)
if [ "$SITEMAP" = "200" ]; then
    echo "    Found! Saved to: $OUTPUT_DIR/sitemap.xml"
    URL_COUNT=$(grep -c "<loc>" "$OUTPUT_DIR/sitemap.xml" 2>/dev/null)
    echo "    Contains $URL_COUNT URLs"
else
    echo "    Not found (HTTP $SITEMAP)"
fi
echo ""

# --- 4. Security.txt ---
echo "[*] Checking .well-known/security.txt..."
SECTXT=$(curl -s -A "$UA" "https://${TARGET}/.well-known/security.txt" -o "$OUTPUT_DIR/security.txt" -w "%{http_code}" 2>/dev/null)
if [ "$SECTXT" = "200" ]; then
    echo "    Found! Saved to: $OUTPUT_DIR/security.txt"
    cat "$OUTPUT_DIR/security.txt" | sed 's/^/    /'
else
    echo "    Not found (HTTP $SECTXT)"
fi
echo ""

# --- 5. Common interesting paths (single request each) ---
echo "[*] Checking common paths..."
PATHS=("/.git/HEAD" "/.env" "/wp-login.php" "/admin" "/api" "/graphql" "/swagger" "/api-docs" "/.well-known/openid-configuration")

for path in "${PATHS[@]}"; do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" -A "$UA" "https://${TARGET}${path}" 2>/dev/null)
    if [ "$CODE" != "404" ] && [ "$CODE" != "000" ]; then
        echo "    [${CODE}] https://${TARGET}${path}"
    fi
done
echo ""

# --- 6. DNS Records ---
echo "[*] DNS Records for $TARGET..."
echo "  A Records:"
dig +short A "$TARGET" 2>/dev/null | sed 's/^/    /'
echo "  CNAME:"
dig +short CNAME "$TARGET" 2>/dev/null | sed 's/^/    /'
echo "  MX:"
dig +short MX "$TARGET" 2>/dev/null | sed 's/^/    /'
echo "  TXT:"
dig +short TXT "$TARGET" 2>/dev/null | sed 's/^/    /'
echo ""

# --- 7. SSL/TLS Certificate Info ---
echo "[*] SSL Certificate info..."
echo | openssl s_client -servername "$TARGET" -connect "$TARGET:443" 2>/dev/null | openssl x509 -noout -subject -issuer -dates 2>/dev/null | sed 's/^/    /'
echo ""

# --- Summary ---
echo "============================================"
echo " Recon complete for: $TARGET"
echo " Output saved in: $OUTPUT_DIR/"
echo "============================================"
