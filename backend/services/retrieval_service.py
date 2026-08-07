import numpy as np


# ==================================================
# RETRIEVE RELEVANT CHUNKS
# ==================================================

def retrieve_relevant_chunks(
    chunks: list[str],
    chunk_embeddings: list[list[float]],
    query_embedding: list[float],
    top_k: int = 5,
) -> list[str]:

    if not chunks:
        return []

    if not chunk_embeddings:
        return []

    if len(chunks) != len(chunk_embeddings):
        raise ValueError(
            "Each chunk must have one embedding."
        )

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than zero."
        )

    chunk_vectors = np.array(
        chunk_embeddings
    )

    query_vector = np.array(
        query_embedding
    )

    scores = chunk_vectors @ query_vector

    top_indices = np.argsort(
        scores
    )[::-1][:top_k]

    relevant_chunks = [
        chunks[index]
        for index in top_indices
    ]

    return relevant_chunks