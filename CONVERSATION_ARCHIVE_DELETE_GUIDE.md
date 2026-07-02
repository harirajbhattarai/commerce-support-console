# Support Console: Conversation Lifecycle, Archive, & Deletion Guide

This document establishes the official operational guidelines for archiving and deleting customer support chat logs within the HCHAHAL Support Console database.

---

## 1. Core Operating Principles

| Action | Recommended Trigger | Data Retention | Primary Purpose |
| :--- | :--- | :--- | :--- |
| **Archive** | Chat is resolved, ticket is closed, or user queries are completed. | **Retained permanently** in `chat_logs`, `agent_replies`, and child tables. | Preserves interactions for long-term RAG/LLM training logs, model learning, and support history audits. |
| **Permanent Delete** | Thread contains spam, duplicate sandbox tests, or GDPR/private data deletion requests. | **Erase completely** from all database tables. | Clean up development test runs or execute strict privacy/spam cleanups. |

---

## 2. Conversation Archival Flow (Recommended Path)

*   **When to Archive**: Once a conversation's status is changed to `Resolved`, support staff should click the **Archive Conversation** button in the Action Controls section of the side sheet.
*   **System Impact**:
    -   Sets the session status in Supabase to `archived`.
    -   Filters the thread out of active dashboard lists by default.
    -   Keeps the historical log database intact so that future vector similarity matching pipelines (e.g. pgvector) can query verified support turns for agent training.
*   **Retrieval**: Support staff can view archived conversations at any time by selecting the **Archived** status tab inside the Left Sidebar panel.

---

## 3. Permanent Deletion Flow (Dangerous Admin Path)

*   **When to Delete**: Only use this function for developer sandbox test sessions, spam attacks, or when a customer explicitly requests data deletion.
*   **System Impact**:
    -   Executes cascading SQL deletes to permanently erase child rows inside `reply_drafts`, `staff_notes`, and `agent_replies`.
    -   Erases the master records in `chat_logs`.
    -   This action is **irreversible** and removes the data from future training log sets.
*   **Safety Guards**:
    1.  **Zone Collapse**: The delete button is hidden inside a collapsible "Danger Zone" block.
    2.  **Required Text Confirmation**: Staff must type the word **DELETE** in the confirmation input field to enable execution.
    3.  **Browser Prompt Warning**: A browser confirm dialog warns the user before launching database actions.
