# Switch_Rog — Implementation Plan (Stage 2 - Revised)

> **Project**: Switch_Rog (Two-Person Hackathon)  
> **Target Architecture**: Architecture B (Official Switch Ecosystem Stack)  
> **Release Target**: Current Official Stable Release (`sandbox-quantum/switch`)  
> **Date**: 2026-11-05  
> **Directory Layout**:  
> - Switch Infrastructure: `D:\3 year\Switch\switch` (WSL2: `/mnt/d/3\ year/Switch/switch`)  
> - Project Workspace: `D:\3 year\Switch\Switch_Rog` (WSL2: `/mnt/d/3\ year/Switch/Switch_Rog`)  
> **Companion Documents**:  
> - [`docs/architecture.md`](file:///d:/3%20year/Switch/Switch_Rog/docs/architecture.md)  
> - [`docs/technical-requirements.md`](file:///d:/3%20year/Switch/Switch_Rog/docs/technical-requirements.md)

---

## Technical Directives & Safety Policies

1. **Zero Execution Mandate**: This plan is a strictly documented operational blueprint. No installation commands or containers are executed during this review.
2. **Credential Sanitization**: No real API keys, GitHub tokens, or machine enrollment tokens appear in this plan. All parameters use standard shell variables (`${GOOGLE_API_KEY}`) or clear placeholders (`<ENROLLMENT_TOKEN>`).
3. **Mandatory Human-in-the-Loop Approval**: `Auto mode` and `Bypass permissions` are strictly set to **OFF**. Unrestricted autonomous file writes and terminal executions are disabled.
4. **Agent Management Recommendation**: In the official Switch architecture, the **Switch Console desktop application** is the recommended interface for managing local agent sessions and provider adapters on developer workstations. For headless or automated environments, the standalone `switch-agent-controller` CLI daemon is used. This plan documents both approaches, with Switch Console as the primary developer workflow.
5. **No Automatic Model Failover Assumption**: OpenCode does **not** silently fail over between LLM providers on rate limits. Both Google Gemini and Groq Cloud must be configured as distinct providers in `opencode.json`, and an explicit model-switch procedure is documented and tested.

---

## Phase Overview

| Phase | Description | Environment Partitioning |
|---|---|---|
| **Phase 1** | Prepare Windows, WSL2, and Docker Desktop on Laptop 1 | `[PowerShell]` (Admin) |
| **Phase 2** | Deploy Self-Hosted Switch Core, Mattermost, and Gateway | `[WSL2]` & `[Browser]` |
| **Phase 3** | Install OpenCode & Start Server in Project Workspace | `[WSL2]` |
| **Phase 4** | Setup Switch Console & Connect OpenCode Agent | `[Browser]` & `[WSL2]` |
| **Phase 5** | Configure & Verify Gemini API with Groq Fallback | `[WSL2]` & `opencode.json` |
| **Phase 6** | Connect Mattermost `#ai-coding` with Switch Room | `[Browser]` |
| **Phase 7** | Connect Laptop 2 (Client Workstation) | `[PowerShell]`, `[Browser]` & Git CLI |
| **Phase 8** | End-to-End Validation: Shared Coding, Approvals & Git | `[Browser]`, Mattermost Chat & Git CLI |

---

## Phase 1: Prepare Windows, WSL2, and Docker Desktop on Laptop 1

### 1.1 Objective
Prepare the Windows 11 host (Laptop 1) with WSL2 Mirrored Networking for direct LAN access, configure Windows Defender Firewall rules for inbound ports 8065 and 3000, and ensure Docker Desktop is linked to the WSL2 engine.

### 1.2 Execution Steps

#### Step 1.1: Verify & Update WSL2 `[PowerShell (Admin)]`
* **Where**: Windows PowerShell (Run as Administrator)
* **Commands**:
  ```powershell
  wsl --status
  wsl --update
  ```
* **Expected Output**: Displays default distribution (e.g. `Ubuntu`), WSL kernel version `2.3.x` or higher.

#### Step 1.2: Configure WSL2 Mirrored Networking `[PowerShell]`
* **Where**: Windows Filesystem (`C:\Users\<YourUsername>\.wslconfig`)
* **Configuration**: Create or edit `C:\Users\<YourUsername>\.wslconfig`:
  ```ini
  [wsl2]
  networkingMode=mirrored
  dnsTunneling=true
  firewall=true
  autoProxy=true
  memory=6GB
  processors=4
  ```
* **Apply Configuration** `[PowerShell (Admin)]`:
  ```powershell
  wsl --shutdown
  ```
* **Expected Output**: WSL terminates cleanly; subsequent launches boot in mirrored networking mode.

#### Step 1.3: Configure Inbound Windows Firewall Rules `[PowerShell (Admin)]`
* **Where**: Windows PowerShell (Run as Administrator)
* **Commands**:
  ```powershell
  New-NetFirewallRule -DisplayName "Switch_Rog - Mattermost (8065)" `
    -Direction Inbound -Protocol TCP -LocalPort 8065 `
    -Action Allow -Profile Private

  New-NetFirewallRule -DisplayName "Switch_Rog - Switch Gateway (3000)" `
    -Direction Inbound -Protocol TCP -LocalPort 3000 `
    -Action Allow -Profile Private
  ```
* **Expected Output**: Both rules created with `Enabled: True`, `Action: Allow`.

#### Step 1.4: Link Docker Desktop to WSL2 Engine `[Browser / UI]`
* **Where**: Docker Desktop Settings GUI
* **Action**:
  1. Open **Settings** ──► **General** ──► Ensure **Use the WSL 2 based engine** is checked.
  2. Open **Resources** ──► **WSL Integration** ──► Enable integration for default distribution (`Ubuntu`).
  3. Click **Apply & Restart**.

### 1.3 Common Errors & Solutions
* **Error**: `networkingMode=mirrored` not recognized.  
  *Cause*: Windows 11 build is older than 22H2 (Build 22621+).  
  *Fix*: Run Windows Update or fall back to standard NAT mode and forward ports using `netsh interface portproxy`.
* **Error**: Docker daemon fails to start inside WSL2.  
  *Cause*: Docker Desktop service hung after WSL shutdown.  
  *Fix*: Restart Docker Desktop from the Windows system tray.

---

## Phase 2: Deploy Switch Core, Mattermost, and Gateway

### 2.1 Objective
Deploy the official Switch standalone self-hosted stack using Docker Compose inside `D:\3 year\Switch\switch`. This starts PostgreSQL, Switch Core, Mattermost, the one-shot `setup` provisioner, and Switch Gateway.

### 2.2 Execution Steps

#### Step 2.1: Clone Switch Repository to Designated Directory `[WSL2]`
* **Where**: WSL2 Terminal
* **Working Directory**: `/mnt/d/3 year/Switch`
* **Commands**:
  ```bash
  mkdir -p "/mnt/d/3 year/Switch"
  cd "/mnt/d/3 year/Switch"

  # Clone current official Switch repository
  git clone https://github.com/sandbox-quantum/switch.git
  cd switch
  ```
* **Expected Output**: Repository cloned into `/mnt/d/3 year/Switch/switch`.

#### Step 2.2: Initialize Environment File `[WSL2]`
* **Where**: WSL2 Terminal
* **Working Directory**: `/mnt/d/3 year/Switch/switch`
* **Commands**:
  ```bash
  # If `just` is installed:
  just init-env

  # If `just` is not installed, copy template manually:
  cp .env.example .env
  ```
* **Configuration File**: Edit `/mnt/d/3 year/Switch/switch/.env`:
  ```env
  GATEWAY_HOST_PORT=3000
  API_HOST_PORT=8000
  MATTERMOST_HOST_PORT=8065

  POSTGRES_USER=switch
  POSTGRES_PASSWORD=generated_random_password_32chars
  POSTGRES_DB=switch

  SWITCH_REGISTRY=ghcr.io
  SWITCH_IMAGE_NAMESPACE=sandbox-quantum
  SWITCH_VERSION=latest
  ```

#### Step 2.3: Launch Stable Standalone Compose Stack `[WSL2]`
* **Where**: WSL2 Terminal
* **Working Directory**: `/mnt/d/3 year/Switch/switch`
* **Command**:
  ```bash
  docker compose -f deploy/local/standalone-docker-compose.yml \
    --profile collab --profile gateway up -d
  ```
* **Expected Output**:
  ```text
  [+] Running 6/6
   ✔ Container switch-postgres-1   Started
   ✔ Container switch-switch-1     Started
   ✔ Container switch-init-db-1    Started
   ✔ Container switch-mattermost-1 Started
   ✔ Container switch-gateway-1    Started
   ✔ Container switch-setup-1      Started
  ```

#### Step 2.4: Verify Container Health & Services `[WSL2]`
* **Where**: WSL2 Terminal
* **Command**:
  ```bash
  docker compose -f deploy/local/standalone-docker-compose.yml ps
  ```
* **Expected Output**:
  - `postgres`: Up (healthy, port 5432 internal)
  - `switch`: Up (Core engine)
  - `gateway`: Up (`0.0.0.0:3000->3000/tcp`)
  - `mattermost`: Up (`0.0.0.0:8065->8065/tcp`)
  - `setup`: Exited (0) — completed one-shot bootstrap

#### Step 2.5: Verify Web Endpoints `[Browser]`
* **Where**: Web Browser on Laptop 1
* **Actions**:
  1. Navigate to `http://localhost:8065` ──► Confirm Mattermost login/team page loads.
  2. Navigate to `http://localhost:3000` ──► Confirm Switch Gateway Operator Dashboard loads.

### 2.3 Common Errors & Solutions
* **Error**: Port 8065 or 3000 already in use.  
  *Cause*: Stale test process holding the socket.  
  *Fix*: Run `Get-Process -Id (Get-NetTCPConnection -LocalPort 8065).OwningProcess | Stop-Process` in PowerShell Admin.
* **Error**: `setup` container fails on initial database connection.  
  *Cause*: PostgreSQL startup took longer than the setup script timeout.  
  *Fix*: Run `docker compose -f deploy/local/standalone-docker-compose.yml restart setup`.

---

## Phase 3: Install OpenCode & Start Server in Project Workspace

### 3.1 Objective
Install the OpenCode CLI inside WSL2, initialize the project repository in `D:\3 year\Switch\Switch_Rog`, and launch OpenCode in server mode on port 4096.

### 3.2 Execution Steps

#### Step 3.1: Install OpenCode CLI `[WSL2]`
* **Where**: WSL2 Terminal
* **Commands**:
  ```bash
  # Ensure Node.js >= 22.13 is installed
  node -v

  # Install official OpenCode CLI globally
  npm install -g @opencode/cli

  # Verify installation
  opencode --version
  ```
* **Expected Output**: Returns `@opencode/cli` version.

#### Step 3.2: Initialize Project Git Workspace `[WSL2]`
* **Where**: WSL2 Terminal
* **Working Directory**: `/mnt/d/3 year/Switch/Switch_Rog`
* **Commands**:
  ```bash
  mkdir -p "/mnt/d/3 year/Switch/Switch_Rog"
  cd "/mnt/d/3 year/Switch/Switch_Rog"

  # Initialize Git repository
  git init
  git config user.name "OpenCode Agent"
  git config user.email "opencode@switchrog.local"
  ```
* **Expected Output**: Initialized empty Git repository in `/mnt/d/3 year/Switch/Switch_Rog/.git/`.

#### Step 3.3: Launch OpenCode Background Server `[WSL2]`
* **Where**: WSL2 Terminal (Inside a persistent `tmux` session or background job)
* **Working Directory**: `/mnt/d/3 year/Switch/Switch_Rog`
* **Command**:
  ```bash
  opencode serve --port 4096
  ```
* **Expected Output**:
  ```text
  [opencode] Server listening on http://127.0.0.1:4096
  [opencode] OpenAPI specification available at http://127.0.0.1:4096/openapi.json
  ```

### 3.3 Common Errors & Solutions
* **Error**: `EADDRINUSE 127.0.0.1:4096`.  
  *Cause*: Prior instance of OpenCode is running.  
  *Fix*: Run `fuser -k 4096/tcp` in WSL2.

---

## Phase 4: Setup Switch Console & Connect OpenCode Agent

### 4.1 Objective
Register OpenCode with Switch using the official recommended method (Switch Console / Gateway Operator Dashboard) and ensure human approval controls are strictly enforced.

### 4.2 Architecture Decision: Console Desktop vs Headless Controller
* **Primary Recommendation**: Use **Switch Console** desktop app (`switch-console`) or the **Gateway Operator Dashboard** (`http://localhost:3000`). It automatically provisions local agent sessions, configures provider settings, and manages the background execution loop.
* **Headless Alternative**: If running entirely headless in WSL2 without a GUI, use `switch-agent-controller` as documented below.

### 4.3 Execution Steps

#### Option A: Headless Daemon Enrollment `[WSL2]`
* **Where**: WSL2 Terminal
* **Commands**:
  ```bash
  # Install headless controller package
  npm install -g @sandboxaq/switch-agent-controller

  # Enroll with Switch Gateway using token generated from UI (:3000 -> Machines -> Add Machine)
  switch-agent-controller enroll <ENROLLMENT_TOKEN> --url http://localhost:3000

  # Check controller diagnostics
  switch-agent-controller doctor
  switch-agent-controller status
  ```
* **Expected Output**: Status displays `Connected` with an active Protocol 2 WebSocket stream.

#### Option B: Switch Console / Gateway UI Setup `[Browser]`
* **Where**: Web Browser on Laptop 1
* **URL**: `http://localhost:3000`
* **Actions**:
  1. Open Gateway Dashboard at `http://localhost:3000`.
  2. Navigate to **Agents** ──► Click **Add Agent**.
  3. Set **Name**: `opencode`.
  4. Set **Provider**: Select `OpenCode` (utilizes native `ProviderAdapter` via HTTP/SSE).
  5. Set **Server URL**: `http://localhost:4096` (or `http://127.0.0.1:4096`).
  6. Set **Working Directory**: `/mnt/d/3 year/Switch/Switch_Rog` (or `D:\3 year\Switch\Switch_Rog`).

#### Step 4.4: Enforce Mandatory Human Approval `[Browser]`
* **Where**: Switch Gateway UI (`http://localhost:3000`)
* **Action**:
  1. Open **Agents** ──► Select **OpenCode**.
  2. Under **General Settings**:
     - Toggle **Auto mode**: **OFF (Disabled)**
     - Toggle **Bypass permissions**: **OFF (Disabled)**
  3. Click **Save Settings**.
* **Verification**: Auto mode badge displays as `Disabled` / `Requires Approval`.

---

## Phase 5: Configure & Verify Gemini API with Groq Fallback

### 5.1 Objective
Configure OpenCode to use Google Gemini 2.5 Flash as its primary model and configure Groq Cloud (`llama-3.3-70b-versatile`) as a standby fallback provider. Document the explicit fallback testing and switchover procedure.

### 5.2 Execution Steps

#### Step 5.1: Export API Keys in WSL2 `[WSL2]`
* **Where**: WSL2 Terminal
* **Commands**:
  ```bash
  # Export session keys (replace with real keys from Google AI Studio & Groq Console)
  export GOOGLE_API_KEY="AIzaSy_YOUR_FREE_GOOGLE_AI_STUDIO_KEY"
  export GROQ_API_KEY="gsk_YOUR_FREE_GROQ_KEY"

  # Persist locally in project directory (.gitignore excludes this file)
  cd "/mnt/d/3 year/Switch/Switch_Rog"
  cat << 'EOF' > .env
  GOOGLE_API_KEY="AIzaSy_YOUR_FREE_GOOGLE_AI_STUDIO_KEY"
  GROQ_API_KEY="gsk_YOUR_FREE_GROQ_KEY"
  EOF
  ```

#### Step 5.2: Create Dual-Provider `opencode.json` `[WSL2]`
* **Where**: WSL2 Terminal
* **File Path**: `/mnt/d/3 year/Switch/Switch_Rog/opencode.json`
* **Configuration**:
  ```jsonc
  {
    "$schema": "https://opencode.ai/config.json",
    "model": "google/gemini-2.5-flash",
    "provider": {
      "google": {
        "options": {
          "apiKey": "{env:GOOGLE_API_KEY}"
        }
      },
      "groq": {
        "package": "@opencode/ai/providers/openai-compatible",
        "settings": {
          "baseURL": "https://api.groq.com/openai/v1"
        },
        "options": {
          "apiKey": "{env:GROQ_API_KEY}"
        },
        "models": {
          "llama-3.3-70b-versatile": {}
        }
      }
    }
  }
  ```

#### Step 5.3: Test Primary Provider (Google Gemini) `[WSL2]`
* **Where**: WSL2 Terminal
* **Working Directory**: `/mnt/d/3 year/Switch/Switch_Rog`
* **Command**:
  ```bash
  opencode run --model google/gemini-2.5-flash "echo 'Gemini connection verified.'"
  ```
* **Expected Output**: Returns model confirmation with zero authorization or quota errors.

#### Step 5.4: Test Fallback Provider (Groq Cloud) `[WSL2]`
* **Where**: WSL2 Terminal
* **Working Directory**: `/mnt/d/3 year/Switch/Switch_Rog`
* **Command**:
  ```bash
  opencode run --model groq/llama-3.3-70b-versatile "echo 'Groq fallback connection verified.'"
  ```
* **Expected Output**: Returns ultra-low latency response from Groq.

#### Step 5.5: Fallback Switchover Procedure (If Gemini Throttles) `[WSL2]`
If Google Gemini encounters rate-limiting (`429 Too Many Requests` or quota exhaustion) during the hackathon:
1. Open `/mnt/d/3 year/Switch/Switch_Rog/opencode.json`.
2. Change the default model line:
   ```json
   "model": "groq/llama-3.3-70b-versatile"
   ```
3. Restart or trigger next task in OpenCode. OpenCode will immediately route subsequent requests to Groq Cloud.

---

## Phase 6: Connect Mattermost `#ai-coding` with Switch Room

### 6.1 Objective
Verify the automated Mattermost bot provisioning, create the `#ai-coding` channel, and bind it to a Switch Room with OpenCode assigned.

### 6.2 Execution Steps

#### Step 6.1: Access Mattermost & Create Channel `[Browser]`
* **Where**: Web Browser on Laptop 1
* **URL**: `http://localhost:8065`
* **Actions**:
  1. Log in to Mattermost (`http://localhost:8065`).
  2. Create a new Public Channel:
     - **Name**: `ai-coding`
     - **Purpose**: Shared developer collaboration with OpenCode
  3. Click **Create Channel**.

#### Step 6.2: Add Switch Bot User to `#ai-coding` `[Browser]`
* **Where**: Mattermost Web Interface (`http://localhost:8065`)
* **Actions**:
  1. Inside `#ai-coding`, click the channel header ──► **Add Members**.
  2. Search for the pre-provisioned bot user (e.g. `switch-bot` or `opencode`).
  3. Select the bot and click **Add**.

#### Step 6.3: Map Channel to Room in Switch Gateway `[Browser]`
* **Where**: Switch Gateway UI (`http://localhost:3000`)
* **Actions**:
  1. Navigate to **Rooms** ──► Click **Add Room** (or select `#ai-coding` if auto-detected).
  2. Set **Room Name**: `ai-coding`.
  3. In **Assigned Agents**: Check **OpenCode**.
  4. In **Platform Channel**: Link to Mattermost channel `ai-coding`.
  5. Click **Save**.

### 6.3 Verification
* Post a test message in `#ai-coding`: `Hello world`.
* Inspect `docker compose -f deploy/local/standalone-docker-compose.yml logs -f switch` to confirm the turn was captured over the WebSocket.

---

## Phase 7: Connect Laptop 2 (Client Workstation)

### 7.1 Objective
Establish local network communication between Laptop 1 and Laptop 2 via a smartphone mobile hotspot, and verify Developer #2 can collaborate via Mattermost without installing server dependencies.

### 7.2 Execution Steps

#### Step 7.1: Connect to Smartphone Hotspot `[Hardware / Wi-Fi]`
* **Action**:
  1. Turn on smartphone 4G/5G mobile hotspot.
  2. Connect **Laptop 1 (Host)** to the hotspot Wi-Fi SSID.
  3. Connect **Laptop 2 (Client)** to the same hotspot Wi-Fi SSID.

#### Step 7.2: Obtain & Configure Host LAN IP `[PowerShell (Admin)]`
* **Where**: Laptop 1 — Windows PowerShell (Admin)
* **Commands**:
  ```powershell
  # Find IPv4 Address of Wi-Fi adapter
  ipconfig | Select-String -Pattern "IPv4 Address"

  # Ensure Network Category is Private (unblocks firewall rules)
  Set-NetConnectionProfile -InterfaceAlias "Wi-Fi" -NetworkCategory Private
  ```
* **Expected Output**: Displays host LAN IP (e.g. `192.168.43.10`), confirms network is `Private`.

#### Step 7.3: Test Connectivity from Laptop 2 `[PowerShell / Terminal]`
* **Where**: Laptop 2 — Terminal / PowerShell
* **Commands**:
  ```bash
  # Test ICMP reachability
  ping 192.168.43.10

  # Test HTTP port 8065 reachability
  curl -I http://192.168.43.10:8065
  ```
* **Expected Output**: `HTTP/1.1 200 OK` or `302 Found`.

#### Step 7.4: Developer #2 Account Creation `[Browser]`
* **Where**: Laptop 2 — Web Browser
* **URL**: `http://192.168.43.10:8065`
* **Actions**:
  1. Open browser to `http://192.168.43.10:8065`.
  2. Sign up with Developer #2 username and password.
  3. Join the `#ai-coding` channel.

#### Step 7.5: Clone Project Repository on Laptop 2 `[Git CLI]`
* **Where**: Laptop 2 — Terminal
* **Command**:
  ```bash
  git clone https://github.com/<your-org>/Switch_Rog.git
  cd Switch_Rog
  ```

---

## Phase 8: End-to-End Validation: Shared Coding, Approvals & Git

### 8.1 Objective
Validate the complete multi-developer collaborative loop: Developer #2 submits a task from Laptop 2, OpenCode holds execution for human approval, Developer #1 authorizes the action from Mattermost, and changes are committed to Git.

### 8.2 Execution Scenarios

#### Scenario 1: Multi-Developer Task Dispatch `[Browser]`
* **Where**: Laptop 2 — Mattermost `#ai-coding` (`http://192.168.43.10:8065`)
* **Action**: Developer #2 posts:
  ```text
  @opencode Create a math utility function in src/math.js and write unit tests in tests/math.test.js.
  ```
* **Expected Behavior**:
  1. Both developers see the message appear in `#ai-coding`.
  2. Switch Core receives the event and dispatches the turn to OpenCode.

#### Scenario 2: Verification of Approval Hold `[Browser]`
* **Where**: Mattermost `#ai-coding` Thread
* **Expected Behavior**:
  OpenCode halts execution and Switch Core posts an interactive permission prompt into the thread:
  ```markdown
  ⚠️ **Action Approval Required from OpenCode**
  **Action**: Create `src/math.js` (+10 lines)
  **Action**: Create `tests/math.test.js` (+15 lines)
  **Command**: `git checkout -b ai/feature-math && git commit -m "feat: add math utility"`
  *Reply `approve` or `deny` in this thread.*
  ```
* **Filesystem Verification `[WSL2]`**:
  Check `/mnt/d/3 year/Switch/Switch_Rog/src/math.js` ──► File does **NOT** exist yet.

#### Scenario 3: Human Authorization & Commit Execution `[Browser]`
* **Where**: Laptop 1 — Mattermost `#ai-coding` (`http://localhost:8065`)
* **Action**: Developer #1 replies in the thread:
  ```text
  approve
  ```
* **Expected Behavior**:
  1. `_ws_handler` captures `approve` event.
  2. OpenCode receives authorization and applies file modifications to disk.
  3. OpenCode commits changes to Git branch `ai/feature-math`.
  4. Bot replies in Mattermost:
     ```markdown
     ✅ **Action Approved & Executed**
     Created: `src/math.js`, `tests/math.test.js`
     Branch: `ai/feature-math` | Commit: `a1b2c3d`
     ```

#### Scenario 4: Push & Local Pull `[Git CLI]`
* **On Laptop 1 `[WSL2]`**:
  ```bash
  cd "/mnt/d/3 year/Switch/Switch_Rog"
  git push origin ai/feature-math
  ```
* **On Laptop 2 `[Git CLI]`**:
  ```bash
  git fetch origin
  git checkout ai/feature-math
  git log -1
  ```
* **Verification**: Developer #2 inspects the committed code generated by OpenCode.

---

## 9. Comprehensive Troubleshooting Reference

| Symptom | Probable Cause | Diagnostic Command | Remediation |
|---|---|---|---|
| Mattermost inaccessible from Laptop 2 | Firewall blocking port 8065 | `Test-NetConnection -Port 8065` in PowerShell | Set Wi-Fi connection profile to Private: `Set-NetConnectionProfile -NetworkCategory Private`. |
| OpenCode modifies files without asking | Auto mode enabled | Check Switch Gateway UI | In Gateway UI ──► Agents ──► OpenCode ──► Set `Auto mode = OFF`. |
| Gemini API throws `429 Quota Exceeded` | Free-tier rate limit reached | Check WSL2 terminal running OpenCode | Edit `opencode.json` to change `"model": "groq/llama-3.3-70b-versatile"`. |
| Switch Bot ignores channel posts | Bot not added as channel member | Open Mattermost channel member list | Header ──► Add Members ──► Search and add `switch-bot`. |
| Docker daemon offline after reboot | WSL shut down without restart | Run `wsl -l -v` in PowerShell | Launch Ubuntu distribution and restart Docker Desktop. |

---

*End of Implementation Plan (Stage 2 - Revised)*
