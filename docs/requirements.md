# Requirements Specification â€” Switch_Rog

## 1. Project Overview
**Switch_Rog** is an open, zero-cost, collaborative AI-assisted software development workflow designed for engineering teams. It integrates team chat in **Mattermost** with an autonomous AI coding agent (**OpenCode**), orchestrated via the **Switch** messaging bridge, and governed by **GitHub** source control for traceable versioning and peer code reviews.

Rather than confining AI coding assistants to a single developer's private local editor or terminal, Switch_Rog brings the AI coding agent directly into a shared team channel. Multiple developers can observe, guide, steer, and review the AI coding agent together in real time, with strict human-in-the-loop approval gates before any code modifications, shell commands, or branch pushes take effect.

---

## 2. Problem Statement
Current AI coding tools (editor extensions, terminal CLIs) operate in isolated, single-user silos, creating severe bottlenecks for software engineering teams:
1. **Siloed Context & Invisible Prompts:** When a developer interacts with an AI agent locally, teammates cannot see the prompt history, assumptions, reasoning steps, or files touched until a Pull Request appears.
2. **Duplication of Effort & Merge Conflicts:** Two developers working concurrently on related bugs may instruct local AI agents down conflicting architectural paths, resulting in complex merge conflicts.
3. **Absence of Pre-Execution Peer Review:** Traditional AI tools apply changes immediately to the local working directory. Teammates cannot intervene, review the agent's plan, or intercept dangerous terminal commands prior to execution.
4. **Knowledge Sharing Deficit:** Junior engineers and peer reviewers are excluded from observing how senior engineers formulate constraints, decompose problems, and validate agent solutions.

---

## 3. Project Objectives
1. **Shared Team Visibility:** Bring AI coding assistance into a shared team communication platform (Mattermost) so all developers maintain mutual awareness of active agent tasks.
2. **Bridge-Driven Coordination via Switch:** Use Switch as the central messaging and routing infrastructure between Mattermost chat rooms and OpenCode without building ad-hoc, brittle chatbots.
3. **Strict Human-in-the-Loop Governance:** Enforce mandatory human approval checkpoints before code edits, shell commands, or git branch pushes can be executed.
4. **Traceable Git & GitHub Integration:** Ensure every AI-assisted code change is isolated in a feature branch and submitted as a GitHub Pull Request for human review and CI verification. Never allow direct commits to the `main` branch.
5. **Zero-Cost & Local Viability:** Target a zero-cost infrastructure model runnable on developer hardware (Docker Desktop, WSL2/Windows, local containers, free/open-source tools) without requiring paid cloud hosting, domains, or paid subscriptions.

---

## 4. Target Users & Personas

### Persona 1: Sunayana â€” Project Planning & Workflow Lead (Full-Stack Developer)
* **Background:** Undergraduate software engineering student working on full-stack application development.
* **Goal:** Wants to delegate bug investigations, test creation, and bug fixes to an AI agent while maintaining complete visibility with her teammate in a shared chat workspace.
* **Pain Point:** Frustrated when AI assistants make silent, uncontrolled changes or when chat context cannot be shared with collaborators.
* **Role in Switch_Rog:** Posts bug reports, reviews agent-proposed plans, specifies constraints, inspects code diffs, and approves or rejects actions.

### Persona 2: Vaibhav â€” Technical Lead & System Architect
* **Background:** Student developer responsible for infrastructure reliability, bridge connectivity, and runtime security.
* **Goal:** Requires total oversight over automated file modifications and terminal commands to prevent build breaks, unsafe shell operations, or repository pollution.
* **Pain Point:** Distrusts black-box agents that run unvetted terminal commands or bypass git review workflows.
* **Role in Switch_Rog:** Configures Switch and OpenCode runtimes, provides reproduction details in chat, reviews proposed diffs, approves GitHub PR merges, and monitors container health.

### Persona 3: Agile Student & Hackathon Development Teams
* **Background:** 2â€“4 developers collaborating under strict deadlines with zero budget.
* **Goal:** Rapid triage, collaborative debugging, and safe scaffolding of features without stepping on each other's code.
* **Pain Point:** Lack of expensive enterprise tooling and difficulty coordinating who is fixing what.
* **Role in Switch_Rog:** Join the shared Mattermost channel, observe active agent tasks in isolated threads, and contribute context or approvals.

---

## 5. User Stories

* **US-01 (Shared Bug Triage):** As a developer (Sunayana), I want to post a bug report in our shared Mattermost channel and tag the AI agent, so that my teammate (Vaibhav) and the agent see the exact same problem statement simultaneously.
* **US-02 (Collaborative Context Enrichment):** As a technical lead (Vaibhav), I want to reply in the active Mattermost thread with reproduction steps and architectural constraints, so that the AI agent incorporates both developers' input before generating code.
* **US-03 (Transparent Plan Review):** As a developer, I want the AI agent to publish a clear, structured implementation plan in the thread before modifying any files, so that our team can review the proposed approach.
* **US-04 (Mandatory Human Approval Gate):** As a reviewer, I want the system to require explicit human approval (`!approve` / interactive button) before any code is modified, terminal commands run, or branches pushed, so that unapproved or hallucinated actions are blocked.
* **US-05 (Rejection & Course Correction):** As a developer, I want to reject an agent's proposal (`!reject` or `!modify <feedback>`) so that the agent aborts or revises its plan without corrupting the workspace.
* **US-06 (Diff & Test Inspection):** As a team, we want the agent to present a unified git diff and test suite execution logs directly in the chat thread, so that we can verify code correctness before opening a Pull Request.
* **US-07 (Traceable GitHub Review):** As a tech lead, I want approved changes pushed to a distinct feature branch with an open Pull Request on GitHub, so that standard peer code review and merging policies are respected.
* **US-08 (Zero-Cost Operation):** As a student team, we want the entire pipeline (Mattermost, Switch, OpenCode) to operate locally at zero cost, so that no paid cloud subscriptions or proprietary domains are needed.

---

## 6. Functional Requirements (FR)

Every functional requirement defines a concrete capability and its measurable acceptance criteria.

### 6.1 Team Chat & Collaboration (Mattermost)

#### FR-01: Multi-Developer Communication Channel
* **Description:** Two authenticated developers (Sunayana and Vaibhav) must be able to communicate concurrently in the same Mattermost channel.
* **Acceptance Criteria:**
  1. Both user accounts can log into the local Mattermost workspace.
  2. Messages sent by User A appear in User B's channel view in real time (< 2 seconds).
  3. Channel message history persists across browser reloads.

#### FR-02: AI Agent Invocation via Mention
* **Description:** Developers must be able to invoke the AI coding agent directly within a Mattermost channel using `@opencode` or a designated mention trigger.
* **Acceptance Criteria:**
  1. A post containing `@opencode <prompt>` is recognized by the system.
  2. The system acknowledges the request with an immediate reaction or status indicator within 3 seconds.

#### FR-03: Thread-Isolated Task Sessions
* **Description:** All conversation, status messages, execution logs, and approvals for a given task must remain strictly confined to the triggering Mattermost thread (`root_id`).
* **Acceptance Criteria:**
  1. Subsequent agent replies are posted as thread replies, not root channel posts.
  2. Tasks running in Thread A do not leak context or state into concurrent Thread B.

#### FR-04: Multi-User Thread Participation
* **Description:** Multiple developers must be able to post messages into an active agent thread to add reproduction steps, modify constraints, or steer execution.
* **Acceptance Criteria:**
  1. If User B posts feedback into User A's active agent thread, the agent ingests the feedback and updates its planned action accordingly.

---

### 6.2 Message Orchestration & Session Routing (Switch)

#### FR-05: Switch Message Ingestion & Event Routing
* **Description:** The Switch bridge must listen to incoming Mattermost messages, identify agent-bound tasks, and route them to OpenCode.
* **Acceptance Criteria:**
  1. Switch receives channel webhook / WebSocket events from Mattermost.
  2. Switch extracts the sender identity, thread ID (`root_id`), message text, and channel ID.
  3. Switch routes the payload to the appropriate OpenCode session.

#### FR-06: Thread-to-Agent Session State Mapping
* **Description:** Switch must maintain a mapping between Mattermost thread IDs and OpenCode session IDs to preserve conversation history throughout the task lifecycle.
* **Acceptance Criteria:**
  1. Repeating requests within the same thread reuse the existing OpenCode session memory.
  2. Starting a new thread initializes a fresh session without contaminated state from previous tasks.

#### FR-07: Human-in-the-Loop Interception
* **Description:** Switch must intercept consequential agent actions (file edits, shell execution, git commits, git pushes) and hold execution until explicit human authorization is received.
* **Acceptance Criteria:**
  1. Agent execution pauses when an approval gate is reached.
  2. An approval prompt is posted into the Mattermost thread displaying the proposed action.
  3. Execution only resumes upon receiving a valid human approval response.

#### FR-08: Progress & Status Reporting
* **Description:** Switch must stream or post incremental status updates back to the Mattermost thread during long-running operations.
* **Acceptance Criteria:**
  1. Status updates (e.g., "Inspecting files...", "Running test suite...", "Generating diff...") appear in the thread during execution.
  2. No operations run silently without developer feedback for more than 15 seconds.

---

### 6.3 AI Coding Agent Capabilities (OpenCode)

#### FR-09: Workspace & Codebase Inspection
* **Description:** OpenCode must be able to inspect permitted project files, directory structures, and git history in an approved local workspace.
* **Acceptance Criteria:**
  1. Given a file path or search pattern within the target repository, OpenCode reads and analyzes the file content.
  2. OpenCode cannot read files outside the approved workspace root.

#### FR-10: Structured Plan Generation
* **Description:** OpenCode must formulate and output a structured, step-by-step implementation plan before modifying any code.
* **Acceptance Criteria:**
  1. The generated plan lists target files, root cause analysis, proposed changes, and verification steps.
  2. The plan is posted to the Mattermost thread for human review prior to file modification.

#### FR-11: Targeted Code Modification
* **Description:** OpenCode must be capable of applying targeted, syntactically correct code edits to project files in an isolated feature branch.
* **Acceptance Criteria:**
  1. File modifications accurately implement the approved plan.
  2. Edits do not truncate unrelated code or corrupt file formatting.

#### FR-12: Test Suite Execution & Output Capture
* **Description:** OpenCode must be capable of executing local test suites (e.g., `npm test`, `pytest`) inside a controlled environment and capturing stdout/stderr.
* **Acceptance Criteria:**
  1. The test runner is invoked with appropriate arguments.
  2. Test pass/fail counts and error stack traces are captured and reported to the chat thread.

#### FR-13: Unified Git Diff Generation
* **Description:** OpenCode must generate a standard unified git diff of all modified files for developer inspection.
* **Acceptance Criteria:**
  1. Diff shows exact line additions and deletions (`git diff`).
  2. The diff is formatted inside a Markdown code block in the Mattermost thread.

---

### 6.4 Human Approval Mechanics

#### FR-14: Command-Based Approval & Rejection
* **Description:** The system must accept standard keyword commands (`!approve`, `!reject`, `!modify <feedback>`) from authorized team members in the thread.
* **Acceptance Criteria:**
  1. Submitting `!approve` triggers the next execution phase (e.g., apply edits, push branch).
  2. Submitting `!reject` halts execution, discards uncommitted changes, and marks the task as aborted.
  3. Submitting `!modify <text>` instructs the agent to regenerate its plan or code incorporating the new feedback.

#### FR-15: Interactive UI Button Approval (Optional Enhancement)
* **Description:** Where supported by Mattermost interactive dialogs/attachments, clickable buttons (`[Approve]`, `[Reject]`) must be displayed alongside the diff.
* **Acceptance Criteria:**
  1. Clicking `[Approve]` sends an action integration payload to Switch equivalent to `!approve`.
  2. Text command fallbacks remain fully functional if interactive buttons are unavailable.

---

### 6.5 Source Control & GitHub Traceability

#### FR-16: Feature Branch Isolation
* **Description:** OpenCode must execute all modifications on dedicated git feature branches (e.g., `feature/fix-place-order-button`) and never commit directly to `main`.
* **Acceptance Criteria:**
  1. OpenCode verifies or creates a dedicated feature branch before committing.
  2. Any attempted direct push to `main` is blocked by system policy.

#### FR-17: Traceable Git Commits
* **Description:** Commits made by or on behalf of the agent must include structured, descriptive messages referencing the task and human approver.
* **Acceptance Criteria:**
  1. Commit message follows conventional format (e.g., `fix(checkout): validate order payload before submission`).
  2. Commit author / co-author metadata identifies the collaborative origin.

#### FR-18: GitHub Pull Request Generation & Notification
* **Description:** Upon final human approval, the system or developer must push the feature branch to GitHub, open a Pull Request, and post the clickable link to Mattermost.
* **Acceptance Criteria:**
  1. Feature branch exists on GitHub remote repository (`vaibhavbutul-work/Switch_Rog`).
  2. Pull Request is opened against `main` containing problem summary, test results, and reviewer checklist.
  3. Pull Request URL is posted into the originating Mattermost thread.

#### FR-19: Peer Review & Merge Gate
* **Description:** Merging of the Pull Request must require human review and approval on GitHub by the second developer (e.g., Vaibhav reviewing Sunayana's branch).
* **Acceptance Criteria:**
  1. Pull Request cannot be merged without at least one approved human review on GitHub.
  2. Completed merge is announced back in the Mattermost thread for audit closure.

---

## 7. Non-Functional Requirements (NFR)

### 7.1 Performance & Responsiveness
* **NFR-01 (Chat Latency):** Mattermost message delivery between users on the local setup must occur within **1 second**.
* **NFR-02 (Acknowledgment Time):** Switch must acknowledge an agent mention with an emoji or status message within **3 seconds**.
* **NFR-03 (Plan Generation Latency):** For typical project repositories (< 50 source files), OpenCode must generate an initial implementation plan within **30 seconds**.
* **NFR-04 (Command Execution Timeout):** Terminal and test commands executed by OpenCode must enforce a hard timeout of **60 seconds** to prevent infinite loops from freezing the system.

### 7.2 Reliability & Fault Tolerance
* **NFR-05 (Crash Resilience):** If OpenCode or a test execution fails, Switch must capture stderr, report the failure gracefully in the thread, and return to an idle state without crashing the bridge.
* **NFR-06 (Safe Rejection Rollback):** When a user submits `!reject`, the system must execute a safe targeted rollback within **5 seconds** without discarding unrelated developer changes. If an isolated ephemeral task branch or git worktree is used, the branch/worktree is cleanly discarded; if operating in-place, only the exact files recorded in the session manifest are reverted (`git checkout HEAD -- <target-files>`), ensuring any unstaged developer work outside the task remains completely preserved.
* **NFR-07 (Network Disconnection Recovery):** If a developer's browser temporarily disconnects from Mattermost, upon reconnection all thread history and pending approvals must remain intact.

### 7.3 Usability & Clarity
* **NFR-08 (Markdown Formatting):** All agent plans, diffs, test summaries, and error logs must be rendered using clean GitHub-flavored Markdown with code syntax highlighting.
* **NFR-09 (Zero-Jargon User Prompts):** Approval prompts must explicitly instruct developers on available actions (e.g., `Reply !approve to apply changes, !modify <notes> to revise, or !reject to cancel`).

### 7.4 Feasibility & Low-Resource Footprint
* **NFR-10 (Zero Cloud Dependency):** Core orchestration (Mattermost, Switch, OpenCode) must run entirely on a standard developer workstation (Windows 11 / WSL2, Docker Desktop) without requiring paid cloud hosting.
* **NFR-11 (Low Memory Footprint):** The combined running infrastructure must operate smoothly within 8 GB to 16 GB of system RAM typical of student development laptops.

---

## 8. Security Requirements (SEC)

* **SEC-01 (No Secrets in Repository):** No API keys, personal access tokens (PATs), Mattermost passwords, or private SSH keys may ever be committed to the git repository. All secrets must reside in uncommitted `.env` files matching `.gitignore`.
* **SEC-02 (Restricted Workspace Directory):** OpenCode must be strictly constrained to inspect and modify files inside the designated project root directory (`C:\Users\sunay\Switch_Rog` or container mount). Access to host root filesystems, user home directories, or system settings is prohibited.
* **SEC-03 (Dangerous Command Blacklist):** Destructive terminal commands (including `rm -rf /`, `mkfs`, `sudo`, `chmod -R 777`, `curl ... | bash`, `npm publish`, `git push --force`) must be automatically intercepted and blocked by the system.
* **SEC-04 (Secret Masking in Logs):** Any environment variables or tokens encountered in command execution stdout/stderr must be masked (e.g., `ghp_****`) before posting to Mattermost threads.
* **SEC-05 (Explicit Approval for External Side Effects):** Git pushes to remote repositories and network publication actions must require explicit human confirmation.
* **SEC-06 (No Direct Push to Main):** Direct pushes to `main` must be prohibited by branch protection rules on GitHub and by pre-push validation in the workflow.

---

## 9. System Constraints (CON)

* **CON-01 (Zero-Cost Budget):** The project operates under strict zero-cost hackathon constraints. No paid SaaS subscriptions, cloud VMs (AWS/GCP/Azure), paid domains, or paid LLM tokens may be required for baseline operation.
* **CON-02 (Operating Environment):** Host system is Windows 11 with WSL2, Docker Desktop, and PowerShell. All scripts and paths must handle Windows/Linux cross-compatibility.
* **CON-03 (Single Shared Repository):** Code collaboration takes place on GitHub at `https://github.com/vaibhavbutul-work/Switch_Rog` using branches (`feature/project-planning`, `feature/architecture`) and Pull Requests.
* **CON-04 (Role Segregation):** Documentation, workflow, and validation are assigned to Sunayana; technical bridge plumbing, container configuration, and runtime integration are assigned to Vaibhav. Neither developer may overwrite the other's assigned files without prior coordination.

---

## 10. Project Scope & Limitations

### 10.1 In-Scope (Hackathon Deliverable)
1. Shared Mattermost team setup with dedicated channels (`#project-general`, `#bug-reports`, `#ai-agent-tasks`, `#code-review`).
2. Two authenticated developer accounts (Sunayana and Vaibhav) participating in the same workspace.
3. Switch messaging bridge connecting Mattermost channel threads to OpenCode.
4. OpenCode AI coding agent executing file inspection, structured planning, file edits, and test verification.
5. End-to-end bug fix scenario: Online shopping application "Place Order button" failure triage, fix, and verification.
6. Human-in-the-loop approval gate with `!approve`, `!modify`, and `!reject` mechanics.
7. Feature branch git workflow and GitHub Pull Request review handoff.
8. Comprehensive test scenarios, collaboration test plan, user guide, and demo script.

### 10.2 Out-of-Scope (Future Enhancements)
1. Automated self-merging of Pull Requests into `main` without human GitHub code review.
2. Complex multi-tenant enterprise RBAC (e.g., SAML/SSO integration, LDAP).
3. Voice-to-text chat invocation or video conference integration.
4. Real-time multi-agent consensus debates (running 5+ competing LLMs in parallel).
5. Automated deployment to live multi-region production cloud clusters.

---

## 11. Traceability & Measurable Acceptance Criteria Summary

| Requirement ID | Category | Summary Description | Verification Method | Acceptance Pass Criterion |
| :--- | :--- | :--- | :--- | :--- |
| **FR-01** | Chat | Multi-developer communication | Interactive Test | Two users exchange messages in real time (< 2s). |
| **FR-02** | Chat | Agent invocation via `@opencode` | Functional Test | Mention recognized; acknowledgment within 3s. |
| **FR-03** | Chat | Thread isolation | Functional Test | Task conversation confined to `root_id`; zero cross-thread bleed. |
| **FR-04** | Chat | Multi-user thread input | Functional Test | Second user's comments incorporated into active plan. |
| **FR-05** | Switch | Message routing to OpenCode | Integration Test | Mattermost webhook payload successfully parsed by Switch. |
| **FR-06** | Switch | Session mapping | Integration Test | Thread ID maps to distinct OpenCode session memory. |
| **FR-07** | Switch | Human approval interception | Integration Test | Consequential actions hold until human confirmation. |
| **FR-08** | Switch | Progress updates | Functional Test | Status logs posted to thread during processing. |
| **FR-09** | OpenCode | Codebase inspection | Functional Test | Agent reads files within approved workspace path only. |
| **FR-10** | OpenCode | Structured plan generation | Functional Test | Plan output contains root cause, file targets, and steps. |
| **FR-11** | OpenCode | Targeted code modification | Functional Test | Edits solve target issue without corrupting syntax. |
| **FR-12** | OpenCode | Test runner execution | Functional Test | Unit tests executed; pass/fail output posted to chat. |
| **FR-13** | OpenCode | Unified git diff output | Functional Test | Clean Markdown git diff displayed in thread. |
| **FR-14** | Approval | Keyword approval / rejection | Functional Test | `!approve` proceeds; `!reject` reverts workspace. |
| **FR-15** | Approval | Interactive buttons | UI Test | Interactive button click triggers approval handler. |
| **FR-16** | GitHub | Feature branch isolation | Git Audit | Work committed on `feature/...`; `main` untouched. |
| **FR-17** | GitHub | Traceable commit messages | Git Audit | Commit history reflects task ID and approver identity. |
| **FR-18** | GitHub | Pull Request creation | GitHub Audit | Open PR exists with test evidence and chat link. |
| **FR-19** | GitHub | Peer review merge gate | GitHub Audit | PR merged only after human peer approval on GitHub. |

---

## 12. Expected Project Outcome
The final outcome of Switch_Rog is a fully documented, locally verified, zero-cost collaborative AI development environment. By connecting Mattermost, Switch, OpenCode, and GitHub, the project proves that AI coding agents can function effectively as transparent, supervised virtual teammates within a peer-reviewed engineering workflow. The solution eliminates single-user AI silos, prevents unvetted code from reaching production, and provides a repeatable blueprint for hackathons and software engineering teams.
