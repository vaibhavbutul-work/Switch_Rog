# Requirements Specification — Switch_Rog

## 1. Project Overview & Problem Statement

### 1.1 Project Overview
**Switch_Rog** is a collaborative AI-assisted development environment built for small engineering teams. It connects team communication in **Mattermost** with an autonomous AI coding agent powered by **OpenCode**, coordinated via the **Switch** messaging bridge, and integrated with **GitHub** for source code management.

Instead of isolating AI coding assistants inside an individual developer's personal code editor, Switch_Rog brings the AI agent directly into team chat channels. Multiple developers can observe, direct, discuss, and supervise the AI coding agent together in real time.

### 1.2 Problem Statement
Current AI coding tools (such as editor plugins and command-line assistants) are built for single-user, isolated environments:
1. **Siloed Context:** When a developer works with an AI tool in their local editor, other team members cannot see what prompts were used, what decisions were made, or what code changes are taking place until a pull request is submitted.
2. **Duplicate Work and Code Conflicts:** Two developers facing related problems may unknowingly prompt their local AI assistants to solve overlapping issues in incompatible ways.
3. **Lack of Peer Review during Generation:** Traditional AI workflows only allow human review *after* code is written and committed. There is no shared intermediate stage where a peer or lead developer can review the agent's proposed plan or approve dangerous terminal commands before execution.
4. **Knowledge Sharing Deficit:** Junior developers miss out on observing how senior engineers prompt, guide, and constrain AI agents to produce high-quality code.

### 1.3 Proposed Solution
Switch_Rog solves these problems by moving AI-assisted software development into a shared team channel:
* Developers interact with **OpenCode** by mentioning it in Mattermost threads.
* The **Switch** bridge captures messages, manages session context per thread, routes tasks to the OpenCode agent, and posts structured progress updates back to the chat.
* Changes are proposed publicly within the thread, allowing any team member to comment, steer, or halt the agent.
* Critical actions (terminal execution, code edits, git commits, PR creation) require explicit **human approval** via interactive chat buttons or confirmation keywords before taking effect.

---

## 2. Target Users & Personas

Switch_Rog is designed for collaborative software teams that want transparency and safety when using AI coding agents.

### User Persona 1: Sunayana — Full-Stack Developer & Reviewer
* **Background:** Computer Science undergraduate working on a team project.
* **Goal:** Wants to delegate repetitive tasks (such as writing boilerplate tests, fixing lint errors, or creating API endpoints) to an AI agent while keeping her teammate in the loop.
* **Pain Point:** Frustrated when local AI tools make silent changes or when she cannot easily share the AI conversation context with her partner.
* **Usage:** Initiates tasks in Mattermost threads, reviews the agent's proposed plan, and approves code diffs.

### User Persona 2: Vaibhav — Tech Lead & Code Reviewer
* **Background:** Student developer responsible for system architecture and repository stability.
* **Goal:** Needs oversight on all automated code modifications to prevent hallucinated packages, broken builds, or risky shell commands.
* **Pain Point:** Dislikes black-box code generators that produce messy commits or break existing test suites without warning.
* **Usage:** Observes agent progress in the Mattermost thread, inspects unified diffs, approves or rejects PR creation, and ensures security guardrails are respected.

### User Persona 3: Student Hackathon Teams / Pair Programmers
* **Background:** 2–4 developers building applications under tight deadlines.
* **Goal:** Need rapid scaffolding and bug resolution without stepping on each other's toes.
* **Pain Point:** Lack of time to manually write boilerplate code and lack of visibility into what each teammate is editing.
* **Usage:** Shared channel where anyone can inspect agent actions and jump in to assist.

---

## 3. Developer and AI Agent Roles

To ensure safe collaboration, Switch_Rog defines clear roles and boundaries for human developers and the AI agent:

| Role | Entity | Key Responsibilities |
| :--- | :--- | :--- |
| **Task Initiator** | Developer (Human) | Creates the task in Mattermost, describes requirements, provides context or error logs, and sets constraints. |
| **Peer Reviewer / Approver** | Developer (Human) | Reviews the agent's plan, inspects code diffs, approves or rejects execution requests, and merges GitHub Pull Requests. |
| **Task Coordinator** | Switch (Bridge) | Ingests Mattermost messages, tracks thread session state, enforces human-in-the-loop policies, and routes data between chat and OpenCode. |
| **Planner & Implementer** | OpenCode (AI Agent) | Analyzes the codebase, explains the solution, generates execution plans, edits code files, runs tests in a sandbox, and reports results. |
| **Code Repository Host** | GitHub (System) | Stores version-controlled code, isolates changes in feature branches, and manages Pull Requests. |

---

## 4. Functional Requirements (FR)

The functional requirements are categorized by system component.

### 4.1 Chat Interface & Invocation (Mattermost)
* **FR-1.1 (Agent Invocation):** A developer must be able to invoke the AI agent in a designated channel by mentioning `@opencode` or typing a slash command (e.g., `/opencode <prompt>`).
* **FR-1.2 (Thread Isolation):** All interactions for a specific task must remain confined to a single Mattermost thread (`root_id`), preventing message clutter in the main channel.
* **FR-1.3 (Multi-User Input):** Multiple developers in the same channel must be able to post messages into the active thread to provide additional guidance or corrective instructions to the agent.
* **FR-1.4 (Interactive UI Elements):** The system must present interactive buttons (e.g., `[Approve]`, `[Reject]`, `[Modify]`) or clear keyword prompts (`!approve`, `!reject`) for required human approvals.

### 4.2 Messaging & Session Coordination (Switch Bridge)
* **FR-2.1 (Event Ingestion):** Switch must listen to Mattermost channel events via Mattermost REST API v4 / WebSocket and identify messages directed to the agent.
* **FR-2.2 (Session Mapping):** Switch must map each Mattermost thread ID (`root_id`) to a distinct OpenCode session so conversations maintain context without cross-talk.
* **FR-2.3 (Human-in-the-Loop Interception):** Switch must intercept agent actions that require approval (such as shell commands or file writes) and pause agent execution until an authorized human response is received.
* **FR-2.4 (Status Streaming):** Switch must post incremental progress updates (e.g., "Reading files...", "Running tests...", "Generating diff...") back to the Mattermost thread.

### 4.3 AI Coding Agent Capabilities (OpenCode)
* **FR-3.1 (Codebase Analysis):** OpenCode must be capable of inspecting workspace files, directory structures, and git history to understand project context.
* **FR-3.2 (Plan Generation):** Before modifying any files, OpenCode must generate a structured step-by-step implementation plan and post it to the thread for review.
* **FR-3.3 (Code Editing):** OpenCode must be capable of creating new files and modifying existing code with precise edits.
* **FR-3.4 (Test Execution):** OpenCode must be capable of executing project test suites (e.g., `npm test`, `pytest`) inside its sandbox environment and reporting test passes or failures back to the chat.
* **FR-3.5 (Diff Generation):** OpenCode must produce a readable unified git diff of all proposed changes before committing.

### 4.4 GitHub Collaboration & Source Control
* **FR-4.1 (Branch Isolation):** OpenCode must never commit directly to the `main` or default branch. It must create and work within dedicated feature branches (e.g., `feat/opencode-<task-name>`).
* **FR-4.2 (Commit & Push):** Upon receiving human approval, OpenCode must commit the approved changes with a descriptive commit message and push the branch to GitHub.
* **FR-4.3 (Pull Request Creation):** The system must generate a GitHub Pull Request with a summary of changes, linked issue/thread references, and test results.
* **FR-4.4 (PR Link Notification):** The system must post the clickable GitHub Pull Request URL into the Mattermost thread so developers can perform final code reviews and merge.

---

## 5. Non-Functional Requirements (NFR)

### 5.1 Performance & Responsiveness
* **NFR-1.1 (Acknowledgment Latency):** The system must acknowledge a developer's request in Mattermost with an immediate reaction (e.g., 👀 emoji) or a status message within **3 seconds**.
* **NFR-1.2 (Plan Delivery):** For typical code tasks (under 10 files involved), the agent must formulate and post its initial plan within **30 seconds**.
* **NFR-1.3 (Message Throughput):** The Switch bridge must handle concurrent messages across at least 3 active threads without dropped events or message duplication.

### 5.2 Reliability & Fault Tolerance
* **NFR-2.1 (Graceful Failure Handling):** If OpenCode fails to execute a command or encounters a syntax error during testing, it must report the exact error output in the thread rather than crashing or terminating silently.
* **NFR-2.2 (Timeout Safeguards):** Agent terminal commands must enforce an execution timeout (e.g., 60 seconds) to prevent infinite loops from hanging the system.
* **NFR-2.3 (State Preservation):** If the Switch bridge restarts, it must retain session identifiers so in-flight tasks can be gracefully resumed or closed.

### 5.3 Security & Safety
* **NFR-3.1 (Sandboxed Execution):** OpenCode tool execution must run inside an isolated container or restricted workspace with no access to host credentials, private SSH keys, or parent host filesystems.
* **NFR-3.2 (Command Whitelist / Blacklist):** Destructive commands (e.g., `rm -rf /`, `curl ... | bash`, `git push --force`) must be strictly blocked or require explicit double confirmation.
* **NFR-3.3 (Secret Masking):** The Switch bridge must scrub environment variables containing API keys or tokens before printing terminal logs to Mattermost.

### 5.4 Usability & Simplicity
* **NFR-4.1 (Clean Output Formatting):** All agent responses in Mattermost must use GitHub-flavored Markdown, including syntax-highlighted code blocks, tables, and collapsible diffs for readability.
* **NFR-4.2 (Simple Developer UX):** Developers must not need to memorize complex syntax; standard English instructions and simple commands (`!approve`, `!reject`, `!cancel`) must be sufficient.

### 5.5 Feasibility for a Two-Person Student Team
* **NFR-5.1 (Off-the-Shelf Components):** The architecture must utilize standard Docker containers, existing official APIs (Mattermost REST API v4, GitHub REST API / `gh` CLI), and open-source Switch connectors.
* **NFR-5.2 (Minimal Infrastructure):** The entire stack must be deployable on a single developer workstation or laptop using Docker Compose.

---

## 6. Project Scope & Limitations

### 6.1 In-Scope (Hackathon MVP)
1. Single Mattermost team and dedicated development channel (e.g., `#dev-ai`).
2. Thread-based interaction with `@opencode`.
3. Switch message routing and session management.
4. OpenCode plan generation, file reading, file editing, and test execution.
5. Interactive human approval for code diffs and branch pushes.
6. Automated creation of feature branches and GitHub Pull Requests.
7. Support for standard web/software stacks (e.g., Node.js / Python projects).

### 6.2 Out-of-Scope (Future Enhancements)
1. Multi-tenant enterprise permission hierarchies (e.g., complex role-based access control per repository).
2. Voice-to-text input or voice channel integration.
3. Automated self-merging of Pull Requests into `main` without human GitHub review.
4. Real-time multi-agent debate (running 5+ competing LLMs concurrently).
5. Automatic deployment to live production environments (CI/CD pipeline stops at GitHub PR creation).
