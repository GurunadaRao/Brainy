from src.infrastructure.database.graph_client import graph_client


async def get_graph_summary() -> dict:
    """Retrieves count metrics for nodes, labels, and relationships in the Neo4j database."""
    summary = {
        "total_nodes": 0,
        "entity_nodes": 0,
        "chunk_nodes": 0,
        "relationships": 0,
        "orphan_entities": 0,
        "disconnected_chunks": 0
    }
    
    try:
        # 1. Total Nodes
        res = await graph_client.run_query("MATCH (n) RETURN count(n) as count")
        summary["total_nodes"] = res[0]["count"] if res else 0
        
        # 2. Entity Nodes
        res = await graph_client.run_query("MATCH (e:Entity) RETURN count(e) as count")
        summary["entity_nodes"] = res[0]["count"] if res else 0
        
        # 3. Chunk Nodes
        res = await graph_client.run_query("MATCH (c:Chunk) RETURN count(c) as count")
        summary["chunk_nodes"] = res[0]["count"] if res else 0
        
        # 4. Relationships
        res = await graph_client.run_query("MATCH ()-[r]->() RETURN count(r) as count")
        summary["relationships"] = res[0]["count"] if res else 0
        
        # 5. Orphan Entities (no connections whatsoever)
        res = await graph_client.run_query("MATCH (e:Entity) WHERE NOT (e)-[]-() RETURN count(e) as count")
        summary["orphan_entities"] = res[0]["count"] if res else 0
        
        # 6. Disconnected Chunks (chunks that do not mention any entity)
        res = await graph_client.run_query("MATCH (c:Chunk) WHERE NOT (c)-[:MENTIONS]->(:Entity) RETURN count(c) as count")
        summary["disconnected_chunks"] = res[0]["count"] if res else 0
        
    except Exception as e:
        print(f"GraphValidation: Error gathering metrics: {e}")
        
    return summary


async def print_graph_report() -> None:
    """Logs a clean human-readable text report of the Neo4j schema stats."""
    metrics = await get_graph_summary()
    print("\n" + "="*40)
    print("      NEO4J GRAPH VALIDATION REPORT")
    print("="*40)
    print(f"Total Nodes:            {metrics['total_nodes']}")
    print(f"  - Entity Nodes:       {metrics['entity_nodes']}")
    print(f"  - Chunk Nodes:        {metrics['chunk_nodes']}")
    print(f"Total Relationships:    {metrics['relationships']}")
    print("-"*40)
    print(f"Orphan Entities:        {metrics['orphan_entities']}")
    print(f"Disconnected Chunks:    {metrics['disconnected_chunks']}")
    print("="*40 + "\n")
