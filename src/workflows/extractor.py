import asyncio
from typing import List, Dict, Any
from sqlalchemy import select
from src.domain.models import Video, Transcription, Chunk, Triplet
from src.infrastructure.database.session import AsyncSessionLocal, with_retry
from src.ingestion.chunker import semantic_chunk_text
from src.infrastructure.ai.llm_client import llm_client


@with_retry()
async def process_video_extraction(video_id: str, confidence_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Orchestrates the Knowledge Extraction pipeline for a transcribed video:
    1. Fetches transcription text from the database.
    2. Runs semantic chunking on the text.
    3. Generates sentence/chunk embeddings using local nomic-embed-text.
    4. Extracts Subject-Predicate-Object triplets via LLMs (Ollama / OpenAI).
    5. Saves chunks, embeddings, and high-confidence triplets to PostgreSQL.
    """
    print(f"Extractor: Starting knowledge extraction for video {video_id}...")
    
    # 1. Fetch transcription
    async with AsyncSessionLocal() as session:
        stmt = select(Transcription).where(Transcription.video_id == video_id)
        result = await session.execute(stmt)
        transcriptions = result.scalars().all()
        
        if not transcriptions:
            raise ValueError(f"No transcription found for video ID: {video_id}")
            
        transcription = transcriptions[0]
            
        text = transcription.text

    # 2. Chunk transcript
    print("Extractor: Creating semantic chunks...")
    chunks_text = semantic_chunk_text(text)
    print(f"Extractor: Generated {len(chunks_text)} chunks.")

    extracted_data = []

    # 3. For each chunk: Embed & Extract Triplets
    for chunk_content in chunks_text:
        # Get local embedding
        print("Extractor: Generating local embedding via Ollama...")
        embedding = llm_client.get_embedding(chunk_content)
        
        # Extract Triplets
        print("Extractor: Extracting triplets...")
        triplets = llm_client.extract_triplets(chunk_content)
        
        # Filter triplets by confidence
        filtered_triplets = [
            t for t in triplets 
            if t.get("confidence", 1.0) >= confidence_threshold
        ]
        print(f"Extractor: Extracted {len(filtered_triplets)} high-confidence triplets.")
        
        extracted_data.append({
            "content": chunk_content,
            "embedding": embedding,
            "triplets": filtered_triplets
        })

    # 4. Save to Database
    graph_load_payload = []
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Clean up old extractions if any exist to prevent duplicates
            cleanup_stmt = select(Chunk).where(Chunk.video_id == video_id)
            existing_chunks_res = await session.execute(cleanup_stmt)
            existing_chunks = existing_chunks_res.scalars().all()
            for ec in existing_chunks:
                await session.delete(ec)
                
            # Insert new chunks and triplets
            for chunk_data in extracted_data:
                db_chunk = Chunk(
                    video_id=video_id,
                    content=chunk_data["content"],
                    embedding=chunk_data["embedding"]
                )
                session.add(db_chunk)
                await session.flush()  # Populates db_chunk.id
                
                for trip_data in chunk_data["triplets"]:
                    db_triplet = Triplet(
                        chunk_id=db_chunk.id,
                        subject=trip_data["subject"],
                        predicate=trip_data["predicate"],
                        object=trip_data["object"],
                        confidence=trip_data["confidence"]
                    )
                    session.add(db_triplet)
                
                # Collect payload for Neo4j and Qdrant streaming
                graph_load_payload.append({
                    "chunk_id": db_chunk.id,
                    "content": chunk_data["content"],
                    "embedding": chunk_data["embedding"],
                    "triplets": chunk_data["triplets"]
                })
                
    # 5. Load to Neo4j and Qdrant Databases
    print("Extractor: Streaming extractions to Graph (Neo4j) and Vector (Qdrant) databases...")
    from src.graph.graph_loader import load_chunk_and_triplets_to_graph
    from src.infrastructure.database.vector_client import vector_client
    
    for payload in graph_load_payload:
        # Load to Neo4j
        await load_chunk_and_triplets_to_graph(
            chunk_id=payload["chunk_id"],
            chunk_content=payload["content"],
            video_id=video_id,
            triplets=payload["triplets"]
        )
        # Load to Qdrant
        vector_client.upsert_chunk(
            chunk_id=payload["chunk_id"],
            embedding=payload["embedding"],
            payload={
                "content": payload["content"],
                "video_id": video_id
            }
        )
                    
    print(f"Extractor: Knowledge extraction and graph construction complete for video {video_id}.")
    return {
        "video_id": video_id,
        "chunks_count": len(extracted_data),
        "triplets_count": sum(len(c["triplets"]) for c in extracted_data)
    }
