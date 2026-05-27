#!/bin/bash
# =============================================================================
# VINCI Bug Bounty - Scope Alive Check
# =============================================================================
# Quickly checks which targets are alive and gets basic info.
# One request per target - very low traffic.
# =============================================================================

UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 -BugBounty-vinci-31337 "

echo "============================================"
echo " VINCI Scope - Alive Check"
echo " Date: $(date)"
echo "============================================"
echo ""

TARGETS=(
    "www.vinci.com"
    "leonard.vinci.com"
    "castor.vinci.com"
    "survey.vinci.com"
    "www.fondation-vinci.com"
    "www.lab-recherche-environnement.org"
    "www.vinci-vie.fr"
    "www.trajeoh.com"
    "actionnaires.vinci.com"
    "emag.vinci.com"
    "boost.vinci.com"
    "vinci-groupe.profils.org"
    "jobs.vinci.com"
    "solutions-environnement.vinci.com"
    "essentiel.vinci.com"
    "essentials.vinci.com"
    "www.chaire-arpenter.fr"
    "www.habileoh.com"
    "stats.vinci.com"
)

printf "%-45s %-6s %-12s %s\n" "TARGET" "CODE" "SIZE" "SERVER"
printf "%-45s %-6s %-12s %s\n" "------" "----" "----" "------"

for target in "${TARGETS[@]}"; do
    RESULT=$(curl -s -o /dev/null -w "%{http_code}|%{size_download}" \
        -A "$UA" -m 10 "https://${target}" 2>/dev/null)
    
    CODE=$(echo "$RESULT" | cut -d'|' -f1)
    SIZE=$(echo "$RESULT" | cut -d'|' -f2)
    
    SERVER=$(curl -sI -A "$UA" -m 10 "https://${target}" 2>/dev/null | \
        grep -i "^server:" | cut -d' ' -f2- | tr -d '\r')
    
    if [ "$CODE" = "000" ]; then
        printf "%-45s %-6s %-12s %s\n" "$target" "DOWN" "-" "-"
    else
        printf "%-45s %-6s %-12s %s\n" "$target" "$CODE" "${SIZE}B" "$SERVER"
    fi
    
    sleep 1
done

echo ""
echo "============================================"
echo " Check complete"
echo "============================================"
