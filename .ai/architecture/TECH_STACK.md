# Technology Stack Specification: Brainy 1.0

## Backend Framework
- **FastAPI**: Core Python web framework for performance, asynchronous execution, and automatic OpenAPI schema generation.
- **Pydantic v2**: Data validation and configuration management.
- **SQLAlchemy (Async)**: Object-Relational Mapper (ORM) for PostgreSQL interaction.

## Databases & Vectors
- **PostgreSQL**: Relational database for transactions, users, jobs/tasks tracking, and video metadata.
- **Neo4j**: Graph database for storing entity-relation-entity triplets and running Cypher-based GraphRAG traversals.
- **Qdrant**: Vector database for high-dimensional semantic search and payload-based filtering.

## Queue & Communication
- **RabbitMQ**: Message broker managing the asynchronous ingestion pipeline (discovery, download, transcribe, extract, load).
- **Celery / Custom Async Workers**: For consumption and execution of long-running video ingestion tasks.

## Object Storage
- **MinIO**: S3-compatible object storage for saving raw audio tracks, transcripts, and model checkpoints.

## Observability & Monitoring
- **OpenTelemetry**: Standardized instrumentation for generating distributed traces.
- **Grafana**: Main metrics and visualization dashboard.
- **Loki**: Log aggregation platform integrated with Grafana.
- **Tempo**: Distributed tracing backend to profile performance bottlenecks across the ingestion queue.

## Infrastructure & Deployment
- **Docker & Docker Compose**: For local development and system orchestration.
- **Kubernetes**: Production deployment target, using Helm charts for scaling worker instances based on RabbitMQ queue depth.
