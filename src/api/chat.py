from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.infrastructure.ai.llm_client import llm_client
from src.retrieval.context_assembly import (
    assemble_context,
    format_seconds_to_timestamp,
    get_chunk_timestamps,
    get_video_title,
)
from src.retrieval.hybrid_retriever import hybrid_retriever

chat_router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5


class SourceCitation(BaseModel):
    video_id: str
    video_title: str
    start_time: str
    end_time: str
    content: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    graph_facts: List[Dict[str, Any]]


@chat_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    POST /api/v1/chat
    Accepts a query and returns a source-cited reasoning response leveraging GraphRAG.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty")

    try:
        # 1. Retrieve hybrid context
        retrieved_data = await hybrid_retriever.retrieve(
            request.query, top_k=request.top_k
        )

        # 2. Assemble dense context for LLM
        context_block = await assemble_context(retrieved_data)

        # 3. Generate answer citing the context sources
        answer = llm_client.generate_reasoning_answer(request.query, context_block)

        # 4. Format source citations with titles and timestamps
        sources = []
        for chunk in retrieved_data.get("chunks", []):
            video_id = chunk["video_id"]
            title = await get_video_title(video_id)
            start, end = await get_chunk_timestamps(chunk["content"], video_id)

            sources.append(
                SourceCitation(
                    video_id=video_id,
                    video_title=title,
                    start_time=format_seconds_to_timestamp(start),
                    end_time=format_seconds_to_timestamp(end),
                    content=chunk["content"],
                )
            )

        # 5. Extract graph facts used
        graph_facts = [
            {
                "subject": rel["subject"],
                "predicate": rel["predicate"],
                "object": rel["object"],
            }
            for rel in retrieved_data.get("relationships", [])
        ]

        return ChatResponse(answer=answer, sources=sources, graph_facts=graph_facts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GraphRAG Chat failed: {str(e)}")
