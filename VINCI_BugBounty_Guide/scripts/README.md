# VINCI Bug Bounty - Helper Scripts

## Overview
These scripts are designed for **manual, low-traffic testing** in compliance 
with VINCI's bug bounty program rules. They are NOT automated scanners.

## Setup
```bash
# Make shell scripts executable
chmod +x *.sh

# Install Python dependencies (for Python scripts)
pip install requests
```

## Scripts

### 1. `scope_alive_check.sh`
Quick check which targets are alive. Run first!
```bash
./scope_alive_check.sh
```

### 2. `recon_headers.sh`
Passive header/tech recon on a single target.
```bash
./recon_headers.sh www.vinci.com
```

### 3. `js_analyzer.py`
Download and analyze JS files for endpoints, secrets, and routes.
```bash
python3 js_analyzer.py www.vinci.com
```

### 4. `cors_checker.sh`
Test a specific endpoint for CORS misconfigurations.
```bash
./cors_checker.sh https://www.vinci.com/api/some-endpoint
```

### 5. `param_miner.py`
Discover reflected parameters and test input handling.
```bash
# Discover parameters
python3 param_miner.py https://www.vinci.com/search

# Test specific parameter
python3 param_miner.py https://www.vinci.com/search --param q

# Check HTTP methods
python3 param_miner.py https://www.vinci.com/api --methods
```

### 6. `idor_checker.py`
Interactive IDOR testing between two accounts.
```bash
python3 idor_checker.py
```

## Important Rules
- All scripts include the required User-Agent: `-BugBounty-vinci-31337`
- Scripts send minimal requests (NOT mass scanning)
- Always use these on IN-SCOPE targets only
- Do NOT use these to cause service degradation
- Take screenshots of any findings for your report
