# Workflow Definitions: Brainy 1.0

This document defines the key workflows driving development and runtime features.

---

## 1. Requirement Workflow

```mermaid
graph LR
    Idea[Idea / Feature Request] --> PRD[Product Requirement Document]
    PRD --> SRS[System Requirement Specification]
    SRS --> Stories[User Stories & Acceptance Criteria]
    Stories --> Architecture[Architecture Design & Review]
```

1. **Idea / Feature Request**: Initiated by Product Manager Agent or human requests.
2. **PRD Creation**: PM Agent drafts product requirements.
3. **SRS Generation**: Requirements Engineer parses PRD and creates exact specifications.
4. **User Stories & Acceptance Criteria**: Written to guide QA and engineering tasks.
5. **Architecture Review**: System Architect validates changes against existing system designs.

---

## 2. Ingestion Workflow

```mermaid
graph TD
    A[YouTube URL] --> B[Discovery Service]
    B --> C[Download Service: yt-dlp]
    C --> D[MinIO Object Storage]
    C --> E[Whisper Transcription]
    E --> F[Transcript Cleaning & Chunking]
    F --> G[Embedding Generation]
    G --> H[Entity & Relation Extraction]
    H --> I[(Write: PostgreSQL, Neo4j, Qdrant)]
```

1. **Discovery**: Channel, playlist, or video is checked, resolving metadata.
2. **Download**: Downloader worker downloads high-quality audio streams.
3. **Whisper Transcription**: Converts raw audio to formatted text with word-level timestamps.
4. **Cleaning & Chunking**: Paragraph formatting, word correction, and semantic chunking.
5. **Embeddings**: Vector embeddings generated for chunks and entities.
6. **Extraction**: LLM extracts entities and relations, compiling triplets.
7. **Storage**: Write operations commit metadata to PostgreSQL, relations to Neo4j, and vectors to Qdrant.

---

## 3. Query Workflow

```mermaid
graph TD
    Query[User Query] --> Planner[Query Planner]
    Planner --> Vector[Vector similarity in Qdrant]
    Planner --> Graph[Graph traversal in Neo4j]
    Vector --> Context[Context Aggregator]
    Graph --> Context
    Context --> LLM[LLM Generator]
    LLM --> Citation[Citation Engine]
    Citation --> Response[Cited Response + Timestamps]
```

1. **Query Planner**: Determines search pathways (local vs. global).
2. **Hybrid Search**: Concurrent execution of vector semantic searches and graph hop queries.
3. **Context Aggregator**: Collects matching transcript chunks and entity network contexts.
4. **LLM Generation**: Processes context to yield accurate responses.
5. **Citation Engine**: Appends playback links and timestamp metadata to the answer.

---

## 4. Development Workflow

```mermaid
graph LR
    Task[Task Assignment] --> Design[Technical Design]
    Design --> Code[Implementation]
    Code --> Test[Testing & Linting]
    Test --> Review[Peer Review & Approval]
    Review --> Deploy[Deployment]
```

1. **Task**: Pulled from `task.md` or backlog.
2. **Design**: Establish interface contracts or database changes.
3. **Implementation**: Code components according to PEP 8 standards.
4. **Testing**: Run unit and integration tests.
5. **Review**: Ensure compliance with code rules and architectural standards.
6. **Deployment**: Release builds to production/staging.
