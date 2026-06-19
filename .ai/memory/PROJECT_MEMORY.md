# Project Memory: Brainy 1.0

This file records the evolutionary path of Brainy 1.0, tracking core decisions, history, and learnings.

## Project Origin & Core Mission
Brainy 1.0 was conceived as an antidote to information overload in online video courses, technical conferences, and tutorials. Traditional search parses transcripts linearly; Brainy aims to build a conceptual web where cross-video, multi-hop ideas are mapped to a queryable graph database.

## Critical Decisions Log
1. **The DB Triad (Relational + Graph + Vector)**:
   - *PostgreSQL* for reliable metadata storage, transactions, and system configuration.
   - *Neo4j* for relational graph reasoning, Cypher traversals, and GraphRAG.
   - *Qdrant* for fast semantic matches, vector indexing, and payload filters.
   - *Tradeoff*: Increases infrastructure complexity, but guarantees highly structured, semantic, and explainable retrieval.

2. **Event-Driven Ingestion Queue (RabbitMQ)**:
   - Selected over simple API polling to handle high-latency processes like Whisper transcription and heavy LLM extraction pipeline runs.

3. **OpenTelemetry for Observability**:
   - Chosen early to enable tracing of request life cycles spanning multiple API endpoints, RabbitMQ queues, and LLM processing jobs.

## Core Lessons Learned
- *To be populated as implementation proceeds and tests are executed.*
