# Technical Requirements & Credential Management Architecture

This document evaluates the hardware feasibility, local container footprints, credential management models, free-tier cloud hostings, and scaling cost dynamics for Brainy 1.0 under realistic student/MVP resource constraints.

---

## Part 1: Hardware Feasibility Analysis

### Development Machine Constraints
- **RAM**: 16 GB
- **GPU**: NVIDIA RTX 3050 Laptop (6 GB VRAM)
- **CPU**: Laptop-class (e.g., 6-core/12-thread AMD Ryzen 5 or Intel Core i5)
- **Storage**: SSD (Sufficient disk speed, but space constrained)

### Estimated Resource Footprint (Simultaneous Docker Run)

| Service | CPU Usage (Idle/Load) | RAM Footprint | VRAM Footprint | Run Mode |
| :--- | :--- | :--- | :--- | :--- |
| **FastAPI** | 1% / 15% | 150 MB | 0 MB | Docker |
| **PostgreSQL** | 1% / 10% | 100 MB | 0 MB | Docker |
| **Neo4j** | 2% / 25% | 1.5 GB | 0 MB | Docker (JVM heap tuned) |
| **Qdrant** | 1% / 20% | 300 MB | 0 MB | Docker (In-memory index) |
| **RabbitMQ** | 1% / 5% | 200 MB | 0 MB | Docker |
| **MinIO** | 1% / 10% | 150 MB | 0 MB | Docker |
| **Ollama (Llama3-8B)** | 5% / 100% | 4.8 GB | 4.5 GB | Native (GPU accelerated) |
| **Whisper (base/small)** | 5% / 100% | 1.5 GB | 1.2 GB | Native (GPU accelerated) |
| **Total (Running All)** | **~17% / ~280%** | **~8.7 GB** | **5.7 GB / 6 GB** | **CRITICAL CAPACITY** |

### Key Bottlenecks Identified
1. **RAM Limits (16 GB Host)**: With Docker running the base database suite (~2.4 GB) and host OS/Web browser taking ~6 GB, launching Ollama (4.8 GB) and Whisper (1.5 GB) simultaneously will push the system into swap storage, degrading SSD lifespan and CPU performance.
2. **VRAM Exhaustion (6 GB VRAM)**: Ollama (Llama-3-8B takes ~4.5 GB) and Whisper-small (~1.2 GB) cannot sit in VRAM concurrently. Launching a transcription while running an extraction will cause out-of-memory (OOM) errors or context offloading to CPU, which slows processing speed by $10\times$.

### Recommendations for Local Setup
- **Do not run Ollama and Whisper concurrently on GPU**: Set up the worker pipeline to run sequentially (transcribe first, write to MinIO, release Whisper memory, then load LLM for extraction).
- **Limit Neo4j and JVM heap allocations**: Set `dbms.memory.heap.initial_size=512m` and `dbms.memory.heap.max_size=1g` in Docker environment variables.

---

## Part 2: Local Development Stack (Docker Compose)

We recommend running database layers in Docker, while CPU/GPU-intensive modeling engines (Ollama and Whisper) run native or utilize specialized API integrations.

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: brainy_postgres
    environment:
      POSTGRES_DB: brainy_db
      POSTGRES_USER: brainy_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 256M

  neo4j:
    image: neo4j:5.12-community
    container_name: brainy_neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_dbms_memory_heap_initial__size: 256m
      NEO4J_dbms_memory_heap_max__size: 512m
      NEO4J_dbms_memory_pagecache_size: 256m
    volumes:
      - neo4j_data:/data
    deploy:
      resources:
        limits:
          memory: 1.2G

  qdrant:
    image: qdrant/qdrant:latest
    container_name: brainy_qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    deploy:
      resources:
        limits:
          memory: 512M

  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: brainy_rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    deploy:
      resources:
        limits:
          memory: 256M

  minio:
    image: minio/minio:RELEASE.2023-10-25T06-33-25Z
    container_name: brainy_minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minio_admin
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    deploy:
      resources:
        limits:
          memory: 256M

volumes:
  pg_data:
  neo4j_data:
  qdrant_data:
  minio_data:
```

---

## Part 3: Credential Management Analysis

| Option | Pros | Cons | Security Risk | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **Env Variables (`.env`)** | Simplest, native integration, zero compute footprint | Hard to share across teams, prone to git leakage | High if committed | **Dev Stage** |
| **Docker Secrets** | Restricts secrets to runtime containers | Hard to manage outside Swarm/K8s environments | Low | **MVP Stage** |
| **HashiCorp Vault** | Industry standard, encryption-as-a-service | Resource-heavy (~500MB RAM), high setup complexity | Very Low | **Enterprise Stage** |
| **Infisical (Free)** | Excellent developer dashboard, CLI integrations | Self-hosting requires postgres instance setup | Low | **MVP Stage (Alternative)** |
| **Doppler (Free)** | Zero infrastructure setup, excellent CLI bindings | Free tier limited to 5 users/projects | Low | **Production Stage** |
| **AWS Secrets Manager**| Managed, secure IAM integration | Expensive ($0.40/secret/month + API call fees) | Low | **Enterprise (AWS Deploy)** |

### Recommendation by Lifecycle Stage
- **Development**: Decoupled `.env` files parsed using `pydantic-settings`.
- **MVP (Self-hosted)**: Infisical (Self-hosted on Render/fly.io) or Docker Secrets.
- **Production**: Doppler (Cloud Managed Free Tier).

---

## Part 4: Cloud Deployment Analysis (Free Tier Providers)

- **Render**: Free tier offers Web Services (auto-spins down after 15m inactivity). PostgreSQL database free for 90 days. Ideal for initial FastAPI MVP testing but lacks persistent databases.
- **Railway**: Provides $5.00/month free credits. Excellent Docker support. PostgreSQL setup is simple. However, usage-based caps run out quickly under heavy background worker load.
- **Fly.io**: Free tier includes 3 micro-VMs (256MB RAM each), 3GB volume storage. Perfect for lightweight FastAPI + SQLite/Postgres setups. Lacks resources to run Neo4j or heavy queue brokers.
- **Koyeb**: Free tier offers two nano instances (512MB RAM). Excellent container deployments with native edge routing. Great for hosting the FastAPI server.
- **Oracle Cloud Free Tier**: **The Gold Standard for MVPs**. Provides up to 4 Ampere A1 Compute instances with up to 24 GB RAM and 200 GB block volume storage total. Lacks GPU access, but easily hosts PostgreSQL, Neo4j, Qdrant, and RabbitMQ within Docker on a single VM.
- **AWS / GCP / Azure Free Tiers**: Provide 12 months of micro instances (e.g., AWS t2.micro, 1GB RAM) which are too small to host Neo4j or memory-dense Java systems.

---

## Part 5: Infrastructure Mapping Strategy

```mermaid
graph TD
    subgraph Development (Local Laptop)
        FastAPI_Dev[FastAPI]
        Whisper_Dev[Native Whisper GPU]
        Ollama_Dev[Native Ollama GPU]
        DBs_Dev[Docker DBs: PG/Neo4j/Qdrant/RMQ]
    end
    
    subgraph MVP (Free-Tier Cloud)
        FastAPI_MVP[FastAPI on Koyeb/Fly.io]
        DBs_MVP[Oracle Cloud A1 VM: Dockerized PG/Neo4j/Qdrant/RMQ]
        API_Models[HuggingFace / Groq APIs / OpenAI]
    end
```

### Resource Placements

| Service | Development Placement | MVP Cloud Placement | Production Placement |
| :--- | :--- | :--- | :--- |
| **FastAPI** | Local Docker | Koyeb / Fly.io (512MB VM) | AWS ECS Fargate |
| **Neo4j** | Local Docker (tuned limits) | Oracle Cloud A1 (4GB RAM Docker) | Neo4j AuraDB (Managed) |
| **Qdrant** | Local Docker | Oracle Cloud A1 (2GB RAM Docker) | Qdrant Cloud (Managed) |
| **PostgreSQL** | Local Docker | Oracle Cloud A1 (1GB RAM Docker) | Supabase / AWS RDS |
| **RabbitMQ** | Local Docker | Oracle Cloud A1 (512MB Docker) | CloudAMQP (Free tier) |
| **MinIO / S3** | Local Docker | Cloudflare R2 (10GB Free Tier) | AWS S3 |
| **Whisper** | Native Local GPU | RunPod Serverless (pay-per-sec) | AWS ECS GPU Workers |
| **LLM (Ollama)** | Native Local GPU | Groq / Gemini Free Tier API | OpenAI / Azure OpenAI |

---

## Part 6: Open-Source Alternatives Mapping

- **Credential Management**: Infisical (Self-hosted) or Doppler (Cloud Free).
- **Monitoring & Logging**: Prometheus + Grafana (Self-hosted on Docker).
- **Tracing**: Jaeger (Docker-friendly, lightweight alternative to Tempo).
- **Queueing**: RabbitMQ (standard) or Celery + Redis (lowest RAM footprint).
- **Object Storage**: MinIO (development) -> Cloudflare R2 (S3-compatible, no egress fees).
- **Authentication**: SuperTokens (Self-hosted) or Clerk (Free tier).

---

## Part 7: Cost Analysis

| Phase | Estimated Active Users | Key Cost Drivers | Monthly Cost |
| :--- | :--- | :--- | :--- |
| **Development** | 1 (Developer) | Laptop electricity | **$0.00** |
| **MVP** | 1–10 | Free-tier hostings + OpenAI API tokens ($2.00) | **~$2.00** |
| **100 Users** | 100 | RunPod Whisper API ($10), Gemini API ($15), DB hosts | **~$35.00** |
| **1,000 Users** | 1,000 | Managed Vector/Graph DBs, AWS ECS runtime, LLM | **~$450.00** |
| **10,000 Users** | 10,000 | Multi-region scaling, large GPU instances, high DB operations | **~$4,200.00** |

---

## Part 8: Final Recommendations & Design Adjustments

1. **Memory Budgeting**: Developers must configure container memory limits on their development laptops. Set strict limits on Docker Compose components to save RAM.
2. **API Offloading in MVP**: Avoid self-hosting Whisper and LLMs on cloud instances. Use Groq/Gemini API keys (offering free tiers) for entity extraction, and run Whisper locally or using Serverless GPU endpoints.
3. **Storage Egress Avoidance**: Use Cloudflare R2 instead of AWS S3 for audio/video storage to prevent egress transfer costs.
4. **Credential Decoupling**: Use standard `.env` configuration files parsed through Pydantic Settings. Do not commit credentials to source code.
