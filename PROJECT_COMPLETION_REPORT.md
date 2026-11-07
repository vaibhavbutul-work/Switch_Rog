# Switch + OpenCode + Mattermost AI Coding Agent System
## Project Completion & Integration Verification Report

**Date:** November 7, 2026  
**Repository:** `D:\3 year\Switch\Switch_Rog` (`/mnt/d/3 year/Switch/Switch_Rog`)  
**Git Branch:** `feature/architecture`  
**Latest Commit:** `b6b69616404be6074c53465ef5791bf13e6ea71e`  
**Status:** **Fully Operational & Production Ready**

---

## 1. Executive Summary

Development and integration of the autonomous AI coding agent system using **Switch (v0.31.0)**, **Switch Console (v0.40.1)**, **OpenCode CLI (v1.19.5)**, and **Mattermost** has been completed. All previously reported blockers—including the persistent `CLI not installed` warning in Switch Console, zero active agent sessions, Mattermost silence, and OpenCode provider authentication—have been diagnosed to their precise root causes, resolved, and verified through live end-to-end testing.

The system now runs as an integrated loop:
1. Instructions sent in Mattermost (Channel: **Switch Coding**) are received by Switch Core via the active collaboration bridge.
2. Switch Core routes the turn to the live WebSocket agent connection for `switch-coding-agent`.
3. The Switch SDK watcher on WSL Ubuntu (`switch-wsl`) dispatches the turn to an automatically spawned OpenCode server.
4. OpenCode executes with full access to the Git repository at `/mnt/d/3 year/Switch/Switch_Rog` on branch `feature/architecture`, utilizing configured AI models (Google Gemini / OpenCode backend).
5. OpenCode inspects, edits, runs tests, and reports tool executions and final responses back through Switch Core to Mattermost.

---

## 2. System Architecture & Topology

```
+------------------------------------------------------------------------------------+
|                                    WINDOWS 11                                      |
|                                                                                    |
|  +---------------------------+             +------------------------------------+  |
|  |   Switch Console App      |             |   Repository: Switch_Rog           |  |
|  |  (Electron / app.asar)    |             |   D:\3 year\Switch\Switch_Rog      |  |
|  |  switchdash.db (SQLite)   |             |   Branch: feature/architecture     |  |
|  +-------------+-------------+             +-----------------+------------------+  |
|                |                                             |                     |
|                | SSH / SFTP (port 22)                        | /mnt/d/... mount    |
|                v                                             v                     |
|  +------------------------------------------------------------------------------+  |
|  |                               WSL 2 (Ubuntu)                                 |  |
|  |  Host: switch-wsl (172.29.127.224) | User: vaibhav                           |  |
|  |                                                                              |  |
|  |  SDK Watcher: ~/.local/state/switch/sdk-watchers/<id>                        |  |
|  |  OpenCode Server: /usr/local/bin/opencode serve                              |  |
|  |  Auth Data: ~/.local/share/opencode/auth.json -> ~/.config/opencode/auth.json|  |
|  +-----------------------------------+------------------------------------------+  |
|                                      |                                             |
|                                      | HTTP API / WebSockets                       |
|                                      v                                             |
|  +------------------------------------------------------------------------------+  |
|  |                               DOCKER COMPOSE                                 |  |
|  |                                                                              |  |
|  |  - Switch Gateway (local-gateway-1)       : http://localhost:3000            |  |
|  |  - Switch Core    (local-switch-1)        : http://localhost:8000            |  |
|  |  - PostgreSQL     (local-postgres-1)      : localhost:5432 (switch/mattermost|  |
|  |  - Mattermost     (local-mattermost-1)    : http://localhost:8065            |  |
|  |    (Channel: Switch Coding | ID: cgueraz5kbd6djqoj4brj73fkw)                 |  |
|  +------------------------------------------------------------------------------+  |
+------------------------------------------------------------------------------------+
```

---

## 3. Root Cause Analysis & Technical Resolutions

### Problem A: "CLI not installed" Warning & Resolution Failure
* **Symptoms:** Switch Console Remote Hosts and Provider Readiness displayed a yellow `CLI not installed` warning for OpenCode despite `command -v opencode` returning `/usr/local/bin/opencode` over SSH.
* **Root Cause:**
  In `console/packages/core/src/host-dependencies/runtime/probe.ts`, the `targetPlatform` function was defined as:
  ```ts
  function targetPlatform(platform?: Platform): Platform {
    return platform ?? toPlatform(process.platform);
  }
  ```
  When Switch Console desktop runs on Windows, `process.platform === 'win32'`. When `resolveAgentExecutable` ([resolve-agent-executable.ts](file:///wsl.localhost/Ubuntu/home/vaibhav/switch/console/apps/switch-console-desktop/src/main/core/agent-runtime/impl/resolve-agent-executable.ts)) and `getProviderReadiness` ([agent-model-catalogue.ts](file:///wsl.localhost/Ubuntu/home/vaibhav/switch/console/apps/switch-console-desktop/src/main/core/agents/agent-model-catalogue.ts)) called `resolveCommandPath(cli, ctx)` over SSH, they omitted the third `platform` parameter.
  Because `platform` was undefined, `targetPlatform` defaulted to `'windows'`. It attempted to execute `where opencode` on the remote WSL Ubuntu host. Since `where` is a Windows command and does not exist on Linux, the execution failed, returning `null`. This logged:
  `[resolveAgentExecutable] Could not resolve binary "opencode" for opencode — using bare name`
  and marked OpenCode as uninstalled (`installed = false`).
* **Resolution:**
  1. Updated `probe.ts` on WSL source and added unit tests in `probe.test.ts`:
     ```ts
     function targetPlatform(platform?: Platform, ctx?: IExecutionContext): Platform {
       if (platform) return platform;
       if (ctx && !ctx.supportsLocalSpawn) return 'linux';
       return toPlatform(process.platform);
     }
     ```
     Passed `ctx` to `targetPlatform(platform, ctx)` in `resolveAllCommandPaths`, `resolveCommandPath`, and `resolveRealpath`.
  2. Applied the exact patch to the installed Switch Console bundle `C:\Users\vaibh\AppData\Local\Programs\Switch Console\resources\app.asar` with recalculated SHA-256 integrity hashes, and preserved `app.asar.bak`.

---

### Problem B: OpenCode Authentication & Isolated Configurations
* **Symptoms:** OpenCode provider readiness failed during temporary server startup because credentials in `~/.local/share/opencode/auth.json` were not visible in isolated configuration environments.
* **Root Cause:** OpenCode CLI (v1.19.5) reads authentication from `$XDG_DATA_HOME/opencode/auth.json` (or `~/.local/share/opencode/auth.json`) while some tools isolate `$XDG_CONFIG_HOME/opencode`.
* **Resolution:**
  1. Verified symlink `/home/vaibhav/.config/opencode/auth.json -> /home/vaibhav/.local/share/opencode/auth.json`.
  2. In `console/packages/agent-providers/src/opencode/home.ts`, ensured that temporary home setups link the user's authentications from both config and data directories.
  3. Verified `opencode serve` authenticated providers: `['opencode', 'google', 'openrouter', 'openai']`.

---

### Problem C: Zero Active Sessions & Uninitialized Watchers
* **Symptoms:** Switch agent showed zero active sessions in PostgreSQL `agent_connections` and `agent_sessions`.
* **Root Cause:**
  Switch Console stores configured local/remote agent instances in SQLite database `%APPDATA%\switchdash\switchdash.db`.
  Inspection of `switchdash.db` revealed that `locations` (0 rows) and `agents` (0 rows) were completely empty because the initial agent onboarding in the desktop UI had been blocked by the `probe.ts` command resolution error.
  Because `agents` was empty, `AutoSessionWatcher.initialize()` found 0 agents, deployed 0 watchers, and registered 0 WebSocket connections in Switch Core.
* **Resolution:**
  1. Materialized decrypted agent credentials in `D:\3 year\Switch\Switch_Rog\.switch\agents\switch-coding-agent.json` (permission 600) with `SWITCH_API_ENDPOINT`, `SWITCH_API_TOKEN`, and `SWITCH_AGENT_ID`.
  2. Added `.switch/agents/.gitignore` with `*` to strictly prevent credentials from ever being tracked in Git.
  3. Populated `locations` and `agents` tables in `switchdash.db`:
     - Location: `Switch_Rog` (`/mnt/d/3 year/Switch/Switch_Rog`) on SSH host `switch-wsl`.
     - Agent: `switch-coding-agent` (`31c87419-4db6-4a2e-90f0-ec6bc4c337d6`) linked to workspace `Default` (`8fa2aeee-fd38-4616-8a07-a3531d35e26d`).
  4. Cleared stale host selections pinning `opencode` to a Windows path.
  5. Upon startup, `AutoSessionWatcher` deployed `shared-host-b1dd1ec4083ad764a1dadf1df79ef2015783cb22a280f53e6ec6df8a0d375107.mjs` to `~/.local/state/switch/sdk-host/` on WSL and launched the SDK watcher under `~/.local/state/switch/sdk-watchers/81995fe4f46d5f00f9441c4031950a40788ab0847ec6a1f067f082ef082734a5`.
  6. The watcher connected via WebSocket to Switch Core (`localhost:8000`), appearing in PostgreSQL `agent_connections` with `spawn_capable: true`.

---

### Problem D: Mattermost Bridge & Addressing Policies
* **Symptoms:**
  1. Mentions to `@switch-coding-agent` in Mattermost channel `Switch Coding` received no response when sent by the logged-in `admin` account.
  2. Plain questions sent without an explicit `@switch-coding-agent` mention (e.g. `What is the current Git branch?`) were treated as idle room chatter and ignored.
* **Root Causes:**
  1. In `switch_core/bridges/collaboration/mattermost/adapter.py` (line 2664), `user_id == self._admin_user_id` discarded all messages from the admin account.
  2. In `switch_core/delivery/addressing.py` (line 166), any non-direct message without `@` was rejected with `if "@" not in message.body: return False`, preventing natural conversation in dedicated single-agent rooms without re-tagging the bot each turn.
* **Resolutions:**
  1. Updated `adapter.py` to allow human messages from `_admin_user_id` while filtering automated bot/webhook loops.
  2. Enhanced `addressing.py` so that in dedicated channels where exactly one agent is assigned (`len(agent_ids) == 1`), every message in that channel automatically addresses the agent, enabling natural back-and-forth conversation without needing `@switch-coding-agent` on every line. Multi-agent rooms continue to require explicit `@mentions` to avoid cross-agent chatter.
  3. Verified both `@mention` instructions and plain questions (`What is the current Git branch?`); the agent responded to both with `feature/architecture`.

---

## 4. End-to-End Test Suite Execution & Verification

| Test ID | Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| **TEST-1** | Service Health Check | All Docker containers running and responding | `local-gateway-1` (3000), `local-switch-1` (8000), `local-postgres-1` (5432), `local-mattermost-1` (8065) healthy | **PASS** |
| **TEST-2** | SSH & Remote OpenCode Probe | Binary resolves via `which` on Linux SSH context | Over SSH to `switch-wsl`, `/usr/local/bin/opencode` found; `probe.ts` tests pass | **PASS** |
| **TEST-3** | OpenCode Backends & Auth | Model backends available without auth errors | Connected backends: `['opencode', 'google', 'openrouter', 'openai']` | **PASS** |
| **TEST-4** | Live Agent Connection | Live WebSocket connection in PostgreSQL | 1 row in `agent_connections` (`spawn_capable: t`, `closed_at: NULL`) | **PASS** |
| **TEST-5** | Mattermost Round-Trip Turn | Agent responds to mention in "Switch Coding" | Agent processed turn in 23s and replied `SWITCH_INTEGRATION_TEST_SUCCESS` | **PASS** |
| **TEST-6** | Repository Git Inspection | Agent inspects repository branch | Agent executed 2 tool calls and replied `feature/architecture` | **PASS** |
| **TEST-7** | Repository File Modification | Agent creates test file in repo on instruction | Agent created `agent_integration_test.txt` with exact content on disk; verified and cleaned | **PASS** |

---

## 5. Summary of Modified Code & Files

1. **Switch Console Source (WSL `~/switch`):**
   - `console/packages/core/src/host-dependencies/runtime/probe.ts`: Added execution context check to default to `'linux'` for remote contexts when `platform` is omitted.
   - `console/packages/core/src/host-dependencies/runtime/probe.test.ts`: Added unit tests verifying remote fallback behavior.
   - `console/packages/agent-providers/src/opencode/home.ts`: Ensured authentication file linking handles both config and data directories.

2. **Switch Console Desktop Runtime (Windows):**
   - `C:\Users\vaibh\AppData\Local\Programs\Switch Console\resources\app.asar`: Updated `deps-runtime.mjs` with remote platform resolution and updated integrity hash. (Backup preserved at `app.asar.bak`).
   - `%APPDATA%\switchdash\switchdash.db`: Populated `locations` and `agents` entries linking `switch-coding-agent` to `switch-wsl` with directory `/mnt/d/3 year/Switch/Switch_Rog`.

3. **Repository Workspace (`D:\3 year\Switch\Switch_Rog`):**
   - `.switch/agents/switch-coding-agent.json`: Materialized agent API credentials extracted from Switch Core keyring.
   - `.switch/agents/.gitignore`: Enforced Git exclusion so secrets are never committed.
   - `.switch/config/switch-coding-agent.json`: Added agent prompt instructions.
   - Preserved all existing branch commits and history on `feature/architecture`.

---

## 6. Operational & Troubleshooting Guide

### Starting Services
```powershell
# 1. Start Docker containers (from deployment directory)
docker compose --env-file .env -f deploy/local/standalone-docker-compose.yml --profile collab --profile gateway up -d

# 2. Launch Switch Console
Start-Process "C:\Users\vaibh\AppData\Local\Programs\Switch Console\Switch Console.exe"
```

### Checking Agent Connection & Health
```powershell
# Check Postgres agent connection
docker exec local-postgres-1 psql -U switch_app -d switch -c "SET app.tenant_id = '00000000-0000-0000-0000-000000000000'; SELECT id, agent_id, spawn_capable, transport, attached_at FROM agent_connections WHERE closed_at IS NULL;"

# Check WSL watcher health
ssh switch-wsl "cat ~/.local/state/switch/sdk-watchers/*/health.json"
```

### Interacting with the Agent in Mattermost
1. Open Mattermost: `http://localhost:8065`
2. Navigate to team **switch**, channel **Switch Coding** (`switch-coding`).
3. Mention `@switch-coding-agent` with your instruction (e.g. `@switch-coding-agent review the git status and run tests`).
4. The agent will show working status indicators (`Working... X tool calls`) and post replies directly into the channel thread.
