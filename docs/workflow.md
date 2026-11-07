# Collaborative Development Workflow & Scenario Specification â€” Switch_Rog

## 1. System Architecture & Information Flow

The Switch_Rog environment coordinates human developer collaboration with autonomous AI coding capabilities through four primary components:

```
+-----------------------------------------------------------------------------------+
|                        1. Shared Mattermost Workspace                             |
|  - Developers (Sunayana & Vaibhav) collaborate in channel #bug-reports            |
|  - Tasks initiated and discussed in dedicated message threads (root_id)           |
|  - Thread context maps directly to a single coding session                        |
|  - Human approval commands and diffs rendered in GitHub-flavored Markdown         |
+------------------------------------+----------------------------------------------+
                                     |
                                     | Mattermost Webhook / WebSocket Event
                                     v
+-----------------------------------------------------------------------------------+
|                           2. Switch Messaging Bridge                              |
|  - Listens for @opencode mentions and thread replies                              |
|  - Maps Mattermost thread ID (root_id) to active OpenCode agent session           |
|  - Intercepts consequential actions and enforces Human-in-the-Loop approval       |
|  - Dispatches structured prompts and context updates to OpenCode                  |
+------------------------------------+----------------------------------------------+
                                     |
                                     | Agent Protocol / CLI Subprocess
                                     v
+-----------------------------------------------------------------------------------+
|                           3. OpenCode AI Coding Agent                             |
|  - Inspects approved workspace files and tests                                    |
|  - Formulates structured implementation plan                                      |
|  - Executes targeted code modifications in isolated feature branch                |
|  - Runs test suites (npm test / pytest) inside sandbox and captures logs          |
|  - Generates unified git diff for human review                                    |
+------------------------------------+----------------------------------------------+
                                     |
                                     | Git CLI / GitHub REST API
                                     v
+-----------------------------------------------------------------------------------+
|                         4. GitHub Repository & Review Gate                        |
|  - Remote repository: vaibhavbutul-work/Switch_Rog                                |
|  - Dedicated feature branch: feature/fix-place-order-button                       |
|  - Traceable Pull Request with problem summary, diff, and test evidence           |
|  - Peer review and merge performed by human developer                             |
+------------------------------------+----------------------------------------------+
                                     |
                                     | PR URL & Status Notification
                                     v
                         [Reported to Mattermost Thread]
```

---

## 2. Actors and Responsibilities

| Actor | Entity Type | Primary Responsibilities |
| :--- | :--- | :--- |
| **Sunayana** | Human Developer (Workflow Lead) | Identifies bug, posts initial report in Mattermost, reviews agent proposals, executes plan approvals, tests results, and verifies documentation. |
| **Vaibhav** | Human Developer (Technical Lead) | Adds technical reproduction context, configures runtime infrastructure, reviews git diffs, performs peer review on GitHub PR, and approves merges. |
| **Switch** | Core Messaging Bridge | Ingests chat events, maintains thread-to-session state, halts execution at approval gates, formats agent responses into Markdown, and routes data. |
| **OpenCode** | AI Coding Agent | Reads codebase, diagnoses root cause, drafts step-by-step plans, writes code edits, executes test suites, and outputs unified diffs. |
| **GitHub** | Version Control Host | Manages repository branches, enforces branch protection on `main`, hosts Pull Requests, and tracks peer review approvals. |

---

## 3. End-to-End 14-Step Bug Fix Workflow

### Demonstration Scenario: Online Shopping Application "Place Order" Button Failure
In a web-based e-commerce application, clicking the **"Place Order"** button on the checkout screen silently fails: no network request is dispatched, the cart is not cleared, and no confirmation is displayed.

```
+----------------------------------------------------------------------------------+
|                           14-STEP WORKFLOW LIFECYCLE                             |
+----------------------------------------------------------------------------------+
  [1. Issue Identified]       --> Sunayana discovers Place Order button fails
  [2. Bug Reported in Chat]   --> Sunayana posts issue in Mattermost #bug-reports
  [3. Reproduction Added]     --> Vaibhav posts console error & reproduction steps
  [4. Task Routed by Switch]  --> Switch captures thread and invokes OpenCode
  [5. OpenCode Ingestion]     --> OpenCode loads repository context & prompt
  [6. Codebase Inspection]    --> OpenCode reads checkout.js and cartService.js
  [7. Root Cause Diagnosed]   --> OpenCode identifies missing event listener / null ref
  [8. Fix Proposed]           --> OpenCode posts structured plan to thread
  [9. Human Review & Gate]    --> Sunayana & Vaibhav review; Sunayana replies !approve
  [10. Code Edit & Test]      --> OpenCode edits code, runs test suite, posts diff
  [11. Git Branch & PR]       --> Branch pushed to GitHub; Pull Request opened
  [12. Peer Code Review]      --> Vaibhav reviews diff and test results on GitHub
  [13. Approved & Merged]     --> PR merged into target branch
  [14. Chat Notification]     --> Switch posts completion summary & PR link in thread
+----------------------------------------------------------------------------------+
```

### Detailed Step-by-Step Breakdown

#### Step 1: Sunayana Identifies the Issue
* **Context:** During integration testing of the shopping portal, Sunayana adds items to the cart, proceeds to checkout, fills in shipping details, and clicks "Place Order".
* **Observed Symptom:** The button does nothing. No order confirmation is displayed.

#### Step 2: Sunayana Posts the Bug Report in Mattermost
* **Action:** In Mattermost channel `#bug-reports`, Sunayana starts a new thread tagging OpenCode:
  ```text
  @opencode BUG: On the checkout page (/checkout), clicking the "Place Order" button
  does not submit the order or trigger any action. Please inspect the checkout flow
  and determine why the submission handler is failing.
  ```

#### Step 3: Vaibhav Adds Reproduction Steps
* **Action:** Vaibhav opens the browser developer console on the staging instance, reproduces the bug, and replies directly in Sunayana's Mattermost thread:
  ```text
  Reproduction context:
  Browser console shows: "Uncaught TypeError: Cannot read properties of null (reading 'addEventListener') at checkout.js:42".
  The DOM element #place-order-btn is queried before the modal DOM is rendered.
  Also ensure checkout.test.js covers this scenario.
  ```

#### Step 4: Switch Routes the Supported Conversation to OpenCode
* **Action:** The Switch bridge intercepts the thread updates:
  1. Detects `@opencode` mention and thread reply from Vaibhav.
  2. Maps Mattermost `root_id` to an active OpenCode session.
  3. Bundles Sunayana's bug description and Vaibhav's reproduction details into a single prompt payload.
  4. Reacts to the message with an acknowledgment emoji (`👀`) and posts a status update: `Switch: Task routed to OpenCode. Analyzing workspace...`

#### Step 5: OpenCode Receives the Task
* **Action:** OpenCode receives the bundled task context, initializes its workspace environment, and identifies the relevant project directories.

#### Step 6: OpenCode Inspects the Approved Project Directory
* **Action:** OpenCode searches and reads relevant files within the approved workspace:
  * `src/components/checkout.js`
  * `src/services/orderService.js`
  * `tests/checkout.test.js`

#### Step 7: OpenCode Identifies the Probable Cause
* **Findings:**
  1. In `src/components/checkout.js`, line 42 attaches an event listener:
     `document.getElementById('place-order-btn').addEventListener('click', handleOrderSubmission);`
  2. In modern checkout flows, the order review section is rendered dynamically inside an async modal. At line 42 execution time, `#place-order-btn` has not yet mounted into the DOM, causing `null.addEventListener` to throw a `TypeError`.
  3. No unit test exists verifying button binding after dynamic DOM mount.

#### Step 8: OpenCode Proposes a Fix
* **Action:** OpenCode drafts a structured implementation plan and Switch posts it back into the Mattermost thread:
  ```markdown
  ### 📋 OpenCode Proposed Plan: Fix Place Order Button

  **Root Cause:**
  `src/components/checkout.js:42` queries `#place-order-btn` before the modal mounts,
  resulting in an unhandled `TypeError: Cannot read properties of null`.

  **Proposed Solution:**
  1. Wrap button binding in a DOM lifecycle check or event delegation on the checkout container (`#checkout-container`).
  2. Add defensive guard check ensuring element exists before attaching listeners.
  3. Add unit test in `tests/checkout.test.js` simulating async modal mount and button click.
  4. Run test runner (`npm test tests/checkout.test.js`) to verify zero regressions.

  **Awaiting Human Approval:**
  Reply `!approve` to apply these edits and run tests, `!modify <feedback>` to revise, or `!reject` to cancel.
  ```

#### Step 9: A Human Reviews the Proposed Action
* **Action:** Sunayana and Vaibhav review the proposed plan in the thread.
* **Outcome:** The plan addresses both the root cause and Vaibhav's reproduction note. Sunayana posts:
  ```text
  !approve
  ```

#### Step 10: Approved Changes are Applied and Tested
* **Action:**
  1. Switch intercepts `!approve` and signals OpenCode to proceed.
  2. OpenCode checks out feature branch: `feature/fix-place-order-button`.
  3. OpenCode modifies `src/components/checkout.js` with defensive event delegation.
  4. OpenCode adds the new test case to `tests/checkout.test.js`.
  5. OpenCode executes the test suite: `npm test tests/checkout.test.js`.
  6. Test suite completes successfully:
     ```text
     PASS tests/checkout.test.js
       âœ“ renders checkout modal
       âœ“ binds place order button safely after async mount (14ms)
       âœ“ dispatches order payload on click (28ms)

     Tests: 3 passed, 3 total
     Snapshots: 0 total
     Time: 1.42s
     ```
  7. OpenCode generates a unified git diff and Switch formats it into the thread:
     ```diff
     --- a/src/components/checkout.js
     +++ b/src/components/checkout.js
     @@ -39,5 +39,8 @@ export function initCheckout() {
     -  document.getElementById('place-order-btn').addEventListener('click', handleOrderSubmission);
     +  const checkoutContainer = document.getElementById('checkout-container');
     +  if (checkoutContainer) {
     +    checkoutContainer.addEventListener('click', (e) => {
     +      if (e.target && e.target.id === 'place-order-btn') {
     +        handleOrderSubmission(e);
     +      }
     +    });
     +  }
     ```

#### Step 11: A Developer or Supported Integration Creates a GitHub Branch and Pull Request
* **Action:**
  1. Switch prompts for final push confirmation or executes automated PR creation if configured.
  2. Human replies `!approve push` or triggers PR creation.
  3. Feature branch `feature/fix-place-order-button` is pushed to GitHub remote `origin`.
  4. Pull Request #14 is created against target branch:
     * Title: `fix(checkout): safely delegate Place Order button event binding`
     * Description: Includes problem description, root cause, diff summary, test pass log, and link to Mattermost thread.

#### Step 12: The Other Developer Reviews the Changes
* **Action:**
  1. Switch posts the live PR link into the Mattermost thread:
     `🚀 Pull Request created: https://github.com/vaibhavbutul-work/Switch_Rog/pull/14`
  2. Vaibhav opens the Pull Request on GitHub.
  3. Vaibhav inspects the changed files, checks that CI/test checks pass, and verifies adherence to project coding standards.

#### Step 13: Approved Changes are Merged
* **Action:**
  1. Vaibhav approves the Pull Request on GitHub.
  2. The Pull Request is merged into the integration branch (`main` or target).
  3. The feature branch is deleted on GitHub.

#### Step 14: The Result is Reported in Mattermost
* **Action:**
  1. Switch / GitHub webhook posts a closure notification into the Mattermost thread:
     ```text
     âœ… Task Complete! PR #14 merged successfully by @vaibhav.
     Issue: Place Order button failure resolved and verified.
     ```
  2. Sunayana verifies on staging and closes the ticket.

---

## 4. Triggering Events & Message Flow

```
[User Input in Mattermost]
         |
         v
+-------------------------------+
| Mattermost Outgoing Webhook / |
| WebSocket Event               |
+---------------+---------------+
                |
                v
+-------------------------------+
| Switch Message Filter:        |
| - Is message in #bug-reports? |
| - Does it mention @opencode?  |
| - Is it an approval command?  |
+---------------+---------------+
                |
       +--------+--------+
       |                 |
  (Task Request)   (Approval / Command)
       |                 |
       v                 v
+---------------+ +---------------+
| Invoke OpenCode| | Signal Active |
| Session       | | OpenCode Proc |
+---------------+ +---------------+
```

---

## 5. Agent Permissions & Guardrails

| Resource / Action | Permission Level | Enforcement Mechanism |
| :--- | :--- | :--- |
| **Read Workspace Files** | Allowed (Unrestricted within project root) | Restricted by OpenCode process root configuration. |
| **Read Files Outside Workspace** | **Blocked** | OS / Docker filesystem isolation prevents path traversal (`../`). |
| **Run Read-Only Terminal Commands** (`git status`, `git diff`) | Allowed | Process runner automatically permits non-destructive inspection. |
| **Run Test Suites** (`npm test`, `pytest`) | Allowed | Sandboxed execution with 60-second timeout. |
| **Apply Code Modifications to Files** | **Requires Human Plan Approval** | Switch blocks write tools until `!approve` is received. |
| **Run Destructive Commands** (`rm -rf`, `sudo`, `mkfs`) | **Strictly Prohibited** | Command blacklist filter in Switch bridge intercepts and aborts. |
| **Push Branch to GitHub** | **Requires Human Diff Approval** | Remote push held until human signs off on unified diff. |
| **Direct Push to `main` Branch** | **Strictly Prohibited** | Git pre-push hook and GitHub branch protection rule. |

---

## 6. Human Approval Mechanics

### 6.1 Two-Stage Approval Architecture
Switch enforces two mandatory human sign-off gates for every task:

1. **Gate 1: Plan Approval (Pre-Modification):**
   * Before any project file is touched or modified, OpenCode must output its implementation plan.
   * Execution pauses until a human submits `!approve`.
2. **Gate 2: Diff Approval (Pre-Push):**
   * After code is edited and unit tests run, OpenCode produces a unified git diff.
   * Remote branch push and PR creation pause until a human submits `!approve`.

### 6.2 Supported Human Commands
* `!approve`: Approves the current step (plan or diff) and allows execution to proceed.
* `!modify <guidance>`: Rejects the current proposal and provides specific guidance for the agent to revise its work.
* `!reject` / `!cancel`: Completely aborts the task, reverts local workspace edits, and resets the session.

---

## 7. Exception & Edge Case Handling

### 7.1 Rejection Handling & Safe Targeted Rollback Protocol
* **Scenario:** Sunayana or Vaibhav inspects the agent's proposed plan or code diff and finds it unsatisfactory (e.g., incorrect architectural approach).
* **Safety Invariant:** A blanket wipe (`git checkout .` / `git clean -fd`) is strictly forbidden because it risks destroying unrelated developer edits or uncommitted files in the workspace.
* **System Action (Targeted Rollback Protocol):**
  1. User replies `!reject` in the thread.
  2. Switch immediately instructs OpenCode to terminate execution.
  3. **Branch/Worktree Isolation Strategy:** If OpenCode operated within an isolated ephemeral task branch (`task/session-<id>`) or a git worktree, Switch deletes the task branch (`git branch -D task/session-<id>`) or removes the worktree (`git worktree remove --force`), guaranteeing zero impact on the developer's working tree.
  4. **In-Place Targeted Rollback Strategy:** If OpenCode modified files directly in the repository, Switch inspects the session file manifest and selectively reverts only the specific files modified by the agent (`git checkout HEAD -- <target-files>`) and selectively deletes newly created session files, leaving all other developer files completely untouched.
  5. Switch posts an audit note to the thread: `🛑 Task aborted by user. Safe targeted rollback completed for session files. Working tree preserved.`
  6. The system must never treat an unapproved or rejected change as approved.

### 7.2 Missing-Context Handling
* **Scenario:** A user submits an overly vague request such as `@opencode The application is broken.`
* **System Action:**
  1. OpenCode recognizes insufficient context (no file, no error message, no reproduction steps).
  2. OpenCode does **not** guess or make random edits.
  3. OpenCode replies in the thread:
     ```text
     âš ï¸ Insufficient Information:
     Please specify:
     1. Which component or page is failing?
     2. What error messages or console logs are displayed?
     3. What are the expected vs. actual behaviors?
     ```
  4. Switch pauses the session and waits for user clarification before proceeding.

### 7.3 Agent Failure Handling
* **Scenario:** OpenCode crashes, throws an unhandled exception, or hangs during analysis.
* **System Action:**
  1. The Switch subprocess runner enforces a 60-second watchdog timer.
  2. If the process times out or exits with a non-zero exit code, Switch captures the stderr traceback.
  3. Switch posts an error alert to the thread:
     `âŒ OpenCode execution encountered an error: [Error summary]. Session reset.`
  4. The bridge remains operational and ready for subsequent tasks.

### 7.4 Test Failure Handling
* **Scenario:** OpenCode applies an edit, runs `npm test`, but one or more unit tests fail.
* **System Action:**
  1. OpenCode does **not** report false success or attempt to push broken code.
  2. OpenCode captures the failing test output, stack trace, and assertions.
  3. OpenCode posts the test failure report in the Mattermost thread:
     ```text
     âŒ Test Verification Failed:
     Test 'checkout button click' failed with assertion error.
     Proposed fix did not pass all regression tests.
     Would you like me to attempt an alternative fix? (Reply !retry or !reject)
     ```
  4. The code remains in the local feature branch without pushing to GitHub.

---

## 8. GitHub Handoff, Peer Review & Merge Workflow

1. **Branch Naming Standard:** All feature branches created for AI tasks must follow the pattern:
   `feature/fix-<component>-<issue-keyword>` (e.g., `feature/fix-place-order-button`).
2. **Commit Standard:** Commit messages follow Conventional Commits:
   `fix(checkout): safely delegate Place Order button event binding`
   `Co-authored-by: Sunayana <sunayana@switchrog.local>`
3. **Pull Request Protocol:**
   * PR is opened against `feature/architecture` or `main`.
   * The PR template requires: Problem Statement, Root Cause, Summary of Changes, Test Evidence, and Chat Thread Reference.
4. **Peer Review Gate:**
   * At least one human peer review is required before merging.
   * If Sunayana authored or initiated the task, Vaibhav must review and approve on GitHub.
   * Automated CI checks must pass.

---

## 9. Implementation Status: Proposed vs. Implemented Behaviour

To maintain complete engineering honesty and traceability, the table below clearly distinguishes what is currently implemented in our repository from proposed behavior pending infrastructure deployment:

| Workflow Component | Current Implementation Status | Notes / Pending Infrastructure |
| :--- | :--- | :--- |
| **Requirements & Workflow Documentation** | **Implemented** | Complete specifications in `docs/requirements.md` and `docs/workflow.md`. |
| **Task Allocation & Ownership Matrix** | **Implemented** | Defined in `docs/task-allocation.md`. |
| **Online Shopping Demo Bug Scenario Design** | **Implemented** | 14-step scenario documented; mock test cases designed. |
| **Human Approval & Rejection Logic Design** | **Implemented** | State machine and keyword grammar specified. |
| **Mattermost Local Workspace** | *Proposed / Pending Setup* | Awaiting local container configuration via Switch Console. |
| **Switch Messaging Bridge Routing** | *Proposed / Pending Setup* | Awaiting Switch gateway configuration by Vaibhav. |
| **OpenCode CLI Tool Execution** | *Proposed / Pending Setup* | Awaiting OpenCode local environment configuration by Vaibhav. |
| **Automated GitHub PR Creation via Bridge** | *Proposed / Planned* | Fallback manual PR creation workflow documented for Stage 2. |
| **End-to-End Chat-to-PR Execution** | *Proposed / Untested* | Requires running Switch + Mattermost stack. |

---

## 10. Expected Final Outcome

The expected outcome of this workflow is a seamless, transparent development lifecycle where:
1. Team members discuss bugs in their normal chat environment.
2. The AI agent acts as a responsive, obedient pair programmer rather than an uncontrolled autonomous actor.
3. Every line of code generated is reviewed by a human in chat before file modification and reviewed on GitHub before merging.
4. The entire process produces an auditable history across Mattermost, Git commits, and GitHub Pull Requests.
