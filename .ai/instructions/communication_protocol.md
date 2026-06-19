# Agent Communication Protocol: Brainy 1.0

This protocol defines communication rules for specialized AI agents collaborating in the Brainy 1.0 workspace.

## 1. Message Structure
All inter-agent messages must adhere to a structured schema to prevent context loss:
```json
{
  "sender": "AgentName",
  "recipient": "AgentName",
  "message_type": "request | response | notification | handover",
  "payload": {
    "task_id": "unique-task-id",
    "context_references": ["file:///path/to/file#lines"],
    "content": "Description of the request, response, or notification details"
  },
  "timestamp": "2026-06-19T11:26:53Z"
}
```

## 2. Task Handoff Structure
When handoff occurs between agents (e.g., from Backend Engineer to QA):
1. **Source Status Update**: The current agent marks the sub-task as `[x]` complete in `task.md`.
2. **Context Delivery**: The outgoing agent provides a handover message pointing to active files, API routes, or test paths.
3. **Target Initialization**: The incoming agent updates `SESSION_MEMORY.md` to reflect the new task ownership and immediately sets the task status to `[/]` (in progress).

## 3. Context Passing Rules
- **Minimize Bloat**: Never pass raw, long file context when a file reference is sufficient. Pass file path references using markdown links `[basename](file:///absolute/path/to/file)`.
- **Scope Limit**: Only load files directly related to the current task.

## 4. Memory Update Rules
- **Session Memory**: Updated by agents at the start and end of every task execution block.
- **Project Memory**: Updated only when structural modifications occur (new systems, database shifts, model changes).

## 5. Decision Sharing & ADRs
- All system-wide design changes require a new ADR file in `.ai/decisions/`.
- Once generated, the System Architect Agent broadcasts the ADR to other agents, updating `ARCHITECTURE_DECISIONS.md`.

## 6. Approval Workflows
- **Code Changes**: Requires validation by the QA Agent (passing test suite runs).
- **Architecture Updates**: Requires approval from the System Architect Agent and human review.

## 7. Conflict Resolution Rules
- If two agents propose conflicting changes (e.g., Database Schema modifications vs. API payload structure):
  1. The System Architect Agent acts as the final arbiter.
  2. If unresolved, the conflict is escalated to the Human User for design clarification.
