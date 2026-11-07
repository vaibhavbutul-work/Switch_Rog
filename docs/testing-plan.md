# Master Verification & Testing Plan â€” Switch_Rog

## 1. Overview & Verification Strategy
This document details the comprehensive testing protocol for the **Switch_Rog** collaborative development platform. It covers:
1. Git branch and source integrity.
2. Mattermost communication and multi-user sync.
3. Switch message routing and session handling.
4. OpenCode AI coding capabilities and sandboxing.
5. Human approval and rejection enforcement.
6. GitHub Pull Request peer review workflows.
7. Failure, error recovery, and timeout safeguards.
8. Evidence collection standards.

---

## 2. Testing Matrix by Subsystem

*Status Note: In compliance with project integrity guidelines, test results are marked according to real verification. Components requiring un-deployed infrastructure are marked **NOT TESTED (Pending Infrastructure)**.*

### 2.1 Git Repository & Branch Hygiene Tests

| Test ID | Test Description | Verification Procedure | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **GIT-01** | Branch Isolation | Run `git branch` on developer workstations. | Sunayana is on `feature/project-planning`; Vaibhav is on `feature/architecture`. `main` has no unreviewed direct commits. | **VERIFIED (Pass)** |
| **GIT-02** | Clean Working Tree | Run `git status`. | Working tree is clean or tracks only intentionally assigned documentation files. | **VERIFIED (Pass)** |
| **GIT-03** | Secret Commit Audit | Run grep across repository for API tokens, passwords, private keys (`ghp_`, `BEGIN OPENSSH`). | Zero secrets found in committed history. | **VERIFIED (Pass)** |

### 2.2 Mattermost Communication & Multi-User Tests

| Test ID | Test Description | Verification Procedure | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **MMT-01** | Account Separation | Verify `sunayana` and `vaibhav` login credentials. | Distinct user profiles, independent browser sessions. | NOT TESTED (Pending Infrastructure) |
| **MMT-02** | Real-Time Sync | Post message in `#bug-reports` from User A. | Renders in User B's client in < 1s. | NOT TESTED (Pending Infrastructure) |
| **MMT-03** | Channel Topology | Inspect channel list in Mattermost team. | `#project-general`, `#bug-reports`, `#ai-agent-tasks`, `#code-review` exist. | NOT TESTED (Pending Infrastructure) |

### 2.3 Switch Bridge & Message Routing Tests

| Test ID | Test Description | Verification Procedure | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **SWT-01** | Webhook / WebSocket Reception | Mention `@opencode` in `#bug-reports`. | Switch bridge terminal logs show incoming event parsed with correct `root_id`. | NOT TESTED (Pending Infrastructure) |
| **SWT-02** | Thread-to-Session Mapping | Open two concurrent threads with `@opencode`. | Switch assigns distinct session IDs; no cross-talk between conversations. | NOT TESTED (Pending Infrastructure) |
| **SWT-03** | Acknowledgment Latency | Measure elapsed time between mention and bot reaction. | Emoji reaction or acknowledgment post appears in < 3s. | NOT TESTED (Pending Infrastructure) |

### 2.4 OpenCode AI Agent Capability Tests

| Test ID | Test Description | Verification Procedure | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **AGT-01** | Bug Diagnosis & Plan Output | Report Place Order button bug in thread. | OpenCode reads `checkout.js`, diagnoses root cause, posts structured plan. | NOT TESTED (Pending Infrastructure) |
| **AGT-02** | Clarification on Vague Prompt | Post `"The app is broken"` in thread. | OpenCode requests specific error logs and reproduction steps without guessing. | NOT TESTED (Pending Infrastructure) |
| **AGT-03** | Code Modification & Tests | Instruct agent to fix null check in `cartService.js`. | Agent edits file, writes unit test, runs test runner, captures stdout. | NOT TESTED (Pending Infrastructure) |
| **AGT-04** | Sandbox File Restriction | Prompt agent to read/edit `/etc/passwd` or outside directory. | Process runner rejects access; logs security error. | NOT TESTED (Pending Infrastructure) |
| **AGT-05** | Destructive Command Filter | Prompt agent to execute `rm -rf /` or `sudo`. | Switch command filter blocks execution immediately. | NOT TESTED (Pending Infrastructure) |

### 2.5 Human Approval & Rejection Tests

| Test ID | Test Description | Verification Procedure | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **APV-01** | Plan Approval (`!approve`) | Post `!approve` to valid proposed plan. | Agent transitions from Planning to Execution phase. | NOT TESTED (Pending Infrastructure) |
| **APV-02** | Plan Rejection (`!reject`) | Post `!reject` to proposed plan. | Task terminates immediately; no files modified. | NOT TESTED (Pending Infrastructure) |
| **APV-03** | Diff Rejection & Targeted Revert | Post `!reject` after inspecting git diff. | Targeted rollback triggered for session files (`git checkout HEAD -- <files>` or task branch removal); unrelated uncommitted files remain preserved. | NOT TESTED (Pending Infrastructure) |
| **APV-04** | Plan Modification (`!modify`) | Post `!modify handle undefined also`. | Agent revises plan incorporating new constraint and re-prompts for approval. | NOT TESTED (Pending Infrastructure) |

### 2.6 GitHub Review & Handoff Tests

| Test ID | Test Description | Verification Procedure | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **GTH-01** | Feature Branch Push | Inspect remote repository after diff approval. | New branch `feature/fix-place-order-button` exists on GitHub. | NOT TESTED (Pending Infrastructure) |
| **GTH-02** | Pull Request Opening | Check open PRs on `vaibhavbutul-work/Switch_Rog`. | PR exists with title, description, diff summary, and test logs. | NOT TESTED (Pending Infrastructure) |
| **GTH-03** | Peer Review Enforcement | Attempt to merge PR without secondary human review. | Blocked by GitHub protection rule; requires approved review from teammate. | NOT TESTED (Pending Infrastructure) |
| **GTH-04** | Merge & Notification | Vaibhav approves and merges PR on GitHub. | Webhook posts completion notice in Mattermost `#code-review`. | NOT TESTED (Pending Infrastructure) |

### 2.7 Failure & Recovery Tests

| Test ID | Test Description | Verification Procedure | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **FLR-01** | Failing Unit Test Reporting | Force test failure during agent run. | Agent captures stderr/stacktrace, reports failing test accurately, does not claim success. | NOT TESTED (Pending Infrastructure) |
| **FLR-02** | Command Timeout Safeguard | Execute long-running loop (`yes > /dev/null`). | Subprocess terminates at 60s timeout; reports timeout error in thread. | NOT TESTED (Pending Infrastructure) |
| **FLR-03** | Network Disconnect Recovery | Toggle client network off for 20s during active session. | Client reconnects, session resumes without message loss. | NOT TESTED (Pending Infrastructure) |

---

## 3. Evidence Collection Protocol

For every test executed during Stage 4 verification:
1. **Raw Logs:** Save terminal stdout/stderr to `docs/evidence/<test-id>-<name>.log`.
2. **Visual Proof:** Capture screenshots of Mattermost threads showing user prompts, agent replies, diffs, and approval keywords (`docs/evidence/<test-id>.png`).
3. **Git Audit:** Record commit SHAs and GitHub PR links in the test log.
4. **Zero Fabrication:** Never record simulated output as verified live test evidence.
