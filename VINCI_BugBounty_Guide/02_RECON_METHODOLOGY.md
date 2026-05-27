# VINCI Bug Bounty - Reconnaissance Methodology & Checklist

## IMPORTANT REMINDERS
- **User-Agent**: Always append ` -BugBounty-vinci-31337 ` to your UA
- **No automated scanners** generating large traffic
- **No DoS** or service degradation
- **Manual testing only** (or low-traffic custom scripts)

---

## Phase 1: Passive Reconnaissance (No Direct Interaction)

### 1.1 Technology Fingerprinting
- [ ] Check Wappalyzer/BuiltWith for tech stack (CMS, frameworks, JS libs)
- [ ] Review HTTP response headers (Server, X-Powered-By, X-AspNet-Version)
- [ ] Identify CDN/WAF (Cloudflare, Akamai, etc.) — affects payload delivery
- [ ] Note CMS versions (WordPress, Drupal, custom)
- [ ] Check `robots.txt` for hidden paths
- [ ] Check `sitemap.xml` for full URL map
- [ ] Check `/.well-known/` directory for security.txt, openid-config, etc.
- [ ] Review page source for comments, debug info, API endpoints

### 1.2 DNS & Infrastructure
- [ ] DNS records (A, AAAA, CNAME, MX, TXT, NS) — `dig` or `nslookup`
- [ ] Check for DNS zone transfer (unlikely but worth trying)
- [ ] Reverse DNS lookup on IPs
- [ ] Check if multiple targets share the same IP/infrastructure
- [ ] Look for related subdomains via Certificate Transparency logs (crt.sh)
- [ ] Note: Only in-scope domains are valid targets!

### 1.3 Historical & Cached Data
- [ ] Wayback Machine (web.archive.org) — find old endpoints, removed pages
- [ ] Google dorking for indexed sensitive files:
  ```
  site:TARGET filetype:pdf
  site:TARGET filetype:xml
  site:TARGET filetype:json
  site:TARGET filetype:conf
  site:TARGET inurl:admin
  site:TARGET inurl:login
  site:TARGET inurl:api
  site:TARGET intitle:"index of"
  site:TARGET ext:env | ext:log | ext:bak
  ```
- [ ] Check Google cache for recently changed pages
- [ ] Search GitHub/GitLab for references to target domains (leaked configs, old code)

### 1.4 JavaScript Analysis (Passive)
- [ ] Download all JS files from the target
- [ ] Search for API endpoints, keys, tokens in JS bundles
- [ ] Look for hidden routes/admin paths in JS routers (React/Vue/Angular)
- [ ] Identify API versioning (v1, v2 — older versions may lack security)
- [ ] Look for comments with developer notes, TODO items

---

## Phase 2: Active Reconnaissance (Light Interaction)

### 2.1 Directory & Endpoint Discovery
- [ ] Manual browsing with Burp Suite proxy (capture all traffic)
- [ ] Common paths to check manually:
  ```
  /admin, /administrator, /login, /wp-admin, /wp-login.php
  /api, /api/v1, /api/v2, /graphql, /swagger, /api-docs
  /debug, /trace, /actuator, /health, /metrics, /info
  /.git, /.svn, /.env, /config, /backup
  /uploads, /media, /static, /assets
  /phpmyadmin, /adminer, /console
  ```
- [ ] Check for HTTP methods (OPTIONS request to discover allowed methods)
- [ ] Try common backup file extensions: `.bak`, `.old`, `.orig`, `.swp`, `.~`
- [ ] Check for version control exposure: `/.git/HEAD`, `/.svn/entries`

### 2.2 Application Mapping
- [ ] Map all user-accessible features and functions
- [ ] Identify all input vectors (forms, URL params, headers, cookies)
- [ ] Document all API endpoints discovered
- [ ] Note authentication mechanisms (cookie, JWT, OAuth, SAML)
- [ ] Identify file upload points
- [ ] Map user roles and permission levels
- [ ] Document all redirects and their parameters

### 2.3 Registration & Authentication Recon
For targets allowing self-registration (boost.vinci.com, vinci-groupe.profils.org):
- [ ] Register with YWH aliases
- [ ] Add "BugBounty, TEST" to name fields
- [ ] Use `@yeswehack.ninja` email
- [ ] Map all post-auth features
- [ ] Check for multiple user roles (candidate, employer, admin?)
- [ ] Test password reset flow
- [ ] Check for session management issues
- [ ] Look at all cookies set after authentication

---

## Phase 3: Vulnerability Surface Mapping

### 3.1 Input Vectors Catalog
For each endpoint, document:
```
| Endpoint | Method | Parameters | Auth Required | Input Type | Notes |
|----------|--------|-----------|---------------|------------|-------|
| /search  | GET    | q, page   | No            | Text       | Reflected in response |
| /profile | POST   | name, bio | Yes           | Text/File  | Rich text editor |
```

### 3.2 High-Value Features to Focus On
- [ ] **Search functionality** → XSS, SQLi
- [ ] **User profiles** → Stored XSS, IDOR
- [ ] **File uploads** → RCE, XSS via SVG/HTML
- [ ] **Password reset** → Token leakage, account takeover
- [ ] **API endpoints** → Auth bypass, IDOR, mass assignment
- [ ] **Payment/financial features** (actionnaires.vinci.com) → Business logic
- [ ] **Contact forms** → SSRF (if URL input), injection
- [ ] **Export/download features** → SSRF, path traversal, XXE
- [ ] **Multi-step workflows** → Business logic bypass
- [ ] **Redirect parameters** → Open redirect chains

### 3.3 Per-Target Quick Checks
For each target in scope, quickly verify:
- [ ] Is the site up and responding?
- [ ] What's the main technology? (WordPress, custom PHP, Node.js, .NET?)
- [ ] Are there login/register forms?
- [ ] Are there API endpoints visible?
- [ ] Are there input-heavy features (search, forms, uploads)?
- [ ] What error pages look like (custom vs default = info leak)

---

## Phase 4: Tool Setup Checklist

### Browser Setup
- [ ] Burp Suite Community/Pro configured as proxy
- [ ] Browser with custom User-Agent set: `Mozilla/5.0 ... -BugBounty-vinci-31337 `
- [ ] FoxyProxy or similar for quick proxy toggling
- [ ] Wappalyzer extension
- [ ] Cookie editor extension

### Burp Suite Configuration
- [ ] Target scope set to all in-scope domains
- [ ] Out-of-scope domains excluded
- [ ] Match & Replace rule to add User-Agent suffix
- [ ] Passive scanner enabled (doesn't generate extra traffic)
- [ ] Logger enabled to capture all requests

### Local Tools Ready
- [ ] `curl` / `httpie` for manual requests
- [ ] `ffuf` or `gobuster` (USE SPARINGLY - low thread count, no large wordlists)
- [ ] `nuclei` (ONLY targeted templates, NOT bulk scanning)
- [ ] `jq` for JSON parsing
- [ ] `sqlmap` (ONLY on confirmed injection points, NOT for discovery)
- [ ] Browser DevTools (Network, Console, Application tabs)

---

## Phase 5: Documentation During Recon

### Create Notes Per Target
```
## [TARGET_NAME]
- **URL**: https://target.vinci.com
- **Tech Stack**: [CMS/Framework/Language]
- **Auth**: [None / Cookie / JWT / OAuth]
- **Interesting Endpoints**:
  - /api/v1/users (returns user data)
  - /search?q= (reflected input)
- **Potential Vulns to Test**:
  - [ ] XSS in search
  - [ ] IDOR in /api/v1/users/{id}
- **Screenshots**: [folder path]
```

### Track Everything
- Take screenshots at every step
- Save all interesting requests/responses from Burp
- Note timestamps (for report timeline)
- Document what you tested AND what you ruled out

---

## Quick Reference: Google Dorks for VINCI

```bash
# Find login pages
site:vinci.com inurl:login OR inurl:signin OR inurl:auth

# Find APIs
site:vinci.com inurl:api OR inurl:graphql OR inurl:swagger

# Find exposed files
site:vinci.com filetype:xml OR filetype:json OR filetype:conf

# Find error pages (tech disclosure)
site:vinci.com "error" OR "exception" OR "stack trace"

# Find admin panels
site:vinci.com inurl:admin OR inurl:dashboard OR inurl:panel

# Find upload features
site:vinci.com inurl:upload OR inurl:file OR inurl:document

# Specific targets
site:boost.vinci.com
site:actionnaires.vinci.com
site:leonard.vinci.com
```

---

## Mindset Tips

1. **Think like a user first** — Use the app normally, understand the business logic
2. **Follow the data** — Where does user input go? Where does it end up?
3. **Check every response** — Look for leaked info in headers, cookies, HTML comments
4. **Test boundary conditions** — What happens with empty input? Max length? Special chars?
5. **Chain low-severity issues** — An open redirect + CSRF might = account takeover
6. **Shared codebase awareness** — If you find something on one target, check others (but remember one fix = one reward)
