# Domain Knowledge: GraphRAG & Video Intelligence

## 1. GraphRAG (Graph-based Retrieval Augmented Generation)
GraphRAG combines the semantic search capabilities of Vector Databases with the structured relationship logic of Knowledge Graphs.

### Key Patterns:
- **Vector-to-Graph Jump**: Retrieval starts by finding semantically similar text chunks or entity descriptions in Qdrant. The retrieved nodes act as entry points into the Neo4j graph, traversing outbound relationships to fetch contextual neighbor facts.
- **Global vs. Local Search**:
  - *Local Search*: Focuses on specific entities mentioned in the query, retrieving direct neighbors and related chunks.
  - *Global Search*: Uses pre-computed community summaries of the graph to answer high-level questions across the entire dataset (e.g., *"What are the recurring themes across all videos?"*).
- **Sub-graph Extraction**: Building runtime sub-graphs of relevant nodes/edges, converting them into structured text representations for LLM reasoning.

## 2. Neo4j Modeling for Video Intelligence
We model video content as a graph to preserve narrative and factual connections.

### Graph Schema Strategy:
- **Video Node**: Represents the source video. Attributes: `id`, `title`, `duration`, `published_at`, `channel`.
- **Chunk Node**: Represents a contiguous semantic segment of the transcript. Attributes: `id`, `text`, `start_time`, `end_time`. Linked via `PART_OF_VIDEO` to the Video, and `NEXT_CHUNK` to sequentially adjacent chunks.
- **Entity Node**: Represents extracted concepts, people, places, or technologies. Attributes: `id` (slugified name), `name`, `type` (e.g., `Technology`, `Person`, `Concept`), `description`.
- **Relationships**:
  - `(Chunk)-[MENTIONS]->(Entity)`
  - `(Entity)-[RELATION {type: "USED_FOR", context: "..."}]->(Entity)`

## 3. Qdrant Vector Databases
Vector databases are used to store and retrieve dense vector representations.
- **Payload Indexing**: Filter queries dynamically using payload keys (e.g., filter chunks belonging only to a specific video or channel).
- **Embedding Models**: Use high-quality embedding models (e.g., text-embedding-3-small or similar) with 1536 dimensions.

## 4. YouTube Ingestion & Transcription (Whisper)
- **Audio Pre-processing**: High-bitrate audio downloads, converted to mono 16kHz WAV format (optimal for Whisper).
- **Whisper Alignment**: Whisper output must include word-level timestamps to map semantic chunks back to specific video playback ranges.
- **Transcript Cleaning**: Remove filler words, correct technical jargon using customized dictionaries, and segment paragraphs dynamically based on pause durations.
