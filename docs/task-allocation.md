# Team Task Allocation, Hackathon Roadmap & Risk Plan — Switch_Rog

## 1. Team Structure & Ownership Matrix

Switch_Rog is engineered by a focused two-person student team. To maximize velocity and eliminate overlapping effort during the hackathon, responsibilities are clearly divided between system architecture and workflow integration.

```
+-----------------------------------------------------------------------------------+
|                                 Switch_Rog Team                                   |
+-----------------------------------------+-----------------------------------------+
| Sunayana Kamat                          | Vaibhav Kumar                           |
| Integration and Workflow Lead           | Technical Lead                          |
+-----------------------------------------+-----------------------------------------+
| - Product Requirements & Scope          | - System Architecture & Bridge Plumbing |
| - Mattermost Setup & Channel Config     | - Switch Connector & OpenCode Runner    |
| - Agent Prompt Engineering & Templates  | - Docker Compose Multi-Container Setup  |
| - Approval Workflow & Interaction UX    | - GitHub CLI / Webhook Automation       |
| - Comprehensive Quality & Test Execution| - Process Sandboxing & Command Security |
+-----------------------------------------+-----------------------------------------+
```

### Detailed Ownership Matrix

| Functional Area | Primary Owner | Secondary Owner | Deliverables |
| :--- | :--- | :--- | :--- |
| **Requirements & Planning** | Sunayana Kamat | Vaibhav Kumar | Requirements doc, user personas, NFRs, scope boundaries. |
| **Chat Platform Setup** | Sunayana Kamat | Vaibhav Kumar | Mattermost team, `#dev-ai` channel, bot account, webhook URLs. |
| **Switch & OpenCode Bridge**| Vaibhav Kumar | Sunayana Kamat | Switch daemon, OpenCode CLI integration, message routing. |
| **Approval & Interaction Flow**| Sunayana Kamat | Vaibhav Kumar | Interactive buttons (`Approve`/`Reject`), keyword parser, diff display. |
| **Container & Environment** | Vaibhav Kumar | Sunayana Kamat | `docker-compose.yml`, environment configuration (`.env`), volume mounts. |
| **GitHub Automation** | Vaibhav Kumar | Sunayana Kamat | Automatic branch checkout, git commits, PR generation via `gh` CLI. |
| **Testing & Quality Assurance**| Sunayana Kamat | Vaibhav Kumar | 10 integration test executions, bug logging, validation matrix. |
| **Demo & Presentation** | Sunayana Kamat | Vaibhav Kumar | 3-minute hackathon demo walkthrough script and presentation slide deck. |

---

## 2. Four-Stage Hackathon Roadmap

To deliver a working, robust prototype within a standard 4-day hackathon timeline, the project follows four structured stages.

```
[Stage 1: Planning & Setup] (Day 1)
   ├── Requirements & Architecture definition
   ├── Workspace initialization & Git repository setup
   └── API key provisioning (LLM, Mattermost Bot, GitHub PAT)
           │
           ▼
[Stage 2: Core Infrastructure] (Day 1 - Day 2)
   ├── Local Mattermost container deployment
   ├── Switch bridge configuration & thread listener
   └── OpenCode CLI execution inside container/sandbox
           │
           ▼
[Stage 3: Workflow & Guardrail Integration] (Day 2 - Day 3)
   ├── Thread session mapping (root_id -> agent session)
   ├── Structured plan output & unified diff formatting
   ├── Human-in-the-loop interactive approvals
   └── GitHub feature branch & Pull Request automation
           │
           ▼
[Stage 4: Testing, Hardening & Demo] (Day 3 - Day 4)
   ├── Execution of 10-point test matrix
   ├── Error handling & timeout safeguards
   └── Live demo recording & submission materials
```

### Stage-by-Stage Milestones

#### Stage 1: Team Setup and Project Planning (Current Stage)
* Define problem statement, target personas, functional requirements, and non-functional requirements.
* Establish team roles, communication channels, and git collaboration guidelines.
* Verify tool compatibility and API limits (Mattermost v4 API, Switch broker, OpenCode agent, GitHub REST API).
* **Exit Milestone:** Completed `requirements.md`, `workflow.md`, and `task-allocation.md` approved by both team members.

#### Stage 2: Infrastructure & Integration Plumbing
* Deploy local Mattermost instance using official Docker image.
* Configure Mattermost Bot Account with Personal Access Token and bot permissions in `#dev-ai`.
* Configure Switch gateway to listen to incoming mentions and thread replies.
* Connect Switch to OpenCode CLI runner in an isolated workspace.
* **Exit Milestone:** Posting `@opencode echo "Hello World"` in Mattermost triggers an agent execution and replies in the thread.

#### Stage 3: Workflow & Guardrails Implementation
* Implement thread isolation: Map Mattermost `root_id` to individual OpenCode sessions.
* Implement structured 2-step execution: Planning Phase followed by Execution Phase.
* Build the Human Approval Gate:
  * Present interactive approval buttons or `!approve`/`!reject` command parser.
  * Hold code execution and remote git push until human approval is registered.
* Connect GitHub CLI / REST API for automated branch creation (`feat/...`) and Pull Request generation.
* **Exit Milestone:** End-to-end task execution: Prompting a bug fix in chat results in an approved GitHub Pull Request.

#### Stage 4: Testing, Verification & Final Demo
* Execute all 10 test cases from `docs/workflow.md` (invocation, isolation, approval, rejection, guardrails, PR creation).
* Measure performance against NFRs (acknowledgment latency < 3s, timeout handling at 60s).
* Prepare demo repository with a realistic sample application (e.g., simple Node.js Express API with unit tests).
* Record a 3-minute video showing two developers collaboratively guiding the agent to resolve an issue.
* **Exit Milestone:** Clean git repository, passed test log, working demo video, and submitted project.

---

## 3. Work Breakdown Structure (WBS) & Task Matrix

The following task matrix details the specific tasks, assigned owners, dependencies, and estimated effort in hours.

| Task ID | Task Description | Assignee | Dependencies | Estimated Effort |
| :--- | :--- | :--- | :--- | :--- |
| **WBS-1.1** | Author Requirements & Personas (`requirements.md`) | Sunayana | None | 2.5 hrs |
| **WBS-1.2** | Author User Workflow & Test Cases (`workflow.md`) | Sunayana | WBS-1.1 | 2.5 hrs |
| **WBS-1.3** | Author Task Allocation & Risk Plan (`task-allocation.md`) | Sunayana | WBS-1.1 | 1.5 hrs |
| **WBS-2.1** | Set up `docker-compose.yml` for Mattermost & Switch | Vaibhav | None | 2.0 hrs |
| **WBS-2.2** | Configure Mattermost team, `#dev-ai` channel, and bot tokens | Sunayana | WBS-2.1 | 1.0 hr |
| **WBS-2.3** | Configure Switch Mattermost listener and WebSocket client | Vaibhav | WBS-2.2 | 3.0 hrs |
| **WBS-2.4** | Configure OpenCode runner in local workspace sandbox | Vaibhav | WBS-2.3 | 2.5 hrs |
| **WBS-3.1** | Implement thread-to-session routing in Switch | Vaibhav | WBS-2.4 | 3.0 hrs |
| **WBS-3.2** | Create agent prompt templates for structured planning | Sunayana | WBS-3.1 | 2.0 hrs |
| **WBS-3.3** | Implement Human Approval Gate (`!approve`, `!reject`, buttons) | Sunayana | WBS-3.1 | 3.0 hrs |
| **WBS-3.4** | Implement unified diff formatter for Mattermost Markdown | Sunayana | WBS-3.3 | 1.5 hrs |
| **WBS-3.5** | Implement Git feature branch checkout and PR creation | Vaibhav | WBS-3.3 | 2.5 hrs |
| **WBS-3.6** | Implement dangerous command blacklist filter | Vaibhav | WBS-2.4 | 1.5 hrs |
| **WBS-4.1** | Create sample demo application with unit tests | Sunayana | None | 2.0 hrs |
| **WBS-4.2** | Execute 10 integration test cases and document results | Sunayana | WBS-3.5, WBS-4.1 | 3.0 hrs |
| **WBS-4.3** | Optimize container resource usage and latency | Vaibhav | WBS-4.2 | 2.0 hrs |
| **WBS-4.4** | Record 3-minute demo video and prepare slide deck | Sunayana & Vaibhav | WBS-4.2 | 3.0 hrs |

*Total Estimated Effort per Student:* ~18 hours over 3–4 days (completely realistic and achievable for two college students).

---

## 4. Project Risks, Limitations & Mitigation Strategies

Hackathon projects face technical uncertainties and tight deadlines. The table below identifies key risks and concrete, low-overhead mitigations tailored for a student team.

| Risk ID | Risk Description | Severity | Likelihood | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **R-01** | **LLM API Rate Limits & Cost Overruns:** Exceeding free-tier API quotas during repeated testing loops. | High | Medium | • Use token-efficient prompts (read only relevant files).<br>• Cache repository structure in session.<br>• Use local small model (e.g., Ollama/DeepSeek) for dev testing; switch to cloud LLM for final demo. |
| **R-02** | **Agent Hallucinations & File Corruption:** Agent makes incorrect edits or deletes working code. | High | Medium | • Strictly require feature branch isolation (`feat/opencode-...`).<br>• Enforce pre-commit `git diff` inspection in Mattermost.<br>• Enable `!reject` command that performs instant `git checkout .`. |
| **R-03** | **Student Laptop Hardware Constraints:** Running Mattermost, Switch, OpenCode, and local app overwhelms laptop RAM. | Medium | High | • Use lightweight Mattermost Team Edition container.<br>• Run OpenCode natively on host CLI if nested Docker container consumes too much RAM.<br>• Limit Docker container memory allocations in Compose file. |
| **R-04** | **Mattermost WebSocket Disconnects:** Dropped network connections between Switch bridge and chat server. | Medium | Medium | • Implement automatic reconnection backoff in Switch adapter.<br>• Provide fallback polling via Mattermost REST API if WebSocket stalls. |
| **R-05** | **GitHub Token & Permission Issues:** PR creation fails due to incorrect PAT scopes. | Medium | Low | • Verify GitHub Personal Access Token permissions (`repo`, `workflow`) early in Stage 1.<br>• Test `gh pr create` via CLI before wiring into automated flow. |
| **R-06** | **Scope Creep (Running out of Time):** Spending too much time on complex UI features instead of the core workflow. | High | High | • Prioritize the text-based command fallback (`!approve`/`!reject`) first.<br>• Add interactive buttons only after the core flow works reliably.<br>• Keep demo focused on one clear, end-to-end bug fix scenario. |

---

## 5. Definition of Done (DoD) & Demo Plan

### 5.1 Definition of Done for Hackathon MVP
The project is considered complete and submission-ready when:
1. **End-to-End Operation:** A developer can trigger `@opencode` in Mattermost, receive a plan, approve it, watch tests pass, review the diff, and have a GitHub PR created without touching the terminal manually.
2. **Multi-Developer Participation:** At least two distinct Mattermost user accounts can post into the same thread and participate in the task lifecycle.
3. **Safety Verification:** The agent cannot push directly to `main`, and dangerous commands are successfully intercepted.
4. **Documentation:** All architecture, workflow, and testing documents are committed to the repository.
5. **Reproducibility:** A new developer can clone the repository, run `docker-compose up`, supply their API keys in `.env`, and replicate the environment.

### 5.2 Hackathon 3-Minute Demo Walkthrough Script
For the final project submission and judge evaluation, follow this live demonstration script:

* **0:00 – 0:30 (The Problem):**  
  Sunayana briefly explains the problem: "AI coding agents today are lonely tools inside individual IDEs. When our team works together, we can't see what the agent is doing, leading to duplicate work and untested code."
* **0:30 – 1:15 (The Initiation & Multi-Dev Collaboration):**  
  Sunayana opens Mattermost `#dev-ai` and tags `@opencode` to fix an authentication bug. OpenCode replies in the thread with an implementation plan. Vaibhav chimes in directly in the thread: "Make sure you also add a test case for missing token header." OpenCode adjusts its plan immediately.
* **1:15 – 2:00 (Human-in-the-Loop Approval):**  
  Sunayana clicks `[Approve Plan]`. OpenCode creates a feature branch, edits the files, and executes the unit test runner in its sandbox. OpenCode posts the passing test output and a clean unified git diff right in the chat.
* **2:00 – 2:30 (GitHub Integration & PR Creation):**  
  Vaibhav reviews the diff in Mattermost and clicks `[Approve & Push]`. Switch instructs OpenCode to push the branch and open a GitHub Pull Request. Switch posts the live GitHub PR link in the thread.
* **2:30 – 3:00 (Review on GitHub & Wrap-Up):**  
  Vaibhav clicks the PR link, shows the committed code and test summary on GitHub, and explains how Switch_Rog enables safe, transparent, and collaborative AI pair programming for student teams.
