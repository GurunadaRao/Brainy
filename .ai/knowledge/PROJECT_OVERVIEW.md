# Project Overview: Brainy 1.0

## Product Vision
Brainy 1.0 is an AI-powered Video Intelligence, Knowledge Graph, and Research Platform. The system ingests YouTube videos, playlists, and channels and converts unstructured video content into structured, interconnected knowledge.

The goal is **not** transcript search. The goal is to build a living knowledge graph capable of:
- Deep knowledge extraction
- Semantic and Graph retrieval (GraphRAG)
- Cross-video multi-hop reasoning
- Explainable AI responses with source citations
- Autonomous research assistance

Brainy 1.0 transforms hours of video content into instantly queryable, structured knowledge.

## Problem Statement
Today's video content (lectures, tutorials, podcasts, documentation videos) is highly dense but difficult to search and synthesize. Users must:
1. Watch entire videos to extract relevant insights.
2. Manually take notes and track context.
3. Remember concepts and manually connect ideas across multiple different videos.
4. Deal with transcripts that lack structural connections or semantic continuity.

Knowledge remains trapped inside video timelines. Brainy 1.0 unlocks that knowledge by transforming videos into structured entities, relationships, concepts, and facts.

## High-Level Goals
- **Ingestion & Processing**: Seamlessly ingest and transcribe videos, cleaning transcripts for structured chunking.
- **Entity & Relation Extraction**: Automatically identify entities, concepts, relationships, and facts, mapping them to a unified schema.
- **Interconnected Graph building**: Construct a Knowledge Graph combining structural links (Neo4j) with vector representations (Qdrant) and relational metadata (PostgreSQL).
- **Explainable GraphRAG**: Empower users to query the platform and receive answers that merge vector similarities and graph-traversal context, fully referenced and cited back to video timestamps.

## Target Users
- **Researchers & Academics**: Seeking to synthesize long lectures, research talks, and seminars.
- **Developers & Engineers**: Looking to quickly extract insights from tech tutorials, conferences, and system walkthroughs.
- **Content Creators & Educators**: Analyzing trends, structuring course curricula, and cross-referencing information.

## Success Metrics
- **Extraction Accuracy**: Precision and recall of extracted entities and relationships compared to human-verified baselines.
- **Retrieval Performance**: Query latency under 2 seconds for hybrid GraphRAG queries.
- **Answer Quality**: Minimization of hallucinations, measured via context relevance and citation accuracy.
- **Ingestion Throughput**: Parallel processing of videos with predictable queue times.
