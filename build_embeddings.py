
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

with (DATA_DIR / "recipes_prepared.json").open(
    "r", encoding="utf-8"
) as f:
    recipes = json.load(f)

print(f"Loaded {len(recipes)} recipes")

# Load multilingual embedding model
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Prepare text for encoding
texts = [recipe["text"] for recipe in recipes]

# Convert documents into vectors
embeddings = model.encode(
    texts,
    batch_size=16,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True,
)

# Save embeddings
np.save(DATA_DIR / "recipe_embeddings.npy", embeddings)

print("Embeddings shape:", embeddings.shape)
print("Saved embeddings to data/recipe_embeddings.npy")
