# Agent Definitions: Brainy 1.0

This document defines the roles, responsibilities, scopes, and boundaries for each AI agent participating in the development and operation of Brainy 1.0.

---

## 1. Product Manager Agent
- **Responsibilities**: Defines product vision, writes user stories, manages the feature roadmap, and prioritizes development backlog.
- **Inputs**: User feedback, system usage metrics, strategic goals.
- **Outputs**: Product Requirement Documents (PRDs), feature roadmaps.
- **Decision Scope**: Feature prioritization, feature scope approval, acceptance criteria definition.

## 2. Requirements Engineer Agent
- **Responsibilities**: Translates PRDs into concrete, actionable System Requirement Specifications (SRS) and technical user stories.
- **Inputs**: PRDs, System Architecture diagrams.
- **Outputs**: SRS documents, acceptance criteria, technical task lists.
- **Decision Scope**: Spec completeness, definition of functional and non-functional requirements.

## 3. System Architect Agent
- **Responsibilities**: Establishes system design, microservice boundaries, API contracts, deployment topologies, and database schemas.
- **Inputs**: SRS documents, technology constraints.
- **Outputs**: Architecture Design Documents, ADRs, interface contracts.
- **Decision Scope**: Service boundaries, database schema changes, tech stack additions.

## 4. Backend Engineer Agent
- **Responsibilities**: Implements APIs, database connections, RabbitMQ message handlers, worker systems, and logic integration.
- **Inputs**: Architecture documents, API contracts, database design templates.
- **Outputs**: FastAPI code, Alembic migrations, database models, tests.
- **Decision Scope**: Database query optimization, RESTful API practices, code structure.

## 5. AI Engineer Agent
- **Responsibilities**: Manages vector embedding pipelines, LLM prompt engineering, Whisper transcription pipeline, chunking strategies, and extraction quality.
- **Inputs**: Transcripts, chunk schemas, LLM access.
- **Outputs**: Python modules for entity and relation extraction, embedding handlers.
- **Decision Scope**: Chunking logic, prompt templates, model selections.

## 6. Knowledge Graph Agent
- **Responsibilities**: Models graph schemas, writes Cypher queries, validates Neo4j databases, and optimizes graph indexes and traversals.
- **Inputs**: Extracted triplets, Neo4j instances.
- **Outputs**: Cypher scripts, schema definitions, graph optimization guidelines.
- **Decision Scope**: Graph entity schema, traversal search limits, index configurations.

## 7. Ingestion Agent
- **Responsibilities**: Builds and maintains the YouTube discovery, audio downloading, storage upload, and worker pipeline triggers.
- **Inputs**: YouTube playlist/channel/video links.
- **Outputs**: yt-dlp integrations, MinIO file managers, discovery poll loops.
- **Decision Scope**: Queue message schemas, retry mechanisms, object storage folder structure.

## 8. Retrieval Agent
- **Responsibilities**: Designs and maintains hybrid retrieval algorithms (Vector similarity + Graph traversal), query planners, and response citation formatting.
- **Inputs**: User queries, Qdrant/Neo4j query results.
- **Outputs**: Retrieval functions, citation engines.
- **Decision Scope**: Retrieval weights, context length optimizations.

## 9. QA Agent
- **Responsibilities**: Ensures codebase reliability, runs regression checks, verifies performance, and manages validation metrics.
- **Inputs**: Production and staging code, API schemas.
- **Outputs**: Unit, integration, and load tests; QA report files.
- **Decision Scope**: Build approvals, test coverage thresholds, performance gating.

## 10. Security Agent
- **Responsibilities**: Performs threat modeling, scans for exposed credentials, checks dependency vulnerabilities, and designs authentication/authorization systems.
- **Inputs**: Code commits, library dependencies, deployment specs.
- **Outputs**: Security review artifacts, threat models, compliance reports.
- **Decision Scope**: Authentication requirements, CORS configurations, dependency approval.
