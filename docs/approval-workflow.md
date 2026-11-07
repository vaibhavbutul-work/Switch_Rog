# Human Approval & GitHub Collaboration Workflow â€” Switch_Rog

## 1. Overview & Core Philosophy

In **Switch_Rog**, autonomous AI coding agents are never granted unilateral authority to modify production code, execute destructive commands, or merge pull requests.

Every consequential action is gated by **Human-in-the-Loop (HITL)** checkpoints within Mattermost, followed by formal peer review on GitHub.

```
[Developer Task]
      â”‚
      â–¼
[AI Analysis & Plan]
      â”‚
      â–¼
[GATE 1: Human Plan Approval] â”€â”€â”€â”€ (Rejected) â”€â”€â–º [Abort & Clean Workspace]
      â”‚ (Approved)
      â–¼
[Sandboxed Code Edit & Test Execution]
      â”‚
      â–¼
[GATE 2: Human Diff Approval] â”€â”€â”€â”€ (Rejected) â”€â”€â–º [Revert Changes & Abort]
      â”‚ (Approved)
      â–¼
[GitHub Feature Branch & PR Creation]
      â”‚
      â–¼
[GATE 3: Human Peer Review on GitHub] â”€â”€ (Changes Requested) â”€â”€â–º [Iterate Fix]
      â”‚ (Approved)
      â–¼
[Merge into Target Branch & Chat Notification]
```

---

## 2. The 10-Step End-to-End Approval Lifecycle

The system enforces a rigorous 10-step lifecycle ensuring accountability at every transition:

1. **Task Submission:** A developer (e.g., Sunayana) posts a task description in Mattermost `#bug-reports` tagging `@opencode`.
2. **AI Task Analysis:** OpenCode inspects workspace files, dependencies, and git status within its approved sandbox directory.
3. **Change Proposal:** OpenCode formulates a structured implementation plan (root cause, affected files, proposed code changes, test strategy) and posts it in the thread.
4. **Human Review of Proposal:** Both developers inspect the proposed approach. Teammates can discuss or suggest revisions.
5. **Human Approval or Rejection (Gate 1):**
   * **Approved:** Sunayana replies `!approve`. The agent proceeds to code modification.
   * **Rejected:** Sunayana replies `!reject` or `!modify <notes>`. The agent halts or refines its proposal.
6. **Execution within Configured Permissions:** OpenCode applies targeted edits strictly within its approved directory on a dedicated feature branch. Prohibited shell commands are blocked.
7. **Automated Test Execution & Diff Capture:** OpenCode runs the unit test suite (`npm test`), captures output, and generates a unified git diff (`git diff`).
8. **Human Review of Diff (Gate 2):** Developers inspect the actual diff and test logs in Mattermost. Sunayana replies `!approve push`.
9. **GitHub Handoff & Peer Review (Gate 3):**
   * The feature branch is pushed to GitHub.
   * A Pull Request is opened (via GitHub CLI `gh pr create` or developer manual push).
   * Vaibhav performs formal peer review on GitHub, inspects CI status, and requests changes or approves.
10. **Final Outcome Recording:** Upon approval, the PR is merged into `main`/target branch. Switch posts the final merge notification and commit SHA in the Mattermost thread.

---

## 3. Rejection & Failure Handling Scenarios

A core safety invariant of Switch_Rog is: **The system must never treat an unapproved or rejected change as approved.**

### 3.1 Rejection at Plan Review (Gate 1)
* **Trigger:** Developer posts `!reject` or clicks `[Reject]` on the proposed plan.
* **System Action:**
  1. Switch signals OpenCode to abort the current task.
  2. No files are edited; no git branch is created.
  3. Switch posts to thread: `🛑 Plan rejected by @sunayana. Task cancelled.`
  4. Session state is cleared.

### 3.2 Rejection at Diff Review (Gate 2) — Safe Targeted Rollback Protocol
* **Trigger:** Developer posts `!reject` after inspecting the unified git diff (e.g., poor code quality or unintended side effects).
* **Safety Invariant:** A blanket `git checkout .` or `git clean -fd` is strictly prohibited because it destroys unrelated developer edits or uncommitted work in the workspace.
* **System Action (Targeted Rollback):**
  1. Switch signals OpenCode to abort execution immediately.
  2. **Strategy A (Ephemeral Task Branch / Worktree):** If OpenCode operated in an isolated task branch (e.g., task/session-42-place-order):
     ```bash
     # Switch returns to base branch and discards only the rejected task branch
     git checkout feature/project-planning
     git branch -D task/session-42-place-order
     ```
  3. **Strategy B (Targeted In-Place Reversion):** If OpenCode modified files in-place:
     ```bash
     # Switch reverts strictly the files recorded in the session manifest
     git checkout HEAD -- src/components/checkout.js tests/checkout.test.js
     # Any newly created session files are selectively removed
     rm -f tests/checkout.test.js  # (only if created during session)
     ```
  4. All unrelated modified files or uncommitted developer changes remain completely intact.
  5. No remote push is executed.
  6. Switch posts to thread: 🛑 Diff rejected by @sunayana. Targeted rollback executed for session files. Developer working tree preserved. No branch pushed.

### 3.3 Rejection / Changes Requested on GitHub (Gate 3)
* **Trigger:** Vaibhav reviews the Pull Request on GitHub and clicks **Request Changes** with specific comments.
* **System Action:**
  1. GitHub webhook alerts Mattermost `#code-review`: `âš ï¸ Changes requested on PR #14 by @vaibhav`.
  2. Developers discuss the feedback in Mattermost.
  3. OpenCode or developer applies the adjustments to the existing feature branch and pushes a new commit.
  4. The PR cannot be merged until Vaibhav submits an official **Approved** review.

---

## 4. GitHub Collaboration & Pull Request Standards

To guarantee enterprise-grade source control and traceability, all code changes must comply with the following standards:

### 4.1 Feature Branch Naming Conventions
Direct pushes to `main` are strictly forbidden. All work must occur on dedicated branches matching:
* Bug fixes: `feature/fix-<component>-<issue-summary>` (e.g., `feature/fix-place-order-button`)
* Enhancements: `feature/feat-<feature-name>`
* Documentation: `feature/docs-<topic>`

### 4.2 Commit Message Standards
Commits must adhere to Conventional Commits:
```text
<type>(<scope>): <short description>

[Optional longer explanation of the problem, root cause, and fix]

Task: #<mattermost-thread-id>
Reviewed-by: @vaibhav
Co-authored-by: OpenCode <opencode@switchrog.local>
```
* Allowed types: `fix`, `feat`, `docs`, `test`, `refactor`, `chore`.

### 4.3 Pull Request Description Template
Every Pull Request generated for an AI-assisted fix must contain:

```markdown
## 📌 Summary of Changes
- Resolves: Issue with Place Order button failing on /checkout page.
- Mattermost Thread: #bug-reports (Thread ID: mm-thread-42)

## ðŸ” Root Cause
`src/components/checkout.js:42` queried `#place-order-btn` before modal DOM mount.

## ðŸ› ï¸ Changes Implemented
- Added defensive event delegation on checkout container.
- Added unit test in `tests/checkout.test.js`.

## 🧪 Test Verification & Evidence
- Command executed: `npm test tests/checkout.test.js`
- Result: 3 passed, 0 failed.
- Test output attached: PASS (1.42s).

## ðŸ›¡ï¸ Safety & Guardrail Checklist
- [x] No secrets, tokens, or credentials committed.
- [x] No modifications outside approved project directories.
- [x] Code tested locally prior to push.
- [x] Plan and Diff approved in Mattermost.
```

### 4.4 Reviewer Responsibilities & Merge Conditions
1. **Separation of Concerns:** The developer who initiated or guided the agent fix (e.g., Sunayana) cannot be the sole approver of the GitHub PR. The second developer (Vaibhav) must review the code.
2. **Reviewer Checklist:**
   * Verify diff addresses the issue without regressions.
   * Verify automated test passes.
   * Confirm no security risks or unvetted dependencies.
3. **Merge Conditions:**
   * At least 1 approved human review on GitHub.
   * All automated checks/tests pass.
   * Merge method: **Squash and Merge** or **Rebase and Merge** to maintain a clean history.
   * Delete feature branch immediately after merge.

### 4.5 Fallback Manual GitHub Actions
If the automated `gh pr create` integration is not yet active in Switch:
1. Developer pushes feature branch from terminal:
         ```bash
   git push origin feature/fix-place-order-button
   ```
2. Developer opens GitHub web interface, creates Pull Request using the template above, and pastes the link into Mattermost `#code-review`.
