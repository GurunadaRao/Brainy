# Database Design Template

- **Database**: [PostgreSQL / Qdrant]
- **Target Schema/Collection**: [Schema Name]

## 1. Tables & Fields (PostgreSQL)
Describe table layout, fields, and constraints.
- **Table Name**: `videos`
  - `id`: UUID (Primary Key)
  - `youtube_id`: VARCHAR(50) (Unique, Indexed)
  - `title`: VARCHAR(255)
  - `created_at`: TIMESTAMP

## 2. Collections & Payloads (Qdrant)
- **Collection Name**: `video_chunks`
- **Vector Dimension**: 1536 (Cosine Similarity)
- **Payload Schema**:
  - `chunk_id`: UUID
  - `video_id`: UUID
  - `text`: string
  - `start_time`: float
