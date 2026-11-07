# Hackathon Live Demonstration Script (3-Minute Walkthrough) — Switch_Rog

## 1. Demonstration Overview

* **Hackathon:** Flip the Switch Hackathon
* **Project Name:** Switch_Rog
* **Team:** Sunayana (Workflow Lead) & Vaibhav (Technical Lead)
* **Target Duration:** Exactly 3 minutes (180 seconds)
* **Core Demonstration Scenario:** Resolving an online shopping application defect where clicking the **"Place Order"** button silently fails on the checkout page.
* **Key Objective:** Clearly demonstrate that **Switch** serves as the essential bridge connecting team communication in **Mattermost** with **OpenCode**, enabling transparent, two-developer peer review and traceable GitHub Pull Request delivery.

---

## 2. Timed 3-Minute Script Breakdown

```
[0:00 - 0:30] Introduction & Problem: The Isolated AI Bottleneck
      │
      ▼
[0:30 - 1:10] Task Initiation & Two-Developer Context in Mattermost
      │
      ▼
[1:10 - 1:50] Switch Routing, OpenCode Analysis & Human Plan Approval
      │
      ▼
[1:50 - 2:30] Sandboxed Testing, Diff Inspection & Remote Push
      │
      ▼
[2:30 - 3:00] GitHub Peer Review, Merge & Loop Closure in Chat
```

---

### Segment 1: The Problem & Vision (0:00 – 0:30)
* **Visual:** Split screen showing traditional solo editor terminal vs. team chat.
* **Speaker:** Sunayana
* **Spoken Script:**
  > "Hello everyone, I'm Sunayana, and with my teammate Vaibhav, we present **Switch_Rog**.
  > Today's AI coding assistants are lonely tools locked inside individual developers' private IDEs. Teammates cannot see what the agent is doing, leading to duplicate work, unreviewed code, and broken builds.
  > We flipped the switch by bringing AI directly into our team chat. Using **Switch** as our messaging bridge, our AI coding agent **OpenCode** collaborates with both of us side-by-side in Mattermost, governed by strict human approval gates and GitHub source control."

---

### Segment 2: Task Initiation & Collaborative Context (0:30 – 1:10)
* **Visual:** Mattermost desktop app showing `#bug-reports`. Sunayana types a message; Vaibhav is visible in the channel.
* **Speaker:** Sunayana & Vaibhav
* **Action & Spoken Script:**
  * **Sunayana:**
    > "Here in our `#bug-reports` channel, I found an issue in our shopping cart app: clicking 'Place Order' on the checkout page does nothing."
  * **Sunayana (Types in Mattermost):**
    ```text
    @opencode BUG: On the checkout page (/checkout), clicking the "Place Order" button
    does not submit the order. Please inspect src/components/checkout.js and propose a fix.
    ```
  * **Vaibhav:**
    > "I see Sunayana's bug report immediately in our shared workspace. I ran the developer console and found the exact error."
  * **Vaibhav (Replies in Thread):**
    ```text
    Reproduction context: Console shows "Uncaught TypeError: Cannot read properties of null (reading 'addEventListener') at checkout.js:42". Element #place-order-btn is queried before the modal DOM is rendered.
    ```
  * **Sunayana:**
    > "Notice that neither of us had to context-switch into a private terminal. Both of our inputs are right here in the shared thread."

---

### Segment 3: Switch Bridge Routing & Human Plan Approval (1:10 – 1:50)
* **Visual:** Mattermost shows instant bot reaction (`👀`). Switch terminal logs in corner show event parsed and routed to OpenCode. OpenCode posts its plan into the thread.
* **Speaker:** Vaibhav
* **Spoken Script:**
  > "This is where **Switch** is essential. Switch intercepts our Mattermost thread events, bundles Sunayana's bug description and my reproduction details into a single session, and passes them to the OpenCode agent.
  > OpenCode inspects the permitted repository files, identifies that the event listener was attached before the async modal mounted, and posts a structured plan back to Mattermost."
* **Visual on Screen:** OpenCode Markdown plan rendered in chat with Root Cause, Proposed Fix, and Awaiting Approval notice.
* **Speaker:** Sunayana
* **Action & Spoken Script:**
  > "Notice that OpenCode has not touched our code yet. The system pauses at Gate 1 for human sign-off. I review the plan, find it sound, and reply: `!approve`."
* **Sunayana (Types):**
  ```text
  !approve
  ```

---

### Segment 4: Sandboxed Code Edits, Testing & Diff Inspection (1:50 – 2:30)
* **Visual:** OpenCode edits code, runs `npm test`, passes all 3 tests, and formats a unified git diff in the thread.
* **Speaker:** Vaibhav
* **Spoken Script:**
  > "Switch receives the approval signal and instructs OpenCode to proceed. In an isolated feature branch, OpenCode applies defensive event delegation to `checkout.js` and adds a unit test in `checkout.test.js`.
  > It then executes the local test runner inside its sandbox. As you can see, all 3 tests pass, and OpenCode renders the exact unified git diff right in our chat."
* **Visual on Screen:** Passing test suite output and clean green/red git diff in Mattermost.
* **Speaker:** Sunayana
* **Action & Spoken Script:**
  > "I inspect the diff right here on my laptop. It's clean and safe. I reply: `!approve push`."
* **Sunayana (Types):**
  ```text
  !approve push
  ```

---

### Segment 5: GitHub Peer Review, Merge & Audit Loop (2:30 – 3:00)
* **Visual:** Switch posts GitHub Pull Request URL in thread. Vaibhav clicks the link, showing the PR on GitHub (`vaibhavbutul-work/Switch_Rog`).
* **Speaker:** Vaibhav
* **Spoken Script:**
  > "OpenCode pushes the branch and creates GitHub Pull Request #14. Switch posts the live link back to Mattermost.
  > As Technical Lead, I open the Pull Request on GitHub. The PR contains the full problem description, test logs, and the git diff. I review the code, approve the PR, and click Merge.
  > Direct pushes to `main` are strictly prevented—every AI change must undergo peer review."
* **Visual on Screen:** Vaibhav approves and merges on GitHub. A confirmation alert appears in Mattermost `#code-review`.
* **Speaker:** Sunayana (Closing)
* **Spoken Script:**
  > "And just like that, the bug is triaged, fixed, tested, reviewed, and merged collaboratively at zero cost. That is the power of **Switch_Rog**—making AI coding agents true, transparent teammates. Thank you!"

---

## 3. Demo Preparation & Verification Checklist

To guarantee a flawless live recording:
- [ ] Clean working tree on `feature/project-planning` and `feature/architecture`.
- [ ] Shopping cart application files ready in staging directory.
- [ ] Mattermost users `sunayana` and `vaibhav` verified in `#bug-reports`.
- [ ] Switch bridge service running and responding to `@opencode` mentions.
- [ ] Screen recorder set to 1080p, capturing both Mattermost and GitHub windows.
- [ ] Rehearsal completed to ensure timing stays within the 3-minute limit.
