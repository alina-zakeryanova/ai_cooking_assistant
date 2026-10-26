
from pathlib import Path

import faiss
import numpy as np

DATA_DIR = Path(__file__).resolve().parent / "data"

# Load the embeddings we created previously
embeddings = np.load(
    DATA_DIR / "recipe_embeddings.npy"
).astype("float32")

# Ensure embeddings are normalized
faiss.normalize_L2(embeddings)

# Number of dimensions (384 for our model)
dimension = embeddings.shape[1]

# Exact nearest-neighbor search
index = faiss.IndexFlatIP(dimension)

# Add all recipe vectors
index.add(embeddings)

# Save the FAISS index
faiss.write_index(
    index,
    str(DATA_DIR / "recipes.faiss")
)

print(f"Index created: {index.ntotal} recipes")
print(f"Vector dimension: {dimension}")
