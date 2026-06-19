import math
import re
from typing import List
from src.infrastructure.ai.llm_client import llm_client


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(v1, v2))
    m1 = math.sqrt(sum(a * a for a in v1))
    m2 = math.sqrt(sum(b * b for b in v2))
    if not m1 or not m2:
        return 0.0
    return dot_product / (m1 * m2)


def split_sentences(text: str) -> List[str]:
    """Splits a body of text into sentences using simple regex."""
    # Split on periods, exclamation marks, or question marks followed by spaces
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def semantic_chunk_text(text: str, min_words: int = 50, max_words: int = 250, similarity_threshold: float = 0.6) -> List[str]:
    """
    Groups sentences into chunks. Starts a new chunk if the cosine similarity
    between adjacent sentence embeddings falls below `similarity_threshold`.
    Enforces min_words and max_words constraints.
    """
    sentences = split_sentences(text)
    if not sentences:
        return []

    # Get embeddings for each sentence
    embeddings = [llm_client.get_embedding(s) for s in sentences]
    
    chunks = []
    current_chunk_sentences = [sentences[0]]
    current_chunk_words = len(sentences[0].split())

    for i in range(1, len(sentences)):
        sentence = sentences[i]
        words_count = len(sentence.split())
        
        # Calculate similarity with the previous sentence
        sim = cosine_similarity(embeddings[i-1], embeddings[i])
        
        # Determine whether to split
        reached_max = (current_chunk_words + words_count) > max_words
        is_semantic_shift = sim < similarity_threshold
        has_min_words = current_chunk_words >= min_words
        
        if (is_semantic_shift and has_min_words) or reached_max:
            # Emit current chunk
            chunks.append(" ".join(current_chunk_sentences))
            current_chunk_sentences = [sentence]
            current_chunk_words = words_count
        else:
            # Append to current chunk
            current_chunk_sentences.append(sentence)
            current_chunk_words += words_count

    # Emit trailing chunk
    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))

    return chunks
