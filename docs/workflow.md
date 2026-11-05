# System Workflow, Use Cases & Testing — Switch_Rog

## 1. System Architecture & Information Flow

The Switch_Rog environment bridges team conversation with automated code execution through four primary components:

```
+-----------------------------------------------------------------------------------+
|                                 Mattermost                                        |
|  - Developers interact in channel threads (#dev-ai)                               |
|  - Thread context maps to a single coding session                                 |
|  - Approval buttons and status posts keep everyone synchronized                   |
+------------------------------------+----------------------------------------------+
                                     |
                                     | Mattermost Webhook / WebSocket API v4
                                     v
+-----------------------------------------------------------------------------------+
|                               Switch Bridge                                       |
|  - Intercepts @opencode mentions and thread replies                               |
|  - Manages session state (maps Mattermost root_id -> OpenCode session)            |
|  - Enforces Human-in-the-Loop approval gates                                      |
|  - Sanitizes inputs and formats outputs into Markdown                             |
+------------------------------------+----------------------------------------------+
                                     |
                                     | Agent Execution Protocol / CLI Subprocess
                                     v
+-----------------------------------------------------------------------------------+
|                             OpenCode AI Agent                                     |
|  - Plans tasks and inspects repository files                                      |
|  - Executes edits in an isolated local git workspace                              |
|  - Runs test suites inside sandbox (npm test / pytest)                            |
|  - Generates unified git diffs for human review                                   |
+------------------------------------+----------------------------------------------+
                                     |
                                     | Git CLI / GitHub REST API
                                     v
+-----------------------------------------------------------------------------------+
|                                   GitHub                                          |
|  - Remote repository hosting and collaboration                                    |
|  - New feature branch: feat/opencode-<task-id>                                    |
|  - Pull Request created with summary, test logs, and reviewer checklist           |
+-----------------------------------------------------------------------------------+
```

---

## 2. Complete End-to-End User Workflow

The end-to-end lifecycle of a collaborative coding task follows a 6-phase workflow designed for transparency, safety, and peer participation:

```
[Phase 1: Inception]
Developer mentions @opencode in Mattermost thread with a task description
        |
        v
[Phase 2: Planning]
OpenCode inspects files, creates step-by-step plan, and posts to thread
        |
        v
[Phase 3: Plan Review & Alignment]
Teammates review plan; accept plan or add comments to refine direction
        |
        v
[Phase 4: Sandboxed Execution & Verification]
OpenCode edits code in feature branch, executes local tests, and captures output
        |
        v
[Phase 5: Diff Inspection & Human Approval]
OpenCode posts unified git diff + test results; prompts developers for approval
   |                                     |
   | Approved                            | Rejected / Feedback provided
   v                                     v
[Phase 6: PR Creation]             OpenCode modifies implementation
Branch pushed to GitHub;           based on feedback and re-tests
PR link posted to Mattermost thread
```

### Detailed Phase Breakdown

#### Phase 1: Task Inception & Channel Invocation
1. A developer (e.g., Sunayana) opens the `#dev-ai` channel in Mattermost.
2. She creates a new message or thread:  
   `@opencode Please fix the null check error in authService.js when the token payload is missing an expiry timestamp, and add a test case.`
3. The Switch bridge receives the post via Mattermost WebSocket / Webhook, acknowledges the message with an emoji reaction (`👀`), and initializes an agent session tied to this `root_id`.

#### Phase 2: Agent Clarification & Plan Generation
1. Switch invokes OpenCode with the prompt and workspace path.
2. OpenCode searches the repository (`authService.js`, corresponding tests in `tests/auth.test.js`).
3. OpenCode drafts an implementation plan and Switch posts it back to the Mattermost thread:
   * **Target Files:** `src/services/authService.js`, `tests/auth.test.js`
   * **Proposed Actions:**
     1. Add validation for `payload.exp` before timestamp comparison.
     2. Write unit test verifying that missing `exp` throws `InvalidTokenError`.
     3. Run test runner (`npm test`) to ensure zero regressions.

#### Phase 3: Collaborative Review & Plan Approval
1. Sunayana and her teammate (Vaibhav) review the plan inside the thread.
2. Vaibhav posts a reply in the thread:  
   `"Make sure to also handle undefined payload entirely so it does not throw TypeError."`
3. Switch feeds this additional context into the active OpenCode session.
4. OpenCode acknowledges and updates the plan.
5. Sunayana clicks `[Approve Plan]` or replies `!approve`.

#### Phase 4: Sandboxed Code Execution & Test Verification
1. OpenCode creates a new git branch: `feat/fix-auth-token-null-check`.
2. OpenCode makes the targeted file edits in the local workspace.
3. OpenCode executes the test suite: `npm test tests/auth.test.js`.
4. Tests pass successfully (12 passing tests, 0 failing).

#### Phase 5: Diff Inspection & Human Approval Gate
1. OpenCode generates a unified git diff (`git diff HEAD~1`).
2. Switch formats the diff into a readable Markdown code block and posts it to the thread along with test execution logs.
3. Switch presents action options:
   * **`[Approve & Push]` / `!approve`**: Approves the changes and triggers remote push.
   * **`[Request Changes]` / `!modify <notes>`**: Asks OpenCode to adjust code.
   * **`[Reject & Discard]` / `!cancel`**: Aborts task and resets the branch.

#### Phase 6: GitHub Pull Request Creation & Review
1. Sunayana or Vaibhav replies `!approve`.
2. Switch instructs OpenCode to commit:  
   `git commit -m "fix(auth): handle missing exp and undefined token payload"`
3. OpenCode pushes the branch to GitHub:  
   `git push origin feat/fix-auth-token-null-check`
4. OpenCode creates a Pull Request via GitHub CLI (`gh pr create`) or GitHub REST API.
5. Switch posts the generated Pull Request URL into the Mattermost thread:  
   `🎉 Task Complete! Pull Request created: https://github.com/org/repo/pull/42`
6. Both developers can now perform their standard code review on GitHub and merge.

---

## 3. Human Approval Process & Safety Guardrails

Because autonomous AI coding agents can generate buggy code, break dependencies, or run harmful shell commands, Switch_Rog places strict human approval gates at key transition points.

### 3.1 Approval Matrix

| Action Type | Trigger Condition | Safety Level | Approval Required? | Default Action on Timeout |
| :--- | :--- | :--- | :--- | :--- |
| **Read Repository Files** | Inspecting code, searching files | Low | No (Auto-permitted) | Proceed |
| **Execute Read-Only Shell Commands** | `git status`, `git diff`, `npm test` | Low | No (Auto-permitted) | Proceed |
| **Edit Code in Feature Branch** | Modifying project files in workspace | Medium | Approved via Plan | Proceed |
| **Execute Destructive Shell Commands** | `rm -rf`, `sudo`, `npm publish` | High (Critical) | **Yes (Explicit Confirmation)** | Abort command |
| **Git Commit & Push to Remote** | Pushing commits to GitHub | High | **Yes (Human Review of Diff)** | Hold branch locally |
| **Direct Push to `main` Branch** | Attempting to push directly to `main` | Blocked | **Strictly Prohibited** | Hard block by Switch |

### 3.2 Human Approval Flowchart

```
                 [OpenCode Prepares Action]
                             |
                  Is action read-only?
                 /                    \
              Yes                      No
              /                          \
     [Execute Action]           Does it modify code or remote?
                                        |
                            +-----------+-----------+
                            |                       |
                     Local File Edit         Push / Dangerous Command
                            |                       |
                   Requires Plan Approval    Posts Diff & Prompts User
                            |                       |
                     User Approved?          User Approved?
                     /            \          /            \
                   Yes             No      Yes             No
                   /                \      /                \
            [Apply Edit]          [Revise] [Execute]    [Discard/Abort]
```

### 3.3 Interactive Approval Mechanics in Mattermost
Switch supports two fallback-tolerant methods for human interaction:
1. **Interactive Message Buttons:** Mattermost interactive attachments featuring:
   * `[✅ Approve & Push]`
   * `[✏️ Request Changes]`
   * `[❌ Cancel Task]`
2. **Text Command Fallbacks:** If interactive buttons are disabled or if users are on mobile:
   * `!approve` or `approve`
   * `!modify <instructions>`
   * `!reject` or `!cancel`

---

## 4. Realistic Use Cases

### Use Case 1: Collaborative Bug Fix (Cross-Developer Triage)

* **Actors:** Sunayana (Backend Dev), Vaibhav (Lead Dev), OpenCode (AI Agent).
* **Context:** A failing endpoint throws an unhandled error during user signup when phone number is omitted.
* **Step-by-step Scenario:**
  1. **Sunayana (Mattermost):** `@opencode The /api/users/signup route crashes with 500 when phoneNumber is not sent in the request body. It should be optional. Please fix and add test.`
  2. **OpenCode (Mattermost):** Posts analysis: "Located `src/routes/users.js` and `src/validators/userValidator.js`. The Joi schema marks `phoneNumber` as `.required()`. I will update schema to `.optional()` and update the controller fallback."
  3. **Vaibhav (Mattermost):** "Also ensure the database migration schema has `phone_number` set to nullable."
  4. **OpenCode (Mattermost):** "Checked database migration `003_create_users.sql`: `phone_number` is already nullable. Updated plan to include validator update and two unit tests (with and without phone number)."
  5. **Sunayana (Mattermost):** `!approve`
  6. **OpenCode:** Edits files, runs `npm test tests/users.test.js`, passes tests, and posts git diff.
  7. **Vaibhav (Mattermost):** Inspects diff in chat, notices clean implementation, clicks `[Approve & Push]`.
  8. **OpenCode:** Pushes branch `feat/opencode-signup-optional-phone` and creates GitHub PR #15.
  9. **Outcome:** Both developers collaborated in real time, caught a database dependency question, verified test results, and created a clean PR in under 4 minutes.

---

### Use Case 2: New Feature Scaffolding (Pair Programming with AI)

* **Actors:** Vaibhav (Developer), OpenCode (AI Agent), Sunayana (Reviewer).
* **Context:** The team needs a health check endpoint `/healthz` returning server uptime, memory usage, and git commit SHA.
* **Step-by-step Scenario:**
  1. **Vaibhav (Mattermost):** `@opencode Create a new health check endpoint at GET /healthz returning uptime in seconds, system memory usage in MB, and current git commit hash. Include a test file.`
  2. **OpenCode (Mattermost):** Generates structured plan:
     * Create `src/routes/health.js` with Express router.
     * Use `process.uptime()`, `process.memoryUsage()`, and read `process.env.GIT_COMMIT`.
     * Mount router in `src/app.js`.
     * Create test in `tests/health.test.js` using `supertest`.
  3. **Sunayana (Mattermost):** "Looks good, proceed."
  4. **OpenCode:** Generates code, runs `npm test tests/health.test.js`. Test output: `1 passed, 0 failed`.
  5. **OpenCode (Mattermost):** Posts unified diff.
  6. **Vaibhav (Mattermost):** `!approve`
  7. **OpenCode:** Pushes feature branch `feat/opencode-healthz-endpoint` and opens PR #16.
  8. **Outcome:** Standard scaffolding was created, tested, and reviewed without leaving the team chat.

---

### Use Case 3: Refactoring with Guardrail Interception & Correction

* **Actors:** Sunayana (Developer), OpenCode (AI Agent).
* **Context:** Refactoring old utility functions while preventing dangerous side effects.
* **Step-by-step Scenario:**
  1. **Sunayana (Mattermost):** `@opencode Please clean up unused helper functions in src/utils/formatters.js.`
  2. **OpenCode (Mattermost):** Proposes plan: "Identified `formatDate`, `formatCurrency`, and `formatLegacyPhone`. `formatLegacyPhone` is never referenced in `src/`. Plan: Remove `formatLegacyPhone` from `src/utils/formatters.js`."
  3. **Sunayana (Mattermost):** Remembers an external reporting microservice relies on that export. She replies:  
     `"Do not remove formatLegacyPhone yet! Add a @deprecated tag with JSDoc comment instead."`
  4. **OpenCode (Mattermost):** "Understood. Revising plan: Retain `formatLegacyPhone`, add JSDoc `@deprecated Use formatPhone instead`, and add a console warning."
  5. **Sunayana (Mattermost):** `!approve`
  6. **OpenCode:** Applies edits, runs linter and tests, posts diff showing deprecation annotations.
  7. **Sunayana (Mattermost):** Clicks `[Approve & Push]`.
  8. **Outcome:** A potential breaking change was caught and corrected during the conversation before any code was deleted or pushed.

---

## 5. Comprehensive Test Plan & Test Matrix

To verify that the Switch_Rog system meets all functional and non-functional requirements, the following test cases must be executed during integration testing.

| Test ID | Test Category | Description | Preconditions | Test Steps | Expected Result | Pass/Fail Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Invocation | Trigger agent via `@opencode` in channel | Mattermost and Switch bridge running; `#dev-ai` channel active. | 1. Post `@opencode help` in `#dev-ai`.<br>2. Observe channel. | Agent reacts with emoji (`👀`) within 3s and replies in thread with command overview. | Response is posted in a thread; no uncaught errors. |
| **TC-02** | Thread Isolation | Ensure multiple threads maintain isolated contexts | Two separate threads started in `#dev-ai`. | 1. In Thread A, prompt agent with task A.<br>2. In Thread B, prompt agent with task B.<br>3. Ask agent in Thread A: "What task are we doing?" | Agent in Thread A references task A only; does not leak context from Thread B. | Strict context isolation between `root_id` sessions. |
| **TC-03** | Multi-Developer Collaboration | Second developer steering active agent thread | Thread A active with Sunayana and agent. | 1. Sunayana prompts agent.<br>2. Vaibhav posts additional constraint in Thread A.<br>3. Agent outputs plan. | Agent incorporates Vaibhav's constraint into its updated plan. | Context from both human users is retained in session. |
| **TC-04** | Code Modification & Sandbox | OpenCode edits local files and executes tests | Workspace contains clean git repo with simple Node/Python test. | 1. Prompt `@opencode fix typo in greet() and run tests`.<br>2. Inspect execution. | OpenCode modifies file, runs test suite, captures stdout, and reports test pass. | Test runner executes successfully in sandbox; diff generated. |
| **TC-05** | Human Approval Gate (Approval) | Agent holds changes until user approves | Agent has generated diff and is waiting for approval. | 1. Developer replies `!approve` or clicks `[Approve]`.<br>2. Observe system actions. | Agent commits code to feature branch and pushes to GitHub. | Code is committed only *after* approval command. |
| **TC-06** | Human Approval Gate (Rejection) | Agent aborts changes on user rejection | Agent has generated diff and is waiting for approval. | 1. Developer replies `!reject` or `!cancel`.<br>2. Observe system actions. | Agent discards local changes (`git checkout`), cancels task, and notifies thread. | Workspace is restored to clean state; no branch pushed. |
| **TC-07** | Dangerous Command Guardrail | Block harmful shell command execution | Agent is prompted to execute an unsafe command. | 1. User prompts `@opencode delete root directory rm -rf /`.<br>2. Switch evaluates command. | Switch security filter intercepts and blocks command with safety warning in thread. | Command is blocked; host and workspace are unharmed. |
| **TC-08** | GitHub PR Creation | Automated creation of branch and GitHub PR | Valid GitHub personal access token configured in `.env`. | 1. Execute task to completion and approve push.<br>2. Check GitHub repo. | New branch `feat/...` exists on GitHub; open PR exists with proper title, summary, and thread link. | Clickable PR URL posted in Mattermost thread. |
| **TC-09** | Command Timeout Safeguard | Prevent infinite terminal command hangs | Agent executes a command with an infinite loop (e.g., `yes`). | 1. Trigger command that does not terminate.<br>2. Wait 60 seconds. | Switch/OpenCode runner terminates process upon reaching 60s timeout and reports error. | System does not freeze; thread receives timeout message. |
| **TC-10** | Error Recovery & Reporting | Agent reports build or syntax failures cleanly | Broken code deliberately introduced into workspace. | 1. Instruct agent to run failing test suite.<br>2. Observe agent output. | Agent captures error log, summarizes root cause, and offers fix without crashing. | Thread displays structured error summary; bridge remains healthy. |
