# Architecture Decisions: Brainy 1.0

This document contains the Architecture Decision Records (ADRs) for the Brainy 1.0 platform.

---

## ADR 001: Three-tier Database Architecture (SQL + Graph + Vector)

### Context
Brainy 1.0 needs to store three distinct forms of data:
1. Structured metadata (video lists, user profiles, download queues).
2. Connected network structures (entities, facts, cross-video connections).
3. Dense vector embeddings (semantic chunks, entity descriptions).

### Decision
We will employ a three-tier database strategy:
1. **PostgreSQL** for relational metadata and transactional operations.
2. **Neo4j** for graph connections and topological traversals.
3. **Qdrant** for vector storing and semantic search.

### Consequences
- **Pros**: Matches storage engines to the physical structure of the data, maximizing query efficiency and search flexibility.
- **Cons**: Requires keeping three separate data systems in sync during ingestion. Requires complex transaction orchestration.

---

## ADR 002: RabbitMQ for Pipeline Asynchrony

### Context
Processing YouTube videos requires downloading files, generating transcriptions with Whisper, and extracting entities via LLMs. These tasks are slow, resource-heavy, and prone to failures.

### Decision
We will use **RabbitMQ** as a message broker to queue tasks and decouple the web API from background ingestion workers.

### Consequences
- **Pros**: Isolates long-running CPU/GPU processes. Supports retries, dead-letter exchanges (DLX), and horizontal scaling.
- **Cons**: Adds operational overhead and requires handling distributed state sync.
