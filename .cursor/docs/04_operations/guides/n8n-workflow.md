# n8n Workflow Guide

This document describes how n8n orchestrates MES events.

## Workflows

### 1. manufacturing-order-intake

- Trigger: HTTP Webhook.
- URL: `/webhook/manufacturing-order-created` (internal n8n URL).
- Flow:
  1. Receive payload from backend when a new order is created.
  2. Optionally call ERP or other external systems.
  3. Send notification (e.g., Telegram) about the new order.
  4. Log event in external system if needed.

### 2. task-dispatched

- Trigger: HTTP Webhook `/webhook/task-dispatched`.
- Flow:
  1. Receive task details from backend.
  2. Notify operator or work center (e.g., Telegram or other channel).
  3. Optionally write to a log or BI sink.

### 3. task-completed

- Trigger: HTTP Webhook `/webhook/task-completed`.
- Flow:
  1. Check if all tasks for the order are completed.
  2. If yes, call ERP API to mark order as complete.
  3. Send final notification.
  4. Update analytics sink if required.

## Export & Versioning

- Export workflows from n8n UI as JSON and store them in `n8n-workflows/`.
- Name files clearly, e.g.:
  - `manufacturing-order-intake.json`
  - `task-dispatched.json`
  - `task-completed.json`
- Keep this document in sync with actual workflows.

(Extend with more workflows as they are added.)
