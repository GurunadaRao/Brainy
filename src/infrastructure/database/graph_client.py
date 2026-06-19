from typing import Any
from neo4j import AsyncGraphDatabase
from src.configs.settings import settings


class GraphClient:
    def __init__(self) -> None:
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    async def close(self) -> None:
        """Close the Neo4j driver connection."""
        await self.driver.close()

    async def init_constraints(self) -> None:
        """Initialize Neo4j uniqueness constraints for fast merges and consistency."""
        queries = [
            "CREATE CONSTRAINT unique_entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE",
            "CREATE CONSTRAINT unique_chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE"
        ]
        
        async with self.driver.session() as session:
            for q in queries:
                try:
                    await session.run(q)
                    print(f"Neo4j: Executed schema query: {q}")
                except Exception as e:
                    print(f"Neo4j: Constraint setup failed for query '{q}': {e}")

    async def run_query(self, query: str, parameters: dict = None) -> Any:
        """Run a parameterized Cypher query and return the result."""
        async with self.driver.session() as session:
            result = await session.run(query, parameters or {})
            return await result.data()


# Global graph client instance
graph_client = GraphClient()
