from functools import lru_cache


MODEL_NAME = "all-MiniLM-L6-v2"


# ==================================================
# LOAD EMBEDDING MODEL
# ==================================================

@lru_cache(maxsize=1)
def get_embedding_model():

    from sentence_transformers import (
        SentenceTransformer,
    )

    return SentenceTransformer(
        MODEL_NAME
    )


# ==================================================
# CREATE EMBEDDINGS
# ==================================================

def create_embeddings(
    chunks: list[str],
) -> list[list[float]]:

    if not chunks:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.tolist()