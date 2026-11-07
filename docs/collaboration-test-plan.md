# Two-Developer Collaboration & Remote Networking Test Plan — Switch_Rog

## 1. Scope & Responsibility Demarcation

In the **Switch_Rog** architecture, two developers collaborate in real time:
* **Sunayana:** Project Planning & Workflow Lead (Client laptop / remote peer).
* **Vaibhav:** Technical Lead & Infrastructure Host (Host server / container runner).

### Critical Operational Boundary:
* **GitHub Repository vs. Live Server:** Sharing a GitHub repository (`vaibhavbutul-work/Switch_Rog`) synchronizes source code and documentation, but does **not** automatically share a running Switch or Mattermost runtime.
* **Vaibhav's Responsibility:** Deploying the Switch/Mattermost container environment, configuring network listener addresses, and providing secure remote connectivity (e.g., via private overlay networks like Tailscale or authenticated tunnels) without exposing unprotected ports to the public internet.
* **Sunayana's Responsibility:** Connecting from her developer workstation (`C:\Users\sunay\Switch_Rog`), validating account access, verifying multi-user messaging, testing thread-based agent interactions, and evaluating disconnection resilience.

---

## 2. Test Environment Setup & Prerequisites

```
+------------------------------------+          +------------------------------------+
|        Vaibhav's Workstation       |          |       Sunayana's Workstation       |
|  - Host OS: Windows / WSL2         |          |  - Client OS: Windows 11           |
|  - Running: Switch Console         |  Secure  |  - Web Browser / Mattermost Client |
|  - Running: Mattermost Container   |<========>|  - Git Branch:                     |
|  - Running: OpenCode Subprocess    | (Tunnel) |    feature/project-planning        |
|  - Network: Private LAN / Tailscale|          |  - Network: Private LAN / Tailscale|
+------------------------------------+          +------------------------------------+
```

### Preconditions:
1. Mattermost instance is running on the host machine.
2. Two distinct user accounts exist:
   * Account A: `sunayana` (Role: Member / Team Admin)
   * Account B: `vaibhav` (Role: System Admin)
3. Shared channel `#bug-reports` and `#project-general` are created under team `switch-rog`.
4. No direct public port forwarding (Port 8065 or 3000) over raw HTTP.

---

## 3. Collaboration Test Matrix (11 Core Scenarios)

*Status Note: In compliance with project rules, all actual results are marked **NOT TESTED** pending live infrastructure availability.*

| Test ID | Scenario Name | Test Steps | Expected Behaviour | Status | Evidence Target |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **COL-01** | Separate Account Authentication | 1. Sunayana logs into Mattermost via `http://<host-address>:8065` with credentials `sunayana`.<br>2. Vaibhav logs in via separate browser/session with `vaibhav`. | Both users authenticate successfully with independent sessions, distinct user profiles, and avatars. | NOT TESTED | `docs/evidence/col-01-auth.png` |
| **COL-02** | Shared Room Membership | 1. Both users join channel `#bug-reports`.<br>2. Check member roster in channel header. | Channel member list displays both `sunayana` and `vaibhav`. | NOT TESTED | `docs/evidence/col-02-roster.png` |
| **COL-03** | Sunayana -> Vaibhav Real-Time Message | 1. Sunayana posts in `#bug-reports`: `"Hello Vaibhav, testing chat sync."`<br>2. Observe Vaibhav's client. | Message appears in Vaibhav's active view within **1 second** without manual browser refresh. | NOT TESTED | `docs/evidence/col-03-msg-sync.log` |
| **COL-04** | Vaibhav -> Sunayana Real-Time Message | 1. Vaibhav replies: `"Acknowledged Sunayana, live sync operational."`<br>2. Observe Sunayana's client. | Message appears in Sunayana's view within **1 second** with correct timestamp and sender badge. | NOT TESTED | `docs/evidence/col-04-msg-reply.log` |
| **COL-05** | Threaded Discussion Coexistence | 1. Sunayana starts a thread on a bug report.<br>2. Vaibhav replies inside the thread.<br>3. Sunayana replies inside the thread. | All replies stay grouped inside the `root_id` thread panel; root channel remains uncluttered. | NOT TESTED | `docs/evidence/col-05-thread.log` |
| **COL-06** | Shared AI Agent Visibility | 1. Sunayana posts `@opencode status` in `#bug-reports`.<br>2. Observe both clients. | Agent response appears simultaneously in both Sunayana's and Vaibhav's client views in real time. | NOT TESTED | `docs/evidence/col-06-agent-view.log` |
| **COL-07** | Dual-User Agent Steering | 1. Sunayana prompts agent with bug description.<br>2. Vaibhav replies in the active thread with extra constraint.<br>3. Agent outputs updated plan. | Agent plan reflects constraints provided by **both** developers. | NOT TESTED | `docs/evidence/col-07-dual-steer.log` |
| **COL-08** | Channel & Role Permissions | 1. Sunayana attempts to post in `#bug-reports` (Permitted).<br>2. Check permission boundaries for read/write access. | Standard developers can post, reply, and approve; system administration settings remain protected. | NOT TESTED | `docs/evidence/col-08-permissions.log` |
| **COL-09** | Client Connection Interruption | 1. While a thread is active, Sunayana temporarily disconnects Wi-Fi for 15 seconds, then reconnects. | Client displays "Reconnecting..." indicator; upon reconnect, missed messages sync automatically. | NOT TESTED | `docs/evidence/col-09-reconnect.log` |
| **COL-10** | Host Laptop Sleep / Offline | 1. Host machine (Vaibhav) is suspended or Docker service is stopped.<br>2. Sunayana attempts to send a message. | Client displays clear connection error (HTTP 502 / network offline); does not silently lose messages. | NOT TESTED | `docs/evidence/col-10-host-down.log` |
| **COL-11** | Full Host Recovery & Session Resumption | 1. Host resumes and Switch/Mattermost container restarts.<br>2. Sunayana refreshes browser. | Workspace reloads; channel history is fully restored from persistent database; pending sessions can resume. | NOT TESTED | `docs/evidence/col-11-recovery.log` |

---

## 4. Network Security & Safe Tunneling Guidelines

To ensure the system adheres to **Section 10 (Security Rules)**:
1. **Never Expose Raw HTTP Ports:** Direct port mapping of Mattermost (`8065`) or Switch (`3000`) to the public internet via router port forwarding is **prohibited**.
2. **Approved Remote Pairing Options:**
   * **Option A (Zero-Cost Private Mesh - Recommended):** Tailscale or ZeroTier network joining both laptops. Traffic is encrypted end-to-end; services bind only to the private 100.x.x.x IP.
   * **Option B (Authenticated Reverse Proxy):** Cloudflare Tunnel (`cloudflared`) pointing to `localhost:8065` with Cloudflare Access pin/email authentication.
3. **Secret Protection:** Remote connection URLs or pre-shared tunnel keys must reside exclusively in uncommitted local configuration and never appear in public git commits.
