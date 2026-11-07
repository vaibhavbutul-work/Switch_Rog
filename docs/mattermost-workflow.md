# Mattermost Workspace & Workflow Architecture — Switch_Rog

## 1. Executive Summary & Integration Architecture

As part of the **Switch_Rog** collaborative development platform, **Mattermost** serves as the unified communication layer where human engineers (Sunayana and Vaibhav) and the AI coding agent (**OpenCode**) collaborate.

The core communication topology is:

```
[Developer: Sunayana] <---+
                           |---> [Mattermost Channel / Thread]
[Developer: Vaibhav]   <---+                |
                                            | WebSocket / REST API v4
                                            v
                                 [Switch Messaging Bridge]
                                            |
                                            v
                                  [OpenCode AI Agent]
```

---

## 2. Official Switch & Mattermost Integration Research

Based on research into the official **Switch** platform (`sandbox-quantum/switch`) and the **Flip the Switch Hackathon** guidelines:

### 2.1 Bundled Mattermost Setup vs. Standalone Installation
1. **Mattermost is Bundled:** The official Switch Console (the desktop application orchestrating local servers and agent pipelines) includes and automatically manages a local **bundled Mattermost container instance**.
2. **No Duplicate Installation Required:** A separate, manual Mattermost installation is **not** required. Running a duplicate standalone Mattermost server causes port collisions (standard port `8065`) and exhausts laptop memory. Vaibhav manages the container configuration through Switch Console.
3. **Infrastructure Responsibility:** As Technical Lead, Vaibhav deploys the Switch bridge and container runtime. Sunayana designs the workspace topology, channel taxonomy, and validation test plan.

---

## 3. User Accounts & Authentication

### 3.1 Account Taxonomy

| User Role | Display Name | Username | Account Purpose |
| :--- | :--- | :--- | :--- |
| **Workflow Lead** | Sunayana Kamat | `sunayana` | Initiates bug tickets, reviews agent plans, issues approvals (`!approve`/`!reject`), and tests code fixes. |
| **Technical Lead** | Vaibhav Kumar | `vaibhav` | Administers team workspace, provides technical reproduction logs, reviews diffs, and approves GitHub merges. |
| **AI Coding Agent** | OpenCode Agent | `opencode` | Bot account managed by Switch. Ingests tasks, posts plans, diffs, and execution logs in threads. |

### 3.2 Authentication & Access Tokens
1. **Human Developers:** Authenticate using email and password against the local Mattermost instance.
2. **Team Invitation:** Developer A creates the team `switch-rog`. Developer B joins via a local invite link (`http://localhost:8065/signup_user_complete/?id=...`).
3. **Bot Account & Token:** OpenCode interacts through a Mattermost Bot Account equipped with a Personal Access Token (PAT).
   * Token permissions required: `post:all`, `channel:read`, `channel:write`.
   * Secure Storage: The bot token is stored strictly in `.env` (`MATTERMOST_BOT_TOKEN`) and must **never** be committed to Git.

---

## 4. Channel Structure & Taxonomy

To keep project discussions organized and isolate agent activity from casual chatter, the following channel structure is established:

```
Switch_Rog Team Workspace
├── 📢 ~project-general      (Team coordination, announcements, standup sync)
├── 🐛 ~bug-reports          (Issue triage, reproduction steps, initial agent invocation)
├── 🤖 ~ai-agent-tasks       (Scaffolding, refactoring, exploratory tasks)
└── 🔍 ~code-review          (Pull Request links, peer code reviews, CI status alerts)
```

### 4.1 Detailed Channel Specifications

#### 1. `~project-general`
* **Purpose:** High-level project planning, sync notes between Sunayana and Vaibhav, hackathon milestones, and general team communications.
* **Agent Participation:** Passive / No agent mentions.

#### 2. `~bug-reports`
* **Purpose:** The primary operational channel for defect investigation and resolution (e.g., the online shopping "Place Order" button bug).
* **Workflow:**
  1. Sunayana posts bug description and mentions `@opencode`.
  2. Vaibhav replies in the thread with console errors and reproduction steps.
  3. All agent responses, plans, approvals, and diffs remain strictly in the thread.

#### 3. `~ai-agent-tasks`
* **Purpose:** Feature scaffolding, test case creation, documentation drafting, or standalone helper script generation.
* **Workflow:** Developers prompt `@opencode` for specific isolated tasks.

#### 4. `~code-review`
* **Purpose:** GitHub Pull Request notifications, CI/CD pipeline results, and peer review sign-offs.
* **Workflow:** Once an agent-assisted fix is approved and pushed, the GitHub PR link is posted here for Vaibhav's review before merging.

---

## 5. Team Collaboration & Message Routing Process

```
[Sunayana posts in #bug-reports]
  |
  +--> Mention: @opencode
  |
[Vaibhav replies in thread with reproduction context]
  |
  v
[Mattermost WebSocket Gateway]
  |
  +--> Event: post_created
  |
[Switch Bridge Ingestion Engine]
  |
  +--> Matches bot mention / thread root_id
  +--> Bundles Sunayana + Vaibhav messages
  +--> Dispatches payload to OpenCode session
  |
[OpenCode AI Agent]
  |
  +--> Analyzes repository
  +--> Formulates plan
  |
[Switch Bridge]
  |
  +--> Formats Markdown plan
  +--> Posts reply to thread: "Reply !approve to execute"
  |
[Human Developer]
  |
  +--> Posts !approve in thread
  |
[Switch intercepts approval -> Signals OpenCode to execute]
```

### 5.1 Technical Configuration Required from Vaibhav
To allow Switch to bind cleanly to Mattermost, Vaibhav must provision and configure the following parameters in the local `.env`:
* `MATTERMOST_URL`: `http://localhost:8065` (or Docker service URL)
* `MATTERMOST_TEAM_NAME`: `switch-rog`
* `MATTERMOST_BOT_TOKEN`: PAT generated from Mattermost System Console
* `MATTERMOST_LISTEN_CHANNELS`: `bug-reports,ai-agent-tasks`
* `SWITCH_GATEWAY_PORT`: Port for webhook/control listener
* `OPENCODE_WORKSPACE_PATH`: Local absolute path to the repository

---

## 6. Verification & Test Procedure (Stage 2 Validation Plan)

*Note: In accordance with our Definition of Done, tests are marked **PLANNED / NOT TESTED** until the local container runtime is deployed by Vaibhav.*

| Test ID | Objective | Test Steps | Expected Output | Status |
| :--- | :--- | :--- | :--- | :--- |
| **MM-01** | Verify Mattermost Workspace Accessibility | 1. Navigate to `http://localhost:8065`.<br>2. Log in as `sunayana`. | Login succeeds; team dashboard loads. | NOT TESTED (Pending Infrastructure) |
| **MM-02** | Two-User Channel Messaging | 1. `sunayana` posts in `#project-general`.<br>2. `vaibhav` views channel. | Message renders in `vaibhav` view within 1s. | NOT TESTED (Pending Infrastructure) |
| **MM-03** | Channel Structure Creation | Verify existence of `#project-general`, `#bug-reports`, `#ai-agent-tasks`, `#code-review`. | All 4 channels exist and are accessible to both users. | NOT TESTED (Pending Infrastructure) |
| **MM-04** | Bot Mention Recognition | In `#bug-reports`, post `@opencode ping`. | Bot acknowledges with `👀` or status post. | NOT TESTED (Pending Infrastructure) |
| **MM-05** | Thread Isolation Check | 1. Post `@opencode Task A` in Thread 1.<br>2. Post `@opencode Task B` in Thread 2. | Replies are strictly routed to their respective threads. | NOT TESTED (Pending Infrastructure) |

---

## 7. Known Limitations & Fallbacks

1. **Local Host Loopback vs. Remote Pairing:** If Sunayana and Vaibhav are working on separate physical laptops, accessing `http://localhost:8065` will not work out-of-the-box. Vaibhav must either:
   * Provide access via a private overlay network (e.g., Tailscale / WireGuard), or
   * Use a secure reverse tunnel (e.g., Cloudflare Tunnel / ngrok) with authenticated tokens.
   * *Safety Rule:* Direct public port forwarding without TLS and authentication is prohibited.
2. **WebSocket Keep-Alives:** Mattermost WebSocket connections can drop if the laptop enters sleep mode. The Switch adapter must implement exponential backoff reconnection.
3. **Interactive Attachment Compatibility:** If Mattermost interactive buttons fail due to webhook callback routing issues on localhost, the system automatically falls back to keyword triggers (`!approve`, `!reject`).
