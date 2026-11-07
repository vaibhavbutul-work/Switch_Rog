# Developer User Guide â€” Switch_Rog

## 1. Introduction
Welcome to **Switch_Rog**! This guide explains how human developers interact with the collaborative AI-assisted development workflow powered by **Mattermost**, the **Switch** messaging bridge, **OpenCode**, and **GitHub**.

---

## 2. Accessing the Shared Chat Workspace

1. **Prerequisites:**
   * Ensure the local Mattermost instance is running (hosted by Vaibhav via Switch Console).
   * Receive your login credentials or team invite link from your team lead.
2. **Logging In:**
   * Open your web browser and navigate to the Mattermost address:
     `http://localhost:8065` (or private team URL provided via Tailscale/tunnel).
   * Enter your assigned email/username and password.
   * Select the team: **`switch-rog`**.
3. **Navigating Channels:**
   * Go to **`#bug-reports`** for investigating and triaging bugs.
   * Go to **`#ai-agent-tasks`** for feature scaffolding or test creation.
   * Go to **`#code-review`** for GitHub Pull Request notifications.

---

## 3. Submitting a Task to the AI Agent

1. In the target channel (e.g., `#bug-reports`), type a message invoking `@opencode`:
   ```text
   @opencode BUG: On the checkout page, clicking the "Place Order" button does not submit the order or trigger any action. Please inspect src/components/checkout.js and propose a fix.
   ```
2. The Switch bridge will acknowledge your request with an emoji reaction (`👀`) and open a thread.
3. **Important:** Always keep subsequent conversation inside this thread to maintain session context.

---

## 4. Providing Additional Context as a Teammate

1. When a teammate posts a task, click **Reply** to open the thread panel.
2. Provide technical reproduction steps, error logs, or constraints:
   ```text
   Reproduction note: Console shows "Uncaught TypeError: Cannot read properties of null (reading 'addEventListener')".
   The #place-order-btn is queried before the async modal mounts.
   ```
3. Switch automatically ingests your reply and feeds the additional context into the active OpenCode session.

---

## 5. Reviewing AI-Generated Plans

1. OpenCode inspects the permitted repository files and posts a structured plan in the thread:
   * **Root Cause:** Explanation of why the bug occurs.
   * **Target Files:** List of files to be modified.
   * **Proposed Fix:** Code strategy.
   * **Test Strategy:** Unit tests to verify the fix.
2. Review the plan carefully with your teammate before taking action.

---

## 6. Approving or Rejecting Proposed Changes

The system enforces strict human approval gates:

### To Approve a Plan:
* Reply in the thread:
  ```text
  !approve
  ```
  *(Or click the `[Approve]` button if interactive attachments are enabled.)*
* The agent will proceed to edit the code, run local unit tests, and generate a unified diff.

### To Reject a Plan or Discard Changes:
* Reply in the thread:
  ```text
  !reject
  ```
* The task terminates immediately. If code was edited, the system performs a safe targeted rollback on the session files without touching your unrelated working changes.

### To Request Adjustments:
* Reply in the thread:
  ```text
  !modify Please ensure you also handle null discountCode defensively.
  ```
* The agent will adjust its plan or code and present an updated proposal.

---

## 7. Inspecting Diffs & GitHub Pull Request Review

1. Once tests pass, the agent posts a unified git diff and test logs into the thread.
2. Review the diff in the chat thread. If satisfied, reply:
   ```text
   !approve push
   ```
3. OpenCode commits the changes to a dedicated feature branch (e.g., `feature/fix-place-order-button`) and pushes to GitHub.
4. Switch posts the generated GitHub Pull Request URL into the thread.
5. Click the link to open the Pull Request on GitHub.
6. The second developer (Vaibhav or Sunayana) reviews the code diff on GitHub, verifies passing CI checks, and merges the Pull Request.

---

## 8. Verifying the Completed Task

1. Pull the merged changes locally:
          ```bash
   git checkout main
   git pull origin main
   ```
2. Run project tests:
          ```bash
   npm test
   ```
3. Confirm that the Place Order button bug is resolved and all unit tests pass.
4. Acknowledge task completion in Mattermost `#code-review`.
