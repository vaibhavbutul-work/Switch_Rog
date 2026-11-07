# Team Task Allocation, Ownership Matrix & Hackathon Roadmap â€” Switch_Rog

## 1. Team Roles & Ownership Boundaries

Switch_Rog is built collaboratively by a two-person engineering team for the **Flip the Switch Hackathon**. To prevent duplicate effort and guarantee complete ownership of deliverables, responsibilities are strictly demarcated according to the project handover specifications:

```
+-----------------------------------------------------------------------------------+
|                                 Switch_Rog Team                                   |
+-----------------------------------------+-----------------------------------------+
| Sunayana                                | Vaibhav                                 |
| Project Planning & Workflow Lead        | Technical Lead & Architect              |
+-----------------------------------------+-----------------------------------------+
| â€¢ Requirements Specification            | â€¢ Technical Architecture & Design       |
| â€¢ Workflow Design & Use Cases           | â€¢ Technical Requirements                |
| â€¢ Task Allocation & Tracking            | â€¢ Switch Bridge Deployment & Gateway    |
| â€¢ Mattermost Channel & UX Validation    | â€¢ OpenCode Agent Runtime Configuration  |
| â€¢ Agent Test Scenarios & Prompts        | â€¢ Runtime Integration & Process Runner  |
| â€¢ Two-User Collaboration Testing        | â€¢ Infrastructure Security & Sandbox     |
| â€¢ Human Approval & Rejection Logic      | â€¢ Technical Integration Debugging       |
| â€¢ GitHub Review Workflow Design         | â€¢ Container Orchestration (Docker/WSL2) |
| â€¢ Test Evidence Collection              |                                         |
| â€¢ Comprehensive Documentation           |                                         |
| â€¢ Final Demo Script & Presentation      |                                         |
+-----------------------------------------+-----------------------------------------+
|                              Shared Responsibilities                              |
| â€¢ GitHub Pull Request Code Reviews      | â€¢ Final Workflow Verification           |
| â€¢ End-to-End Integration Testing        | â€¢ Live Demo Rehearsal & Submission      |
+-----------------------------------------------------------------------------------+
```

---

## 2. Comprehensive Task Allocation Table

Every task includes its Stage, Owner, Dependencies, Status, Deliverable, and measurable Acceptance Criteria.
*Note: Statuses strictly reflect real evidence. Tasks requiring pending infrastructure are marked as "Pending Vaibhav Infrastructure" or "Planned", never falsely marked as completed.*

| Task ID | Task Description | Owner | Stage | Dependencies | Current Status | Expected Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TSK-01** | Author Requirements Specification | Sunayana | Stage 1 | None | **Completed** | `docs/requirements.md` | Contains 19 FRs with IDs and acceptance criteria, NFRs, security rules, and user stories. |
| **TSK-02** | Author System Workflow Specification | Sunayana | Stage 1 | TSK-01 | **Completed** | `docs/workflow.md` | Details the 14-step shopping cart bug fix workflow, exception flows, and proposed vs. implemented status. |
| **TSK-03** | Author Task Allocation Matrix | Sunayana | Stage 1 | TSK-01 | **Completed** | `docs/task-allocation.md` | Full matrix with assigned owners, dependencies, deliverables, and acceptance criteria. |
| **TSK-04** | Author Technical Architecture Specification | Vaibhav | Stage 1 | None | In Progress | `docs/architecture.md` | Component diagrams, container networking, and interface specs on `feature/architecture`. |
| **TSK-05** | Research Switch & Mattermost Integration | Sunayana | Stage 2 | TSK-02 | **Completed** | `docs/mattermost-workflow.md` | Verifies Switch Console bundling, channel structures, authentication, and test procedures. |
| **TSK-06** | Deploy Mattermost & Switch Gateway Runtime | Vaibhav | Stage 2 | TSK-04 | Pending Vaibhav Infrastructure | Switch Console / Docker stack | Running Switch bridge listening to Mattermost events on developer workstation. |
| **TSK-07** | Configure OpenCode Execution Sandbox | Vaibhav | Stage 2 | TSK-06 | Pending Vaibhav Infrastructure | OpenCode Runner configuration | OpenCode CLI responds to subprocess calls within approved directory. |
| **TSK-08** | Prepare AI Agent Test Scenarios | Sunayana | Stage 3 | TSK-01, TSK-02 | **In Progress** | `docs/agent-test-scenarios.md` | 5 detailed test cases (Bug fix, Missing info, Code fix, Unauthorized action, Failed test). |
| **TSK-09** | Prepare Two-User Collaboration Test Plan | Sunayana | Stage 3 | TSK-05 | Planned | `docs/collaboration-test-plan.md` | Test steps for Sunayana & Vaibhav collaborating in shared Mattermost room with disconnect tests. |
| **TSK-10** | Implement Switch Thread-to-Session Routing | Vaibhav | Stage 3 | TSK-06, TSK-07 | Pending Vaibhav Infrastructure | Switch route handlers | Mattermost `root_id` maintains dedicated OpenCode conversation context. |
| **TSK-11** | Design Human Approval & GitHub PR Workflow | Sunayana | Stage 3 | TSK-02 | Planned | `docs/approval-workflow.md` | Interactive/command approval states, rejection rollback, PR conventions, and merge criteria. |
| **TSK-12** | Implement Dangerous Command Blacklist Filter | Vaibhav | Stage 3 | TSK-06 | Pending Vaibhav Infrastructure | Command filter middleware | Destructive commands (`rm -rf`, `sudo`, `curl | sh`) intercepted and blocked. |
| **TSK-13** | Implement Unified Diff Formatter for Chat | Sunayana | Stage 3 | TSK-11 | Planned | Chat diff formatting spec | Git diffs rendered cleanly in Markdown inside Mattermost thread. |
| **TSK-14** | Create Demonstration Shopping Application | Sunayana | Stage 4 | TSK-02 | Planned | Mock e-commerce app repo/folder | App with broken Place Order button and unit test suite ready for triage. |
| **TSK-15** | Execute End-to-End Integration Testing | Shared | Stage 4 | TSK-06, TSK-08, TSK-14 | Planned | `docs/testing-plan.md` + Evidence logs | Full 14-step workflow verified live from chat to merged GitHub PR. |
| **TSK-16** | Peer Review & Pull Request Verification | Shared | Stage 4 | TSK-15 | Planned | Merged Pull Requests on GitHub | Sunayana & Vaibhav cross-review branches; no direct commits to `main`. |
| **TSK-17** | Author Developer User Guide | Sunayana | Stage 4 | TSK-11, TSK-15 | Planned | `docs/user-guide.md` | Step-by-step instructions for developers to join chat, invoke agent, and review code. |
| **TSK-18** | Author Hackathon Demo Script & Walkthrough | Sunayana | Stage 4 | TSK-14, TSK-15 | Planned | `docs/demo-script.md` | Timed 3-minute video presentation script demonstrating the shopping cart fix. |
| **TSK-19** | Final Project Rehearsal & Submission | Shared | Stage 4 | TSK-17, TSK-18 | Planned | Hackathon submission package | Final video recording, clean repo, verified documentation, and submission form. |

---

## 3. Four-Stage Project Roadmap & Milestone Verification

```
+-----------------------------------------------------------------------------------+
| STAGE 1: Team Setup & Planning (CURRENT STAGE)                                    |
| [Deliverables: requirements.md, workflow.md, task-allocation.md]                  |
| -> Sunayana completes planning documentation on feature/project-planning.         |
| -> Vaibhav prepares architecture documentation on feature/architecture.           |
| Verification: Complete specifications peer-reviewed and committed.               |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| STAGE 2: Chat Platform & Bridge Preparation                                       |
| [Deliverables: mattermost-workflow.md, Switch gateway, OpenCode runner]           |
| -> Sunayana researches Switch/Mattermost integration and authors test procedures. |
| -> Vaibhav deploys Switch Console / Mattermost container and connects OpenCode.  |
| Verification: Bot responds to @opencode ping in Mattermost channel.               |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| STAGE 3: Test Scenarios, Collaboration & Approval Workflows                       |
| [Deliverables: agent-test-scenarios.md, collaboration-test-plan.md,               |
|  approval-workflow.md, command filters, session routing]                          |
| -> Sunayana designs 5 agent test cases, 2-user test plan, and approval workflows. |
| -> Vaibhav implements session routing, command blacklist, and PR automation.     |
| Verification: Approval gates hold code execution until human authorizes.          |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| STAGE 4: End-to-End Verification, Documentation & Demo                            |
| [Deliverables: testing-plan.md, user-guide.md, demo-script.md, demo video]        |
| -> Team executes 14-step shopping cart bug fix scenario live.                     |
| -> Sunayana authors user guide, testing plan, and demo walkthrough script.        |
| -> Both team members rehearse, record 3-min demo video, and submit.               |
| Verification: Passing integration tests, clean GitHub PR, live demo verified.     |
+-----------------------------------------------------------------------------------+
```

---

## 4. Risk Assessment & Low-Overhead Mitigation Plan

| Risk ID | Description | Severity | Owner | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | **LLM API Quota Depletion / Cost:** Free tier limits exhausted during agent test iterations. | High | Vaibhav | Use token-efficient prompting; inspect only necessary files; use local/free open-weight models during development testing. |
| **RSK-02** | **Workspace Code Corruption:** Agent hallucinates or deletes working application files. | High | Sunayana / Vaibhav | Strictly enforce git feature branches (`feature/fix-...`); require human plan approval before file modification; enable safe targeted rollback (`git checkout HEAD -- <files>` or ephemeral task branch deletion) instead of blanket `git checkout .`. |
| **RSK-03** | **Hardware & Memory Exhaustion:** Student laptop running Docker, Mattermost, and agent runs low on RAM. | Medium | Vaibhav | Leverage Switch Console bundled Mattermost; limit container RAM in Docker Compose; avoid spinning up unnecessary background VMs. |
| **RSK-04** | **Unauthenticated or Leaked Secrets:** Accidental commit of API keys or access tokens. | Critical | Both | Use `.env.example` templates; strictly add `.env` to `.gitignore`; pre-commit diff inspections before every git push. |
| **RSK-05** | **Direct Git Pushes to Main:** Unreviewed code landing directly on production branch. | Critical | Sunayana / Vaibhav | GitHub branch protection rules enabled on `main`; mandatory Pull Request reviews; agent git credentials restricted from pushing to `main`. |
| **RSK-06** | **Time Constraints & Scope Creep:** Spending excessive time on UI polish rather than core workflow. | High | Sunayana | Prioritize text-based command approvals (`!approve`, `!reject`) over complex custom UI widgets; keep demo focused on single reproducible scenario. |

---

## 5. Definition of Done (DoD)

A task or milestone is marked **Complete** only when:
1. The code or document is committed to the designated feature branch (`feature/project-planning` or `feature/architecture`).
2. There are zero unverified claims, fabricated logs, or placeholder text.
3. Every functional requirement maps to a verified test or tangible deliverable.
4. Peer review is conducted via GitHub Pull Request before merging to `main`.
5. All security checks pass: no secrets committed, sandbox boundaries verified.
