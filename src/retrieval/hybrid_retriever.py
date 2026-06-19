from typing import Any, Dict

from src.infrastructure.ai.llm_client import llm_client
from src.infrastructure.database.graph_client import graph_client
from src.infrastructure.database.vector_client import vector_client


class HybridRetriever:
    async def retrieve(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Orchestrates hybrid retrieval:
        1. Decomposes query into sub-queries using LLM.
        2. Generates text embeddings and queries Qdrant for similar chunks, deduplicating them.
        3. Queries Neo4j using chunk IDs to retrieve 1-hop and 2-hop related entities and triplets.
        """
        # 1. Decompose query
        sub_queries = llm_client.decompose_query(query)

        # 2. Vector search in Qdrant for each sub-query
        vector_results_map = {}
        for sq in sub_queries:
            sq_embedding = llm_client.get_embedding(sq)
            sq_results = vector_client.search_chunks(sq_embedding, top_k=top_k)
            for res in sq_results:
                vector_results_map[res["chunk_id"]] = res

        # Sort combined results by score and slice to top_k
        vector_results = sorted(
            vector_results_map.values(), key=lambda x: x["score"], reverse=True
        )[:top_k]

        if not vector_results:
            return {"chunks": [], "entities": [], "relationships": []}

        # 3. Extract matching chunk IDs
        chunk_ids = [res["chunk_id"] for res in vector_results]

        # 4. Walk the Knowledge Graph in Neo4j up to 2-hops to find associated entities and facts
        cypher = """
        MATCH (c:Chunk)-[:MENTIONS]->(e:Entity)
        WHERE c.id IN $chunk_ids
        OPTIONAL MATCH (e)-[r:!MENTIONS]->(other:Entity)
        RETURN c.id as chunk_id, e.name as subject, type(r) as predicate, other.name as object
        UNION
        MATCH (c:Chunk)-[:MENTIONS]->(e:Entity)
        WHERE c.id IN $chunk_ids
        MATCH (e)-[r1:!MENTIONS]->(other1:Entity)-[r2:!MENTIONS]->(other2:Entity)
        RETURN c.id as chunk_id, other1.name as subject, type(r2) as predicate, other2.name as object
        """

        graph_results = await graph_client.run_query(cypher, {"chunk_ids": chunk_ids})

        # 5. Format and deduplicate Graph results
        entities = set()
        relationships = []

        for record in graph_results:
            if record["subject"]:
                entities.add(record["subject"])
            if record["object"]:
                entities.add(record["object"])

            # Only add relationship if it exists
            if record["predicate"] and record["object"]:
                rel = {
                    "subject": record["subject"],
                    "predicate": record["predicate"],
                    "object": record["object"],
                }
                if rel not in relationships:
                    relationships.append(rel)

        return {
            "chunks": vector_results,
            "entities": list(entities),
            "relationships": relationships,
        }


# Global hybrid retriever instance
hybrid_retriever = HybridRetriever()
