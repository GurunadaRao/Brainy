# Architecture Review Template

- **Review Target**: [Component/Service Name]
- **Reviewer**: System Architect Agent
- **Date**: [YYYY-MM-DD]

## 1. Architectural Alignment
Does the target align with the high-level architecture specified in `ARCHITECTURE.md` and `TECH_STACK.md`?

## 2. Scale & Bottlenecks
- Max throughput evaluation.
- Database locking or performance overhead.
- Queue backlog handling.

## 3. Boundary Integration
- Validation of API inputs/outputs.
- Exception handling strategy across bounds.

## 4. Status
- [ ] Approved
- [ ] Needs Revision (list action items below)
