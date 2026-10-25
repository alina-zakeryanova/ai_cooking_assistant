
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

DATA_DIR = Path(__file__).resolve().parent / "data"

# Load documents
with (DATA_DIR / "recipes_prepared.json").open(
    encoding="utf-8"
) as f:
    recipes = json.load(f)

# Load precomputed embeddings
embeddings = np.load(DATA_DIR / "recipe_embeddings.npy")

assert len(recipes) == len(embeddings), "Data mismatch!"

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

def search(query, top_k=5):
    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    )

    # Normalized dot product = cosine similarity
    scores = embeddings @ query_embedding

    top_indices = np.argsort(scores)[::-1][:top_k]

    for rank, idx in enumerate(top_indices, 1):
        recipe = recipes[int(idx)]

        print(f"\n{rank}. {recipe['title']}")
        print(f"Similarity: {scores[idx]:.3f}")
        print(recipe["text"][:350])
        print("-" * 50)


if __name__ == "__main__":
    while True:
        query = input("\nЧто хочешь приготовить? ").strip()

        if query.lower() in {"exit", "quit", "выход"}:
            break

        if query:
            search(query)
