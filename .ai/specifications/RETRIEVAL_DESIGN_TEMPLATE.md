# Retrieval Design Template

## 1. Query Interpretation
- Input parsing and semantic classification.
- Entity extraction from query text.

## 2. Multi-Hop Logic
Define how the retriever traverses Neo4j:
- **Hop 1**: Search nearest vectors in Qdrant.
- **Hop 2**: Fetch adjacent nodes in Neo4j within range $R$.

## 3. Reranking & Context Assembly
- Formula for combining vector score and graph density.
- Max context token limits.
