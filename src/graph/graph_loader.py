import re
from src.infrastructure.database.graph_client import graph_client


def normalize_entity_name(name: str) -> str:
    """Normalizes entity names: trims whitespace, converts to Title Case."""
    cleaned = name.strip()
    # Preserving acronyms if they are fully uppercase
    if cleaned.isupper() and len(cleaned) <= 5:
        return cleaned
    return cleaned.title()


def sanitize_predicate_label(predicate: str) -> str:
    """
    Sanitizes predicate strings to create valid Cypher relationship types:
    uppercase, converts spaces/hyphens/non-alphanumeric to underscores.
    Example: 'works at' -> 'WORKS_AT'
    """
    cleaned = predicate.strip().upper()
    # Replace non-alphanumeric characters with underscores
    sanitized = re.sub(r'[^A-Z0-9_]+', '_', cleaned)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    # Default fallback label if empty
    return sanitized if sanitized else "RELATED_TO"


async def load_chunk_and_triplets_to_graph(
    chunk_id: int,
    chunk_content: str,
    video_id: str,
    triplets: list
) -> None:
    """
    Performs a transaction to load a chunk and all its extracted triplets to Neo4j.
    Applies name normalization and predicate sanitization.
    """
    # Auto-initialize Neo4j uniqueness constraints
    await graph_client.init_constraints()

    async with graph_client.driver.session() as session:
        # 1. Merge the Chunk node first
        chunk_query = """
        MERGE (c:Chunk {id: $chunk_id})
        SET c.content = $chunk_content, c.video_id = $video_id, c.updated_at = timestamp()
        """
        await session.run(chunk_query, {
            "chunk_id": chunk_id,
            "chunk_content": chunk_content,
            "video_id": video_id
        })

        # 2. Merge each triplet and link to the Chunk node
        for triplet in triplets:
            subject = normalize_entity_name(triplet["subject"])
            obj = normalize_entity_name(triplet["object"])
            predicate_label = sanitize_predicate_label(triplet["predicate"])
            confidence = float(triplet.get("confidence", 1.0))

            # Dynamically inject the sanitized relationship label safely.
            # Parameterize the Subject, Object, Chunk reference, and confidence.
            triplet_query = f"""
            MATCH (c:Chunk {{id: $chunk_id}})
            MERGE (s:Entity {{name: $subject}})
            MERGE (o:Entity {{name: $object}})
            MERGE (c)-[:MENTIONS]->(s)
            MERGE (c)-[:MENTIONS]->(o)
            MERGE (s)-[r:{predicate_label}]->(o)
            ON CREATE SET r.confidence = $confidence, r.created_at = timestamp()
            ON MATCH SET r.confidence = $confidence
            """
            await session.run(triplet_query, {
                "chunk_id": chunk_id,
                "subject": subject,
                "object": obj,
                "confidence": confidence
            })
            
    print(f"Neo4j: Loaded chunk {chunk_id} and {len(triplets)} triplets to graph.")
