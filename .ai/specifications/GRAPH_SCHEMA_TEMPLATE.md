# Graph Schema Design Template

## 1. Node Labels
Define all node types, their properties, and indexing needs.
- **Label**: `Entity`
  - `name`: String (Unique, Indexed)
  - `type`: String
  - `description`: String

## 2. Relationship Types
Define properties, directionality, and cardinality.
- **Type**: `MENTIONS`
  - **Source**: `Chunk`
  - **Target**: `Entity`
  - **Properties**: `confidence: Float`
