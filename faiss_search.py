
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DATA_DIR = Path(__file__).resolve().parent / "data"

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

# Load recipe metadata
with open(DATA_DIR / "recipes_prepared.json", encoding="utf-8") as f:
    recipes = json.load(f)

# Load FAISS index
index = faiss.read_index(str(DATA_DIR / "recipes.faiss"))

assert index.ntotal == len(recipes), "Recipe/index count mismatch"

# Load embedding model
model = SentenceTransformer(MODEL_NAME)


def search(query, top_k=5):
    # Encode the user query
    query_vector = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True
    ).astype("float32")

    # Search for nearest recipes
    scores, indices = index.search(
        query_vector,
        min(top_k, index.ntotal)
    )

    results = []

    for idx, score in zip(indices[0], scores[0]):
        if idx == -1:
            continue

        recipe = recipes[int(idx)]

        results.append({
            "title": recipe["title"],
            "score": float(score),
            "text": recipe["text"]
        })

    return results


if __name__ == "__main__":
    while True:
        query = input("\nЧто хочешь приготовить? ").strip()

        if query.lower() in {"exit", "quit", "выход"}:
            break

        if not query:
            continue

        results = search(query)

        for rank, recipe in enumerate(results, 1):
            print(f"\n{rank}. {recipe['title']}")
            print(f"Similarity: {recipe['score']:.3f}")
            print("-" * 40)
