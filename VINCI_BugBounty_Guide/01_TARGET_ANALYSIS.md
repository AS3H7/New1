# VINCI Bug Bounty - Target Priority Analysis

## Priority Tiers

### TIER 1 - HIGH REWARD + HIGH VALUE (Focus Here First)

| Target | Max Reward | Reports Filed | Strategy |
|--------|-----------|---------------|----------|
| **www.vinci.com** | €3,000 | 156 | Main corporate site. High report count means easy bugs are gone. Look for business logic, complex auth flows, deeper injection points. |
| **actionnaires.vinci.com** | €3,000 | 50 | Shareholder portal. Likely has authenticated features, financial data. IDOR/privilege escalation potential. |

### TIER 2 - MEDIUM REWARD + GOOD OPPORTUNITY

| Target | Max Reward | Reports Filed | Strategy |
|--------|-----------|---------------|----------|
| **boost.vinci.com** | €2,000 | 72 | Self-registration allowed. Grey-box testing. Focus on auth bypass, IDOR after registration. |
| **vinci-groupe.profils.org** | €2,000 | 39 | Job profiles/recruitment. Self-registration. User data = IDOR goldmine. |
| **leonard.vinci.com** | €2,000 | 32 | Innovation platform. Medium reports = still opportunities. |
| **castor.vinci.com** | €2,000 | 29 | Medium reports. Less explored. |
| **www.fondation-vinci.com** | €2,000 | 25 | Foundation site. Fewer reports = less explored. |
| **jobs.vinci.com** | €2,000 | 11 | Job portal. Redirects to profils.org for applications. |
| **www.lab-recherche-environnement.org** | €2,000 | 12 | Research lab. Less tested. |
| **www.vinci-vie.fr** | €2,000 | 12 | Insurance/life services. Financial context = high impact. |
| **www.trajeoh.com** | €2,000 | 3 | Very few reports! Underexplored. |
| **emag.vinci.com** | €2,000 | 2 | Almost untouched. Digital magazine? |
| **www.habileoh.com** | €2,000 | 1 | Nearly zero reports! Fresh target. |

### TIER 3 - LOW REWARD BUT UNDEREXPLORED

| Target | Max Reward | Reports Filed | Strategy |
|--------|-----------|---------------|----------|
| **survey.vinci.com** | €1,500 | 14 | Survey platform. Input-heavy = XSS/injection potential. |
| **voeux.vinci.com** | €1,500 | 0 | ZERO reports! Completely unexplored. Start here for quick wins. |
| **solutions-environnement.vinci.com** | €1,500 | 4 | Few reports. |
| **essentiel.vinci.com** | €1,500 | 1 | Nearly untouched. |
| **essentials.vinci.com** | €1,500 | 1 | Nearly untouched. Mirror of above? |
| **www.chaire-arpenter.fr** | €1,500 | 8 | Academic chair site. |
| **stats.vinci.com** | - | - | Stats/analytics. Could expose sensitive data. |

---

## Recommended Hunt Order (Maximize ROI)

### Phase 1: Quick Wins (Low-hanging fruit on underexplored targets)
1. **voeux.vinci.com** (0 reports - completely fresh!)
2. **www.habileoh.com** (1 report)
3. **emag.vinci.com** (2 reports)
4. **www.trajeoh.com** (3 reports)
5. **stats.vinci.com** (unknown - could be interesting)

### Phase 2: Grey-Box Testing (Register & Dig Deep)
1. **boost.vinci.com** (register, test authenticated features)
2. **vinci-groupe.profils.org** (register, test profile/job features)
3. **actionnaires.vinci.com** (shareholder features, financial data)

### Phase 3: Deep Dive (Complex vulns on well-tested targets)
1. **www.vinci.com** (business logic, chained attacks)
2. **leonard.vinci.com** (innovation platform features)
3. **castor.vinci.com** (less common attack vectors)

---

## Key Observations

- **Shared codebase warning**: Some scopes share frameworks. If you find a vuln on one, check others - but know that one fix = one reward.
- **Third-party solutions**: Some apps use vendor solutions. Focus on config issues and custom code, not vendor platform bugs.
- **Registration targets**: boost.vinci.com & vinci-groupe.profils.org allow self-registration. Use YWH aliases, add "BugBounty, TEST" to name fields.
- **User-Agent required**: Always append ` -BugBounty-vinci-31337 ` to your UA string.
