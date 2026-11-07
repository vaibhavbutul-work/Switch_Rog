# Switch_Rog — System Architecture Document (Version 5.0)

> **Project**: Switch_Rog (Two-Person Hackathon)  
> **Version**: 5.0 — Verified Architecture B (Official Switch Ecosystem Stack)  
> **Date**: 2026-11-05  
> **Repository Under Evaluation**: [`sandbox-quantum/switch`](https://github.com/sandbox-quantum/switch)  
> **Companion Document**: [`docs/technical-requirements.md`](file:///d:/3%20year/Switch/Switch_Rog/docs/technical-requirements.md)

---

## Technical Claim Classification Standard

Every architectural assertion in this document is labeled with one of four verifiable states:
* `[Verified: Source Code]` — Directly verified against specific files and commit histories in the official repository.
* `[Verified: Documentation]` — Confirmed from official published documentation and release notes.
* `[Requires Practical Testing]` — Architecturally valid, but runtime behavior depends on host/network environment and must be verified on-site.
* `[Proposed Design]` — Specific configuration choices designed by our team to integrate components without modifying upstream source code.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Investigation & Verification of Core Inquiries](#2-investigation--verification-of-core-inquiries)
3. [Architecture B Overview: Official Ecosystem Stack](#3-architecture-b-overview-official-ecosystem-stack)
4. [Component Disambiguation & Source-Code Paths](#4-component-disambiguation--source-code-paths)
5. [End-to-End Execution & Data Flow](#5-end-to-end-execution--data-flow)
6. [Human-in-the-Loop Approval Lifecycle](#6-human-in-the-loop-approval-lifecycle)
7. [System Architecture Diagram](#7-system-architecture-diagram)
8. [Two-Laptop Topology: Host vs Client Roles](#8-two-laptop-topology-host-vs-client-roles)
9. [Zero-Budget Networking: Hotspot vs Mesh Tunnel](#9-zero-budget-networking-hotspot-vs-mesh-tunnel)
10. [LLM Provider Strategy: Free-Tier Realities](#10-llm-provider-strategy-free-tier-realities)
11. [Verified vs Unverified Technical Decisions Matrix](#11-verified-vs-unverified-technical-decisions-matrix)
12. [Official Source File References](#12-official-source-file-references)

---

## 1. Executive Summary

**Switch_Rog** deploys a collaborative AI coding environment for two developers on separate Windows laptops over a 24-48 hour college hackathon with a **strict \$0.00 infrastructure budget**.

Following a deep audit of the official `sandbox-quantum/switch` repository, **Architecture B (The Official Switch Ecosystem Stack)** has been verified and selected as our deployment foundation.

### Key Architectural Resolutions
1. **Headless Agent Controller** `[Verified: Source Code]`: `switch-agent-controller` (`console/packages/agent-controller/`) runs as an independent headless CLI daemon on the workstation. It does **not** require the Switch Console desktop GUI to function.
2. **Native OpenCode Provider Adapter** `[Verified: Source Code]`: OpenCode is driven natively through the `ProviderAdapter` interface (`console/packages/agent-providers/src/adapter.ts`), communicating with OpenCode's local server over HTTP and Server-Sent Events (SSE). No ad-hoc custom bridge is required.
3. **Multi-Developer Shared Context** `[Verified: Source Code & Documentation]`: A single OpenCode agent serves multiple developers simultaneously through a shared Switch Room mapped 1:1 to a Mattermost channel.
4. **Native In-Room Approvals** `[Verified: Source Code & Documentation]`: Disabling `Auto mode` in the controller forces Switch Core to hold tool calls and dispatch approval prompts into the Mattermost thread before files are modified or commands executed.

---

## 2. Investigation & Verification of Core Inquiries

### 2.1 Can `switch-agent-controller` run independently without Switch Console? `[Verified: Source Code]`
* **Code Location**: `console/packages/agent-controller/`
* **Finding**: **YES.** `switch-agent-controller` is an independent Node.js package published as `@sandboxaq/switch-agent-controller`. It is designed specifically for headless servers, developer laptops, and CI runners without requiring an Electron desktop GUI.
* The Switch Console desktop application (`console/apps/switch-console-desktop/`) simply embeds this controller; the controller binary itself operates fully autonomously via CLI commands.

### 2.2 Exact Installation and Enrollment Commands `[Verified: Source Code & Documentation]`
* **Prerequisites**: Node.js `>= 22.13.0` or Node 24+.
* **Installation**:
  ```bash
  # Via the official installation script:
  curl -fsSL https://raw.githubusercontent.com/sandbox-quantum/switch/main/console/packages/agent-controller/install.sh | bash
  # Or via npm globally:
  npm install -g @sandboxaq/switch-agent-controller
  ```
* **Enrollment**:
  ```bash
  # Enrolls the local machine with the running Switch Gateway using a token generated from the Gateway UI:
  switch-agent-controller enroll <ENROLLMENT_TOKEN> --url http://localhost:3000
  ```
* **Status & Health Diagnostics**:
  ```bash
  switch-agent-controller doctor
  switch-agent-controller status
  ```

### 2.3 Windows vs WSL2 Support `[Verified: Source Code]`
* **Windows Support**: The controller codebase explicitly supports `win32` platform primitives (path resolution, process spawning, PTY handling).
* **Service Daemon Distinction**: While `switch-agent-controller install-service` natively configures `systemd` user units on Linux and `launchd` on macOS, Windows lacks native SCM integration in the CLI and must be run in an active terminal session.
* **Architectural Decision**: **Run `switch-agent-controller` inside WSL2 on Laptop 1.**
  - Docker Desktop on Windows runs containers inside the WSL2 Linux VM.
  - Running the controller inside WSL2 ensures direct, low-latency access to the Linux filesystem (`/repo`) where the codebase resides, avoiding Windows NTFS-to-WSL2 9P filesystem translation bottlenecks.

### 2.4 Switch Core ↔ Controller Authentication & Communication `[Verified: Source Code]`
* **Authentication**: During `enroll`, the controller generates an **X25519 keypair** and transmits its public key to Switch Core alongside the one-time enrollment token. Switch Core returns encrypted machine credentials.
* **Communication**: The controller maintains a persistent, full-duplex **Protocol 2 WebSocket stream** (`console/packages/agent-controller/src/connection.ts`) to Switch Core.
* Message turns and tool permission prompts flow over this WebSocket connection in real time.

### 2.5 Multi-Developer Serving in a Shared Mattermost Room `[Verified: Source Code & Documentation]`
* **Finding**: **YES.** In Switch, a **Room** represents a shared context boundary. When mapped to a Mattermost channel (`#ai-coding`), any message sent by Developer #1 or Developer #2 triggers a turn event in Switch Core.
* Switch Core appends the turn to the room history and dispatches the prompt over the WebSocket link to the enrolled OpenCode controller.
* When OpenCode yields output, it broadcasts back to the room, making all AI responses, diffs, and context visible to both developers simultaneously.

### 2.6 Native Human Approvals in this Deployment `[Verified: Source Code]`
* **Finding**: **YES.** Switch natively handles interactive tool approvals:
  - Setting `Auto mode = disabled` in the agent configuration ensures OpenCode does not auto-execute actions.
  - When OpenCode requests a file modification or shell execution, the `ProviderAdapter` yields an approval request.
  - The controller pushes this request over the WebSocket to Switch Core.
  - Switch Core logs an approval transaction in PostgreSQL and dispatches an interactive card/prompt into the Mattermost channel thread via `MattermostAdapter`.
  - When a developer replies `approve`, the event is captured by `_ws_handler`, and Switch Core authorizes the controller to proceed.

---

## 3. Architecture B Overview: Official Ecosystem Stack

Architecture B leverages the native Switch repository components without writing ad-hoc custom bridge servers:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        ARCHITECTURE B: OFFICIAL ECOSYSTEM FLOW                         │
│                                                                                        │
│  Mattermost (Chat)                                                                     │
│        ▲                                                                               │
│        │ WebSocket Ingress (`_ws_handler`) & REST Egress (`POST /posts`)               │
│        ▼                                                                               │
│  Switch Core (:8000) ◄──► PostgreSQL (:5432)                                           │
│        ▲                                                                               │
│        │ Full-Duplex Agent Protocol WebSocket (X25519 Encrypted)                       │
│        ▼                                                                               │
│  switch-agent-controller (Headless Workstation Daemon inside WSL2)                     │
│        ▲                                                                               │
│        │ ProviderAdapter (HTTP Dispatch + Server-Sent Events / SSE)                    │
│        ▼                                                                               │
│  OpenCode Engine (:4096) ──► Mounted Workspace Volume (/repo)                          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Component Disambiguation & Source-Code Paths

To prevent confusion between similar terms, each subsystem is mapped to its exact repository path:

| Subsystem Component | Exact Source-Code Path | Operational Boundary |
|---|---|---|
| **Mattermost Collaboration Adapter** | `core/switch_core/bridges/collaboration/mattermost.py` | Runs inside `switch-core` container. Connects to Mattermost WebSocket for real-time ingress and REST API for post egress. |
| **Switch Core Agent Protocol** | `core/switch_core/bridges/agent/` | Server-side routing layer inside `switch-core`. Dispatches room turns to enrolled agent controllers over WebSockets. |
| **Switch Agent Controller** | `console/packages/agent-controller/` | Standalone CLI daemon (`switch-agent-controller`). Enrolls machine with Core, maintains session leases, and spawns agent adapters. |
| **OpenCode Provider Adapter** | `console/packages/agent-providers/src/adapter.ts` | TypeScript adapter implementing `ProviderAdapter`. Communicates with OpenCode via HTTP and SSE. |
| **Switch Gateway** | `gateway/` | Web operator dashboard container running on port `3000` via `deploy/local/standalone-docker-compose.yml`. |
| **Switch Setup** | `setup/` | Bootstrapping container in compose (`--profile collab`) that pre-configures Mattermost bot accounts and room links. |

---

## 5. End-to-End Execution & Data Flow

```
Developer #1 or #2          Mattermost                Switch Core          switch-agent-controller        OpenCode (:4096)
       │                         │                          │                          │                          │
       │ 1. Post Coding Task     │                          │                          │                          │
       │    in #ai-coding        │                          │                          │                          │
       │────────────────────────►│                          │                          │                          │
       │                         │ 2. WebSocket Event       │                          │                          │
       │                         │    (`_ws_handler`)       │                          │                          │
       │                         │─────────────────────────►│                          │                          │
       │                         │                          │ 3. Dispatch Room Turn    │                          │
       │                         │                          │    over Protocol 2 WS    │                          │
       │                         │                          │─────────────────────────►│                          │
       │                         │                          │                          │ 4. HTTP POST /session    │
       │                         │                          │                          │    (Prompt dispatched)   │
       │                         │                          │                          │─────────────────────────►│
       │                         │                          │                          │                          │
       │                         │                          │                          │ 5. SSE Stream Event      │
       │                         │                          │                          │    (Tool Call Proposed)  │
       │                         │                          │                          │◄─────────────────────────│
       │                         │                          │ 6. Hold & Request        │                          │
       │                         │                          │    Approval              │                          │
       │                         │                          │◄─────────────────────────│                          │
       │                         │ 7. POST /api/v4/posts    │                          │                          │
       │                         │    (Approval Card)       │                          │                          │
       │                         │◄─────────────────────────│                          │                          │
       │ 8. Interactive Prompt   │                          │                          │                          │
       │    in Thread            │                          │                          │                          │
       │◄────────────────────────│                          │                          │                          │
       │                         │                          │                          │                          │
       │ 9. Reply `Approve`      │                          │                          │                          │
       │────────────────────────►│                          │                          │                          │
       │                         │ 10. WebSocket Post Event │                          │                          │
       │                         │─────────────────────────►│                          │                          │
       │                         │                          │ 11. Signal Resolution    │                          │
       │                         │                          │     over WebSocket       │                          │
       │                         │                          │─────────────────────────►│                          │
       │                         │                          │                          │ 12. Execute File Write   │
       │                         │                          │                          │     & Git Commit         │
       │                         │                          │                          │─────────────────────────►│
       │                         │                          │                          │                          │
       │                         │                          │                          │ 13. Completion SSE Event │
       │                         │                          │                          │◄─────────────────────────│
       │                         │                          │ 14. Return Final Turn    │                          │
       │                         │                          │◄─────────────────────────│                          │
       │                         │ 15. POST /api/v4/posts   │                          │                          │
       │                         │     (Execution Summary)  │                          │                          │
       │                         │◄─────────────────────────│                          │                          │
       │ 16. View Result & Diff  │                          │                          │                          │
       │◄────────────────────────│                          │                          │                          │
```

---

## 6. Human-in-the-Loop Approval Lifecycle

### 6.1 Policy Enforcement `[Verified: Source Code]`
* **Configuration**: In Switch Gateway/Console, the OpenCode agent profile has **Auto mode** set to **OFF**.
* **Behavior**: OpenCode is barred from executing tool operations (writing files, deleting paths, executing bash commands) without prior authorization.

### 6.2 Approval Execution Flow `[Verified: Source Code & Requires Practical Testing]`
1. **Interception**: OpenCode yields a tool execution proposal.
2. **Transaction Registration**: Switch Core creates an approval transaction record in PostgreSQL with an expiry window and unique token.
3. **Prompt Delivery**: `MattermostAdapter` posts a message in the thread:
   ```markdown
   ⚠️ **Action Approval Required from OpenCode**
   **Action**: Write file `src/auth.js` (+15 lines)
   **Command**: `git commit -m "feat(auth): validate inputs"`
   *Reply `approve` or `deny` in this thread.*
   ```
4. **Human Verification**: Developer #1 or Developer #2 replies `approve`.
5. **Resume & Audit**: `_ws_handler` captures the reply, verifies the user is an authorized team member, updates the transaction, and signals `switch-agent-controller` to authorize OpenCode's tool execution.

---

## 7. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           HOST LAPTOP 1 (Windows 11 + WSL2)                             │
│                                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │                Docker Compose Network (standalone-docker-compose.yml)              │  │
│  │                                                                                   │  │
│  │  ┌──────────────────────┐    WebSocket (_ws_handler)      ┌────────────────────┐  │  │
│  │  │                      │────────────────────────────────►│                    │  │  │
│  │  │  Mattermost Team     │                                 │   Switch Core      │  │  │
│  │  │  Edition Container   │◄────────────────────────────────│   (:8000)          │  │  │
│  │  │  (:8065)             │       POST /api/v4/posts        │                    │  │  │
│  │  └──────────┬───────────┘                                 └──────────┬─────────┘  │  │
│  │             │                                                        │            │  │
│  │             │                                     PostgreSQL Protocol│            │  │
│  │             ▼                                                        ▼            │  │
│  │  ┌──────────────────────┐                         ┌────────────────────────────┐  │  │
│  │  │   Switch Setup       │                         │   PostgreSQL 15 Container  │  │  │
│  │  │   (One-shot setup)   │                         │   (:5432 internal)         │  │  │
│  │  └──────────────────────┘                         │   [postgres_data]          │  │  │
│  │                                                   └────────────────────────────┘  │  │
│  │  ┌──────────────────────┐                                                         │  │
│  │  │   Switch Gateway     │                                                         │  │
│  │  │   Container (:3000)  │                                                         │  │
│  │  │   Web Operator UI    │                                                         │  │
│  │  └──────────────────────┘                                                         │  │
│  └──────────────────────────────────────────────────────┬────────────────────────────┘  │
│                                                         │ Protocol 2 WebSocket          │
│                                                         │ (X25519 Encrypted Stream)     │
│  ┌──────────────────────────────────────────────────────▼────────────────────────────┐  │
│  │                  WSL2 Workstation Environment (Host Laptop 1)                     │  │
│  │                                                                                   │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │      switch-agent-controller (Headless CLI Daemon inside WSL2)              │  │  │
│  │  │      Enrolled via: switch-agent-controller enroll <token>                   │  │  │
│  │  └──────────────────────────────────────┬──────────────────────────────────────┘  │  │
│  │                                         │                                         │  │
│  │                                         │ ProviderAdapter (HTTP & SSE)            │  │
│  │                                         ▼                                         │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │      OpenCode Background Server (:4096)                                     │  │  │
│  │  │      Invoked via: opencode serve --port 4096                                │  │  │
│  │  │      Working Directory: /repo (Cloned Git Workspace)                        │  │  │
│  │  └──────────────────────────────────────┬──────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────┼─────────────────────────────────────────┘  │
│                                            │ Outbound HTTPS API Calls                   │
└────────────────────────────────────────────┼────────────────────────────────────────────┘
                                             │
             ┌───────────────────────────────┴───────────────────────────────┐
             │                                                               │
             ▼                                                               ▼
┌─────────────────────────┐                                     ┌─────────────────────────┐
│ Cloud LLM API Providers │                                     │       GitHub.com        │
│ • Google Gemini (Free)  │                                     │     (Remote Origin)     │
│ • Groq Cloud (Free)     │                                     └────────────▲────────────┘
└─────────────────────────┘                                                  │
                                                                             │ git push / pull
                                                                             │
                                                                 ┌───────────┴────────────┐
                                                                 │    CLIENT LAPTOP 2     │
                                                                 │    (Developer #2)      │
                                                                 │                        │
                                                                 │ • Browser ──► :8065    │
                                                                 │ • Local Git Clone      │
                                                                 │ (Zero Server Software) │
                                                                 └────────────────────────┘
```

---

## 8. Two-Laptop Topology: Host vs Client Roles

| Role Dimension | Host Laptop 1 (Developer #1) | Client Laptop 2 (Developer #2) |
|---|---|---|
| **Hardware** | 16 GB RAM, Quad-Core, Windows 11 22H2+ | Standard laptop (Windows / macOS / Linux) |
| **Docker Containers** | `postgres`, `switch`, `gateway`, `mattermost`, `setup` | **None (Zero containers)** |
| **Host Workstation Processes** | `switch-agent-controller` daemon, OpenCode server (`:4096`) | **None (Zero server processes)** |
| **RAM Utilization** | 6 GB allocated to WSL2; ~2 GB for host apps | Standard browser usage (< 1 GB) |
| **Developer Interface** | Web Browser (`:8065`), Gateway UI (`:3000`) | Web Browser pointing to `http://<HOST_IP>:8065` |
| **Code Participation** | Hosts shared workspace `/repo` | Clones repository directly from GitHub |
| **API Keys & Secrets** | Holds `.env` with Gemini API key & bot tokens | **Requires zero secrets or API keys** |

---

## 9. Zero-Budget Networking: Hotspot vs Mesh Tunnel

### 9.1 Primary Plan: Smartphone Mobile Hotspot `[Requires Practical Testing]`
* **Problem**: University and hackathon guest Wi-Fi networks enforce **AP Client Isolation**, blocking direct TCP connections between laptops.
* **Architecture**: Developer #1 enables a 4G/5G mobile hotspot on their smartphone. Both laptops connect to this hotspot SSID.
* **Requirements & Testing**:
  1. Verify carrier firmware allows peer communication: `ping <HOST_IP>` from Laptop 2.
  2. Set Windows Network Profile to **Private** on Laptop 1:
     ```powershell
     Set-NetConnectionProfile -InterfaceAlias "Wi-Fi" -NetworkCategory Private
     ```
  3. Ensure Windows Firewall allows inbound TCP traffic on port `8065`.

### 9.2 Fallback Plan: Tailscale Mesh VPN `[Requires Practical Testing]`
* **Architecture**: When laptops cannot share a physical hotspot, both install **Tailscale** (free tier).
* Developer #2 accesses Mattermost directly via Developer #1's 100.x.y.z Tailscale IP (`http://100.x.y.z:8065`).
* Bypasses NAT, firewalls, and campus port blocks without requiring a paid domain or VPS.

---

## 10. LLM Provider Strategy: Free-Tier Realities

### 10.1 Primary Provider: Google Gemini 2.5 Flash `[Verified: Documentation]`
* **Cost**: \$0.00 via Google AI Studio API key (no credit card required).
* **Quota Reality `[Requires Practical Testing]`**:
  - Published nominal limits: ~15 RPM / ~1,500 RPD.
  - **Not guaranteed SLAs**: Subject to dynamic throttling and capacity shedding during peak hours.
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

### 10.2 Standby Secondary: Groq Cloud Free Tier `[Verified: Documentation]`
* **Cost**: \$0.00 via [console.groq.com](https://console.groq.com).
* **Models**: `llama-3.3-70b-versatile`, `qwen-2.5-coder-32b`.
* **Role**: Hot-swapped in `opencode.json` if Gemini encounters rate-limiting.

---

## 11. Verified vs Unverified Technical Decisions Matrix

| Subsystem Decision | Classification | Supporting Source / Path |
|---|---|---|
| **Standalone Compose Stack** | `[Verified: Source Code]` | `deploy/local/standalone-docker-compose.yml` |
| **Mattermost Ingress (`_ws_handler`)** | `[Verified: Source Code]` | `core/switch_core/bridges/collaboration/mattermost.py` |
| **Switch Setup Container** | `[Verified: Source Code]` | Service `setup` in compose under `--profile collab` |
| **Gateway Port 3000 Mapping** | `[Verified: Source Code]` | `GATEWAY_HOST_PORT=3000` mapped to `gateway` container |
| **Headless Controller Operation** | `[Verified: Source Code]` | `console/packages/agent-controller/` CLI daemon |
| **Controller Enrollment Protocol** | `[Verified: Source Code]` | `switch-agent-controller enroll` using X25519 handshake |
| **OpenCode ProviderAdapter** | `[Verified: Source Code]` | `console/packages/agent-providers/src/adapter.ts` (HTTP/SSE) |
| **Native In-Room Approvals** | `[Verified: Source Code]` | `core/switch_core/services/` question/approval records |
| **Mattermost Approval Interaction** | `[Requires Practical Testing]` | UI rendering (buttons vs text replies) on Team Edition |
| **Hotspot Direct LAN Routing** | `[Requires Practical Testing]` | Subject to smartphone isolation & Windows firewall profile |
| **Gemini Free-Tier Reliability** | `[Requires Practical Testing]` | Dynamic throttling requires Groq secondary standby |

---

## 12. Official Source File References

1. **Standalone Docker Compose Contract**: [`deploy/local/standalone-docker-compose.yml`](https://github.com/sandbox-quantum/switch/blob/main/deploy/local/standalone-docker-compose.yml)
2. **Environment Template**: [`deploy/local/.env.example`](https://github.com/sandbox-quantum/switch/blob/main/.env.example)
3. **Mattermost Collaboration Adapter**: `core/switch_core/bridges/collaboration/mattermost.py`
4. **Switch Agent Controller**: `console/packages/agent-controller/`
5. **OpenCode Provider Adapter**: `console/packages/agent-providers/src/adapter.ts`
6. **Agent Provider Documentation**: `console/docs/add-an-agent-provider.md`
7. **Switch Room Working Documentation**: [Switch AI Docs — Working with Agents in Rooms](https://docs.switchagents.ai)

---

*End of Architecture Document (Version 5.0)*
