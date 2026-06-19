# Program Management & Sprint Planning: Brainy 1.0

This sprint schedule details Sprints 0 through 8, establishing tasks, timelines, effort estimates, and risks.

---

## Sprint 0: Project Foundation
- **Goal**: Initialize workspace, design standards, and compile operating systems.
- **Epics**: Workspace configuration, Architectural review.
- **Tasks**:
  1. Generate folder structure and static context files.
  2. Implement CI linting configurations.
- **Subtasks**:
  - Configure mypy, black, flake8 settings.
  - Setup `.github/workflows/ci.yml`.
- **Acceptance Criteria**: All template files written and CI pipeline passes.
- **KPIs**: $100\%$ documentation coverage.
- **Risks**: Out-of-sync agent workspace patterns. Mitigation: Set strict file path mappings.
- **Dependencies**: None.
- **Estimated Effort**: 3 Days.

---

## Sprint 1: Core Infrastructure
- **Goal**: Spin up dockerized databases, setup FastAPI server boilerplates.
- **Epics**: Local DB cluster, Web APIs.
- **Tasks**:
  1. Build Docker Compose configuration including PostgreSQL, Neo4j, Qdrant, RabbitMQ, and MinIO.
  2. Initialize FastAPI project with configuration managers.
- **Subtasks**:
  - Configure Alembic migrations for PostgreSQL.
  - Configure health check endpoints.
- **Acceptance Criteria**: Running `docker-compose up` spins up all 5 database/broker services and the API answers health queries.
- **KPIs**: Database connection latencies $\le 50\text{ms}$.
- **Risks**: Network configuration bugs on docker bridges.
- **Dependencies**: Sprint 0.
- **Estimated Effort**: 5 Days.

---

## Sprint 2: Ingestion Pipeline
- **Goal**: Connect YouTube extraction, audio streaming, and Whisper transcription workers.
- **Epics**: Queue handlers, Downloader, Transcription.
- **Tasks**:
  1. Build yt-dlp wrapper to download audio streams and pipe them directly to MinIO.
  2. Implement Whisper worker consuming from RabbitMQ.
- **Subtasks**:
  - Design transcription schema with word-level timestamps.
  - Setup MinIO storage buckets.
- **Acceptance Criteria**: Ingesting a YouTube URL yields a completed WAV file in MinIO and a transcription file with timestamps.
- **KPIs**: Transcription Word Error Rate (WER) $\le 8\%$.
- **Risks**: YouTube blocking yt-dlp traffic. Mitigation: Add proxy configuration settings.
- **Dependencies**: Sprint 1.
- **Estimated Effort**: 8 Days.

---

## Sprint 3: Knowledge Extraction
- **Goal**: Implement semantic chunking, embedding generation, and entity/relationship extraction.
- **Epics**: Natural Language Pipeline, Vector embeddings.
- **Tasks**:
  1. Implement Semantic Chunker dividing text on thematic transitions.
  2. Write extraction pipeline queries sending prompts to LLM APIs.
- **Subtasks**:
  - Configure OpenAI/Gemini API wrappers.
  - Set confidence scoring thresholds.
- **Acceptance Criteria**: A transcription paragraph is processed into chunks, embeddings, and a JSON array of Subject-Predicate-Object triplets.
- **KPIs**: Extraction Precision $\ge 88\%$.
- **Risks**: API rate limits. Mitigation: Add request rate limit throttling.
- **Dependencies**: Sprint 2.
- **Estimated Effort**: 7 Days.

---

## Sprint 4: Knowledge Graph
- **Goal**: Integrate Neo4j database loaders and validate the graph database schema.
- **Epics**: Graph Loading, Validation.
- **Tasks**:
  1. Implement Neo4j transactional loader executing parameterized Cypher queries.
  2. Write graph validation logic.
- **Subtasks**:
  - Setup entity deduplication rules.
  - Build indexes on entity nodes.
- **Acceptance Criteria**: Extracted triplets are successfully merged into Neo4j without duplicating node properties.
- **KPIs**: Write transactions per second $\ge 200$.
- **Risks**: Cypher queries causing lock contentions.
- **Dependencies**: Sprint 3.
- **Estimated Effort**: 6 Days.

---

## Sprint 5: GraphRAG
- **Goal**: Implement hybrid query retrievers and contextual answers citation engines.
- **Epics**: Hybrid Retrieval, Context Assembly.
- **Tasks**:
  1. Build retriever querying Qdrant for similar vectors and traversing Neo4j for neighbor nodes.
  2. Implement citation parser regex checker.
- **Subtasks**:
  - Integrate retrieval scoring math.
  - Add text-to-video timestamp mappings.
- **Acceptance Criteria**: Querying retrieves matching chunks, maps them to entities, and formats dense context for LLM with source timestamps.
- **KPIs**: Retrieval MRR $\ge 0.85$, latency $\le 300\text{ms}$.
- **Risks**: Hallucinations in citations.
- **Dependencies**: Sprint 4.
- **Estimated Effort**: 8 Days.

---

## Sprint 6: User Experience
- **Goal**: Deliver Web API endpoints for search and ingestion dashboard.
- **Epics**: API endpoints, User Interface.
- **Tasks**:
  1. Expose `/api/v1/ingest` and `/api/v1/search` REST endpoints.
  2. Develop a modern search/ingest dashboard.
- **Subtasks**:
  - Write Swagger schema files.
  - Setup query history caching.
- **Acceptance Criteria**: A client can request ingestion and run hybrid searches via standard API calls.
- **KPIs**: API Endpoint latency $\le 200\text{ms}$ (excluding LLM time).
- **Risks**: Missing API validation layers.
- **Dependencies**: Sprint 5.
- **Estimated Effort**: 7 Days.

---

## Sprint 7: Observability
- **Goal**: Implement OpenTelemetry tracing, Prometheus metrics, and Loki log collectors.
- **Epics**: Monitoring, Tracing.
- **Tasks**:
  1. Instrument FastAPI handlers with OpenTelemetry middleware.
  2. Setup Grafana dashboards for performance metrics.
- **Subtasks**:
  - Add trace context propagation to RabbitMQ message brokers.
  - Configure alerting thresholds.
- **Acceptance Criteria**: Running queries publishes telemetry traces visible in Grafana/Tempo UI showing detailed span times.
- **KPIs**: Telemetry overhead $\le 2\%$ CPU.
- **Risks**: Storage limits on trace volumes.
- **Dependencies**: Sprint 6.
- **Estimated Effort**: 5 Days.

---

## Sprint 8: Production Hardening
- **Goal**: Conduct security threat modeling, scale workers, and run chaos tests.
- **Epics**: Security, Performance tuning, Chaos testing.
- **Tasks**:
  1. Configure Kubernetes Horizontal Pod Autoscalers (HPA) for workers.
  2. Run chaos scripts terminating database container services during ingestion runs.
- **Subtasks**:
  - Configure CORS/security middleware.
  - Conduct vulnerability scans.
- **Acceptance Criteria**: Ingestion pipeline recovers gracefully after database restarts, and pipeline performance scales under load.
- **KPIs**: Job recovery rate $100\%$, system uptime $\ge 99.9\%$.
- **Risks**: Data corruption under sudden container termination.
- **Dependencies**: Sprint 7.
- **Estimated Effort**: 6 Days.
