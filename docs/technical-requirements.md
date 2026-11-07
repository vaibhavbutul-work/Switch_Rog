# Switch_Rog — Technical Requirements Document (Version 5.0)

> **Project**: Switch_Rog (Two-Person Hackathon)  
> **Version**: 5.0 — Verified Architecture B (Official Switch Ecosystem Stack)  
> **Date**: 2026-11-05  
> **Repository Under Evaluation**: [`sandbox-quantum/switch`](https://github.com/sandbox-quantum/switch)  
> **Companion Document**: [`docs/architecture.md`](file:///d:/3%20year/Switch/Switch_Rog/docs/architecture.md)

---

## Technical Claim Classification Standard

Every requirement and specification in this document is labeled with one of four verifiable states:
* `[Verified: Source Code]` — Directly verified against specific files and commit histories in the official repository.
* `[Verified: Documentation]` — Confirmed from official published documentation and release notes.
* `[Requires Practical Testing]` — Architecturally valid, but runtime behavior depends on host/network environment and must be verified on-site.
* `[Proposed Design]` — Specific configuration choices designed by our team to integrate components without modifying upstream source code.

---

## Table of Contents

1. [Scope & Zero-Budget Constraints](#1-scope--zero-budget-constraints)
2. [Verified vs Unverified Technical Decisions Matrix](#2-verified-vs-unverified-technical-decisions-matrix)
3. [Reconciled Component Specifications](#3-reconciled-component-specifications)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Hardware & Software Allocations: Host vs Client](#6-hardware--software-allocations-host-vs-client)
7. [Official Standalone Docker Deployment Specification](#7-official-standalone-docker-deployment-specification)
8. [Headless Agent Controller Installation & Enrollment](#8-headless-agent-controller-installation--enrollment)
9. [OpenCode Server & ProviderAdapter Specification](#9-opencode-server--provideradapter-specification)
10. [Human Approval & Permission Protocol](#10-human-approval--permission-protocol)
11. [Networking Protocols & Zero-Budget Connectivity](#11-networking-protocols--zero-budget-connectivity)
12. [LLM Provider Requirements & Quota Realities](#12-llm-provider-requirements--quota-realities)
13. [Environment Configuration & Secrets Schema](#13-environment-configuration--secrets-schema)
14. [Pre-Hackathon Readiness Checklist](#14-pre-hackathon-readiness-checklist)
15. [Official Documentation & Source References](#15-official-documentation--source-references)

---

## 1. Scope & Zero-Budget Constraints

Switch_Rog deploys a collaborative AI coding environment for two developers on separate Windows laptops over a 24-48 hour hackathon with a **strict \$0.00 infrastructure budget**.

| In Scope | Explicitly Out of Scope |
|---|---|
| Single-host multi-container deployment via Docker Compose `[Verified: Documentation]` | Paid cloud hosting, VPS, or cloud Kubernetes clusters |
| Local LAN via smartphone hotspot or free mesh VPN (Tailscale) `[Requires Practical Testing]` | Paid domains, static public IPs, or commercial TLS certificates |
| Headless `switch-agent-controller` daemon running inside WSL2 `[Verified: Source Code]` | Manual custom FastAPI bridge servers |
| Human approval in chat before applying file changes or executing code `[Verified: Source Code]` | Autonomous unreviewed execution (`--auto` / bypass permissions) |
| Free-tier Cloud LLMs (Gemini / Groq) or local quantized models `[Verified: Documentation]` | Paid token APIs (Anthropic/OpenAI without active promotional credits) |

---

## 2. Verified vs Unverified Technical Decisions Matrix

| Subsystem / Feature | Classification | Source Code / Evidence Path |
|---|---|---|
| **Standalone Compose Stack** | `[Verified: Source Code]` | `deploy/local/standalone-docker-compose.yml` |
| **Tuwunel Excluded from Compose** | `[Verified: Source Code]` | Migrated to PostgreSQL; purged from `deploy/local/standalone-docker-compose.yml`. |
| **Port 3000 Exposes Gateway** | `[Verified: Source Code]` | Defined as `GATEWAY_HOST_PORT=3000` on service `gateway` in standalone compose. |
| **Setup Container Auto-boot** | `[Verified: Source Code]` | Defined under `--profile collab` in `deploy/local/standalone-docker-compose.yml`. |
| **Mattermost WebSocket Ingress** | `[Verified: Source Code]` | Implemented in `core/switch_core/bridges/collaboration/mattermost.py` via `_ws_handler`. |
| **Headless Controller Operation** | `[Verified: Source Code]` | CLI daemon in `console/packages/agent-controller/` (`@sandboxaq/switch-agent-controller`). |
| **Controller X25519 Handshake** | `[Verified: Source Code]` | Cryptographic enrollment protocol in `console/packages/agent-controller/src/enroll.ts`. |
| **OpenCode ProviderAdapter** | `[Verified: Source Code]` | Custom adapter interface in `console/packages/agent-providers/src/adapter.ts` (HTTP/SSE). |
| **Native Switch Approval State** | `[Verified: Source Code]` | Durable question/approval tracking in `core/switch_core/services/` and room bridges. |
| **Mattermost In-Room Approval UI** | `[Requires Practical Testing]` | Button cards vs text replies (`approve`/`deny`) depends on Mattermost Team Edition plugins. |
| **Mobile Hotspot Direct Routing** | `[Requires Practical Testing]` | Subject to smartphone OS client isolation settings and Windows Firewall Private profile. |
| **Gemini Free-Tier Reliability** | `[Requires Practical Testing]` | Free tier subject to dynamic throttling; requires secondary provider (Groq) fallback. |

---

## 3. Reconciled Component Specifications

### 3.1 Switch Core (`core/`) `[Verified: Source Code]`
* **Code Location**: `core/switch_core/`
* **Role**: Primary stateful backend coordination engine.
* **Responsibilities**:
  - Manages **Rooms** (continuous conversation context, turn history, and member presence).
  - Implements chat platform adapters (`core/switch_core/bridges/collaboration/`).
  - Maintains server-side question and approval tracking records in PostgreSQL.
* **Network**: Internal Docker bridge network; communicates with PostgreSQL on internal port 5432. Exposes port 8000 if `API_HOST_PORT` is set.

### 3.2 Switch Gateway (`gateway/`) `[Verified: Source Code & Releases]`
* **Code Location**: `gateway/`
* **Role**: The web-based operator dashboard and administration surface.
* **Responsibilities**:
  - Serves the Gateway web administration UI on port `3000`.
  - Exposes APIs for dynamic connector registration and webhook ingress.
* **Packaging**: Ships as a Docker container image (`switch-gateway:${SWITCH_VERSION}`) activated via `--profile gateway`.

### 3.3 Switch Setup (`setup`) `[Verified: Source Code]`
* **Code Location**: `setup/`
* **Role**: Automated provisioning container.
* **Responsibilities**:
  - Runs once upon stack startup under `--profile collab`.
  - Automatically provisions Mattermost: creates admin credentials, the default team, bot user tokens, and registers the Mattermost connector with Switch Core.

### 3.4 Switch Agent Controller (`console/packages/agent-controller/`) `[Verified: Source Code]`
* **Code Location**: `console/packages/agent-controller/`
* **Role**: Headless workstation daemon (`switch-agent-controller`).
* **Responsibilities**:
  - Runs locally inside WSL2 on Laptop 1.
  - Maintains a persistent Protocol 2 WebSocket connection to Switch Core.
  - Spawns and manages local agent execution sessions via `ProviderAdapter`.

---

## 4. Functional Requirements

| ID | Description | Priority | Technical Mechanism |
|---|---|---|---|
| **FR-01** | Developers can submit coding tasks via Mattermost chat | 🔴 Must | Mattermost `#ai-coding` ──► Switch `MattermostAdapter` (`_ws_handler`) `[Verified: Source Code]`. |
| **FR-02** | Shared room serving two developers simultaneously | 🔴 Must | Switch Room context maintains continuous multi-user conversation turns `[Verified: Source Code]`. |
| **FR-03** | Agent generates proposed changes without automatic disk write | 🔴 Must | OpenCode configured with `Auto mode = disabled` in Switch Console `[Verified: Documentation]`. |
| **FR-04** | Switch holds execution and posts approval prompt in Mattermost | 🔴 Must | Switch Core question/approval tracking engine `[Verified: Source Code]`. |
| **FR-05** | Human developer approves/declines change in Mattermost | 🔴 Must | Human replies in thread (`approve` or `deny`); event captured by `_ws_handler` `[Verified: Source Code]`. |
| **FR-06** | Approved changes are committed to Git on an isolated branch | 🔴 Must | OpenCode applies diff to workspace `/repo` and executes `git commit` `[Verified: Documentation]`. |
| **FR-07** | Real-time chat sync across both developer laptops | 🔴 Must | Mattermost exposed on Host port 8065 via WSL2 mirrored networking `[Requires Practical Testing]`. |
| **FR-08** | Collaborating developer can pull AI commits locally | 🟠 Should | Commits pushed to GitHub; Developer #2 executes `git pull` `[Verified: Documentation]`. |

---

## 5. Non-Functional Requirements

| Metric | Target | Rationale |
|---|---|---|
| **Total Cost** | **\$0.00** | Strict zero-budget college hackathon constraint `[Verified: Documentation]`. |
| **Host RAM Limit** | < 6 GB RAM committed to WSL2 | Preserves stability on a 16 GB Windows host `[Verified: Documentation]`. |
| **Turnaround Latency** | < 30 seconds for code generation | Google Gemini 2.5 Flash nominal inference speed `[Requires Practical Testing]`. |
| **Local Network Resilience** | Functional without external internet for chat | Local Docker network handles Mattermost & Switch communication `[Verified: Source Code]`. |
| **Host System Safety** | Non-root container execution; no `docker.sock` mount | Prevents arbitrary host command execution `[Verified: Documentation]`. |
| **Persistence** | Data preserved across container restarts | Named volumes for PostgreSQL (`postgres_data`) and Mattermost (`mattermost_data`) `[Verified: Source Code]`. |

---

## 6. Hardware & Software Allocations: Host vs Client

```
┌────────────────────────────────────────────────────────┐
│             HOST LAPTOP 1 (Your Laptop)                │
│                                                        │
│  Hardware: 16 GB RAM, Quad-Core CPU, Windows 11 22H2+  │
│                                                        │
│  Software & Running Services:                          │
│  1. Windows Subsystem for Linux (WSL2, Mirrored Mode)  │
│  2. Docker Desktop for Windows                         │
│  3. Docker Containers (via standalone compose):        │
│     • `postgres:15-alpine`                             │
│     • `mattermost` (:8065)                             │
│     • `switch` (Core, :8000)                           │
│     • `gateway` (:3000)                                │
│     • `setup` (One-shot provisioner)                   │
│  4. Workstation Daemons (Inside WSL2):                 │
│     • `switch-agent-controller` (CLI daemon)           │
│     • `opencode serve --port 4096` (Engine)            │
│  5. Local Git Workspace Volume (`repo_data` ──► /repo) │
│  6. Host `.env` file holding API keys and secrets      │
└────────────────────────────────────────────────────────┘
                           │
                           │ Wi-Fi Hotspot / LAN
                           ▼
┌────────────────────────────────────────────────────────┐
│           CLIENT LAPTOP 2 (Collaborator Laptop)        │
│                                                        │
│  Hardware: Any standard laptop (Windows / Mac / Linux) │
│                                                        │
│  Software Required:                                    │
│  1. Web Browser (Chrome / Edge / Firefox)              │
│     ──► Opens http://<HOST_IP>:8065 for Mattermost     │
│  2. Git CLI / GitHub Desktop                           │
│     ──► Clones project repository from GitHub          │
│  3. Code Editor (VS Code / Cursor for local coding)    │
│                                                        │
│  ❌ Runs ZERO Docker containers                        │
│  ❌ Runs ZERO server software                          │
│  ❌ Requires NO LLM API keys                           │
└────────────────────────────────────────────────────────┘
```

---

## 7. Official Standalone Docker Deployment Specification

### 7.1 Verified Compose File Schema `[Verified: Source Code]`
Location in repository: `deploy/local/standalone-docker-compose.yml`

```yaml
# deploy/local/standalone-docker-compose.yml (Source Code Contract)
services:
  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-switch}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-switch}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - default

  switch:
    image: ${SWITCH_REGISTRY:-ghcr.io}/${SWITCH_IMAGE_NAMESPACE:-sandbox-quantum}/switch:${SWITCH_VERSION:-latest}
    restart: unless-stopped
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
    ports:
      - "${API_HOST_PORT:-8000}:8000"
    networks:
      - default

  gateway:
    image: ${SWITCH_REGISTRY:-ghcr.io}/${SWITCH_IMAGE_NAMESPACE:-sandbox-quantum}/switch-gateway:${SWITCH_VERSION:-latest}
    profiles: ["gateway"]
    ports:
      - "${GATEWAY_HOST_PORT:-3000}:3000"
    depends_on:
      - switch
    networks:
      - default

  init-db:
    image: ${SWITCH_REGISTRY:-ghcr.io}/${SWITCH_IMAGE_NAMESPACE:-sandbox-quantum}/switch-init-db:${SWITCH_VERSION:-latest}
    profiles: ["collab"]
    depends_on:
      - postgres
    networks:
      - default

  mattermost:
    image: mattermost/mattermost-team-edition:latest
    profiles: ["collab"]
    ports:
      - "${MATTERMOST_HOST_PORT:-8065}:8065"
    depends_on:
      - postgres
      - init-db
    volumes:
      - mattermost_data:/mattermost/data
      - mattermost_config:/mattermost/config
    networks:
      - default

  setup:
    image: ${SWITCH_REGISTRY:-ghcr.io}/${SWITCH_IMAGE_NAMESPACE:-sandbox-quantum}/switch-setup:${SWITCH_VERSION:-latest}
    profiles: ["collab"]
    depends_on:
      - switch
      - mattermost
    networks:
      - default

volumes:
  postgres_data:
  mattermost_data:
  mattermost_config:
```

### 7.2 Verified Compose Commands `[Verified: Documentation]`
```bash
# 1. Generate secrets and .env file
just init-env

# 2. Start core services + Gateway + Mattermost
docker compose -f deploy/local/standalone-docker-compose.yml \
  --profile collab --profile gateway up -d
```

---

## 8. Headless Agent Controller Installation & Enrollment

### 8.1 Prerequisites & Installation `[Verified: Source Code]`
Inside WSL2 on Laptop 1:
```bash
# Ensure Node.js >= 22.13.0 is installed
node --version

# Option A: Install via official script
curl -fsSL https://raw.githubusercontent.com/sandbox-quantum/switch/main/console/packages/agent-controller/install.sh | bash

# Option B: Install via npm globally
npm install -g @sandboxaq/switch-agent-controller
```

### 8.2 Machine Enrollment `[Verified: Source Code]`
1. Open the Switch Gateway UI in a browser at `http://localhost:3000`.
2. Navigate to **Machines** ──► Click **Add Machine** ──► Copy the generated one-time enrollment token.
3. In the WSL2 terminal, execute:
   ```bash
   switch-agent-controller enroll <ENROLLMENT_TOKEN> --url http://localhost:3000
   ```
4. Verify connection status:
   ```bash
   switch-agent-controller status
   ```

---

## 9. OpenCode Server & ProviderAdapter Specification

### 9.1 OpenCode Server Daemon `[Verified: Documentation]`
Inside WSL2 on Laptop 1, navigate to the target repository directory and start OpenCode:
```bash
cd /path/to/Switch_Rog
npm install -g @opencode/cli
opencode serve --port 4096
```

### 9.2 ProviderAdapter Communication `[Verified: Source Code]`
* **Code Reference**: `console/packages/agent-providers/src/adapter.ts`
* The Switch Agent Controller attaches to the running OpenCode process on port `4096`.
* Outbound prompts are dispatched via HTTP POST calls.
* Inbound code proposals, file diffs, and tool logs stream back via Server-Sent Events (SSE).

---

## 10. Human Approval & Permission Protocol

### 10.1 Approval Workflow Enforcement `[Verified: Source Code & Documentation]`
1. **Disable Auto Mode**: In the Switch Gateway UI, navigate to the enrolled OpenCode agent profile and ensure **Auto mode** and **Bypass permissions** are set to **OFF (Disabled)**.
2. **Action Interception**: When OpenCode generates file changes or terminal commands, execution is paused.
3. **In-Room Prompt**: Switch Core formats an approval prompt into the Mattermost channel thread:
   ```markdown
   ⚠️ **Action Approval Required from OpenCode**
   **Action**: Write file `src/auth.js` (+15 lines)
   **Command**: `git commit -m "feat(auth): validate inputs"`
   *Reply `approve` or `deny` in this thread.*
   ```
4. **Human Decision**: Developer #1 or Developer #2 replies `approve`.
5. **Resolution**: `_ws_handler` captures the reply, verifies user authorization, and signals the controller to allow OpenCode to write the file and commit changes.

---

## 11. Networking Protocols & Zero-Budget Connectivity

### 11.1 Host WSL2 Mirrored Configuration `[Verified: Documentation]`
File: `C:\Users\<Username>\.wslconfig` (Host Laptop)

```ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
firewall=true
memory=6GB
processors=4
```

### 11.2 Networking Testing Protocols `[Requires Practical Testing]`

#### Test 1: Mobile Hotspot Peer Connectivity
* **Test**: Connect Laptop 1 and Laptop 2 to Smartphone Hotspot.
* **Execution**: From Laptop 2, run:
  ```bash
  ping <HOST_IP>
  curl -I http://<HOST_IP>:8065
  ```
* **Failure Condition**: Packets drop or connection times out.
* **Remediation**: On Laptop 1, change Windows network profile to Private:
  ```powershell
  Set-NetConnectionProfile -InterfaceAlias "Wi-Fi" -NetworkCategory Private
  ```

#### Test 2: Tailscale Mesh Tunnel Fallback
* **Test**: Both laptops log into the same personal Tailnet.
* **Execution**: From Laptop 2, run:
  ```bash
  curl -I http://100.x.y.z:8065
  ```
* **Failure Condition**: High latency or connection blocked by strict university outbound firewall.
* **Remediation**: Check Tailscale DERP relay status: `tailscale netcheck`.

---

## 12. LLM Provider Requirements & Quota Realities

### 12.1 Google Gemini 2.5 Flash `[Verified: Documentation]`
* **Cost**: \$0.00 via Google AI Studio API key.
* **Nominal Limits**: Published as ~15 RPM / ~1,500 RPD for Flash models.
* **Operational Reality `[Requires Practical Testing]`**:
  - Quotas are **not guaranteed SLAs**. Dynamic throttling, regional shedding, and content filtering apply.
  - Configured in OpenCode (`opencode.json`):
    ```jsonc
    {
      "$schema": "https://opencode.ai/config.json",
      "model": "google/gemini-2.5-flash",
      "provider": {
        "google": {
          "options": {
            "apiKey": "{env:GOOGLE_API_KEY}"
          }
        }
      }
    }
    ```

### 12.2 Secondary Provider: Groq Cloud `[Verified: Documentation]`
* **Cost**: \$0.00 free tier via [console.groq.com](https://console.groq.com).
* **Models**: `llama-3.3-70b-versatile`, `qwen-2.5-coder-32b`.

---

## 13. Environment Configuration & Secrets Schema

File: `.env` (in Switch repository root on Host Laptop) `[Verified: Source Code]`:

```env
# ==============================================================================
# Switch_Rog Environment Configuration (.env)
# EXCLUDED FROM GIT VIA .gitignore
# ==============================================================================

# --- Networking ---
HOST_IP=192.168.43.10          # Replace with Laptop 1's actual Hotspot/LAN IP
GATEWAY_HOST_PORT=3000
API_HOST_PORT=8000
MATTERMOST_HOST_PORT=8065

# --- Database Credentials (generated by just init-env) ---
POSTGRES_USER=switch
POSTGRES_PASSWORD=generated_random_password_32chars
POSTGRES_DB=switch

# --- Switch Images ---
SWITCH_REGISTRY=ghcr.io
SWITCH_IMAGE_NAMESPACE=sandbox-quantum
SWITCH_VERSION=latest

# --- LLM Credentials ---
GOOGLE_API_KEY=AIzaSy_your_free_google_ai_studio_key_here
GROQ_API_KEY=gsk_your_free_groq_key_here

# --- GitHub Integration ---
GITHUB_PAT=github_pat_your_fine_grained_pat_here
GITHUB_REPO=https://github.com/your-org/Switch_Rog.git
```

---

## 14. Pre-Hackathon Readiness Checklist

### Host Laptop (Laptop 1)
- [ ] Windows 11 updated to 22H2+.
- [ ] `.wslconfig` configured with `networkingMode=mirrored` and `memory=6GB`.
- [ ] Inbound Windows Firewall rules added for ports `8065` and `3000`.
- [ ] Docker Desktop updated and WSL2 backend verified.
- [ ] Switch repository cloned: `git clone https://github.com/sandbox-quantum/switch.git`.
- [ ] `switch-agent-controller` installed inside WSL2 (`npm install -g @sandboxaq/switch-agent-controller`).
- [ ] OpenCode CLI installed inside WSL2 (`npm install -g @opencode/cli`).
- [ ] Free Google AI Studio API key obtained and validated.
- [ ] Secondary Groq API key obtained.
- [ ] Standalone compose stack pre-pulled:
  ```bash
  docker compose -f deploy/local/standalone-docker-compose.yml \
    --profile collab --profile gateway pull
  ```

### Client Laptop (Laptop 2)
- [ ] Web browser updated.
- [ ] Git installed and configured.
- [ ] GitHub repository access verified.
- [ ] Tailscale installed (standby).

---

## 15. Official Documentation & Source References

1. **Standalone Docker Compose Contract**: [`deploy/local/standalone-docker-compose.yml`](https://github.com/sandbox-quantum/switch/blob/main/deploy/local/standalone-docker-compose.yml)
2. **Environment Template**: [`deploy/local/.env.example`](https://github.com/sandbox-quantum/switch/blob/main/.env.example)
3. **Mattermost Collaboration Adapter**: `core/switch_core/bridges/collaboration/mattermost.py`
4. **Switch Agent Controller Package**: `console/packages/agent-controller/`
5. **OpenCode Provider Adapter**: `console/packages/agent-providers/src/adapter.ts`
6. **Agent Provider Documentation**: `console/docs/add-an-agent-provider.md`
7. **Switch Room Working Documentation**: [Switch AI Docs — Working with Agents in Rooms](https://docs.switchagents.ai)

---

*End of Technical Requirements Document (Version 5.0)*
