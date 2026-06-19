# QA & Testing Strategy

This document details the testing architecture, validation frameworks, metrics, and production monitoring strategies for Brainy 1.0.

---

## 1. The Testing Pyramid

```text
       /\
      /  \      End-to-End Tests (5%)
     /----\
    /      \    AI Evals & Performance (15%)
   /--------\
  /          \  Integration Tests (30%)
 /------------\
/              \ Unit Tests (50%)
----------------
```

### Unit Tests
- **Coverage Target**: $\ge 85\%$ line coverage across `src/` core services.
- **Tools**: `pytest`, `pytest-cov`, `unittest.mock`.
- **Strategy**: Mock all external service calls (e.g., MinIO Client, OpenAI API, and database connectors). Test business logic, chunking algorithms, data parsing routines, and Pydantic validation structures.

### Integration Tests
Verify communication interfaces and client execution loops against local databases.
- **PostgreSQL Tests**: Validate Alembic migration execution, raw transactional commits, and SQL query optimizations using an in-memory SQLlite driver or dockerized PostgreSQL test instance.
- **RabbitMQ Queue Tests**: Send test payloads and assert message delivery to consumers.
- **Neo4j Tests**: Execute test Cypher queries to verify node creation and relationship traversals.
- **Qdrant Tests**: Assert cosine similarities, payload-based metadata filters, and search recall.

### End-to-End (E2E) Tests
- **Video Ingestion Pipeline**: Feed a real/simulated YouTube URL and verify the raw WAV lands in MinIO, Whisper processes, and PostgreSQL registers the database status change to "completed".
- **Knowledge Extraction**: Verify that text outputs generate structured triplets matching reference ontologies.
- **Graph Generation**: Ensure nodes and relations match in Neo4j.
- **Query Answering**: Submit a request and verify that the system returns a valid, cited text response.

---

## 2. AI Evals
AI evaluations validate response quality and relevance.
- **Retrieval Evals**: Quantify retrieval Precision/Recall metrics using a golden query-context test dataset.
- **Response Grounding**: Use LLM-as-a-judge patterns to evaluate if the response stays faithful to the retrieved context.
- **Citation Precision**: Verify that all playback URL timestamps correspond to the actual context references.

---

## 3. Performance & Load Testing
- **Latency Targets**: API endpoint response time (P95) $\le 200\text{ms}$; hybrid search (P95) $\le 300\text{ms}$.
- **Throughput Bounds**: Pipeline capacity of 10 concurrent video transcription processes.
- **Tools**: `Locust` for web endpoint load testing; custom scripts for queue ingestion load metrics.

---

## 4. Security & Chaos Testing
- **Dependency Scanning**: Run `Trivy` and GitHub Dependabot checks on library modules.
- **Secrets Scanning**: Use git-secrets/TruffleHog patterns during CI pipelines to prevent credential leaks.
- **Chaos Testing**: Simulate failures:
  - Kill a running Whisper consumer worker thread midway through a download task and verify state recovery.
  - Temporarily pause Neo4j container connections and ensure API calls fail gracefully with appropriate error status codes.

---

## 5. Production Monitoring & SLAs

### SLIs and SLOs
- **Availability SLI**: Success rate of API requests (excluding client 4xx errors). **SLO Target**: $\ge 99.9\%$.
- **Latency SLI**: Request processing duration. **SLO Target**: P95 $\le 2.0\text{s}$ for search endpoints.
- **Ingestion SLI**: Duration of ingestion tasks. **SLO Target**: Total processing time $\le 0.5 \times \text{video duration}$.

### Alerting Strategy
Alert rules trigger pager notifications under the following conditions:
- API error rate exceeds $1.5\%$ over any 5-minute window.
- Ingestion queue backlogs exceed 100 unprocessed messages.
- Database connection pools exceed $90\%$ utilization.
