# Context Loading Strategy: Brainy 1.0

To prevent context window saturation and model confusion, agents must load context dynamically based on task scope.

## 1. Global Context (Always Loaded)
These files provide the core boundaries and must be included in the system instructions for every agent run:
- `.ai/instructions/INSTRUCTIONS.md` (Agent role and coding standards)
- `.ai/knowledge/PROJECT_OVERVIEW.md` (Vision and goals)
- `.ai/memory/SESSION_MEMORY.md` (Active session tracker)

## 2. Session Context (Loaded per Session)
- `.ai/memory/PROJECT_MEMORY.md` (Historical context & lessons learned)
- `.ai/architecture/TECH_STACK.md` (Libraries and infrastructure mapping)

## 3. Task Context (Loaded per Task)
- `task.md` (The active task list)
- Specific files directly touched or referenced by the current task.

## 4. Feature Context (Loaded per Feature implementation)
- Applicable Product Requirement Document (PRD) and System Requirement Specification (SRS) in `docs/` or `.ai/specifications/`.
- Corresponding test files under `tests/` to verify logic.

## 5. Architecture Context (Loaded during Reviews/ADRs)
- `.ai/architecture/ARCHITECTURE.md` (System structures)
- `.ai/decisions/ARCHITECTURE_DECISIONS.md` (Historical choices)
- Database schema layouts and model contracts.
