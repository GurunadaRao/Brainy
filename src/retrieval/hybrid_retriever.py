from typing import List, Dict, Any
from src.infrastructure.ai.llm_client import llm_client
from src.infrastructure.database.vector_client import vector_client
from src.infrastructure.database.graph_client import graph_client


class HybridRetriever:
    async def retrieve(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Orchestrates hybrid retrieval:
        1. Generates text embedding for the search query via local Ollama.
        2. Queries Qdrant to find the top-K similar transcript chunks.
        3. Queries Neo4j using chunk IDs to retrieve related entities and triplets.
        """
        # 1. Generate query embedding
        query_embedding = llm_client.get_embedding(query)

        # 2. Vector search in Qdrant
        vector_results = vector_client.search_chunks(query_embedding, top_k=top_k)
        if not vector_results:
            return {
                "chunks": [],
                "entities": [],
                "relationships": []
            }

        # 3. Extract matching chunk IDs
        chunk_ids = [res["chunk_id"] for res in vector_results]

        # 4. Walk the Knowledge Graph in Neo4j to find associated entities and facts
        cypher = """
        MATCH (c:Chunk)-[:MENTIONS]->(e:Entity)
        WHERE c.id IN $chunk_ids
        OPTIONAL MATCH (e)-[r]->(other:Entity)
        RETURN c.id as chunk_id, e.name as subject, type(r) as predicate, other.name as object
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
                    "object": record["object"]
                }
                if rel not in relationships:
                    relationships.append(rel)

        return {
            "chunks": vector_results,
            "entities": list(entities),
            "relationships": relationships
        }


# Global hybrid retriever instance
hybrid_retriever = HybridRetriever()
