
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from ingredient_parser import extract_ingredients


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

with (DATA_DIR / "recipes_prepared.json").open(
    encoding="utf-8"
) as f:
    recipes = json.load(f)

index = faiss.read_index(
    str(DATA_DIR / "recipes.faiss")
)

assert index.ntotal == len(recipes)

model = SentenceTransformer(MODEL_NAME)


def get_recipe_ingredients(recipe):
    """Extract the ingredient section from prepared text."""

    text = recipe["text"]

    if "Ингредиенты:\n" not in text:
        return set()

    section = text.split("Ингредиенты:\n", 1)[1]

    # Do not parse notes and captions as required ingredients.
    section = section.split(
        "\n\nОписание рецепта:", 1
    )[0]

    return extract_ingredients(section)


def hybrid_search(query, top_k=5):
    # Step 1: extract ingredients from user query
    available = extract_ingredients(query)

    # Step 2: semantic retrieval
    query_vector = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True
    ).astype("float32")

    # Search all 40 recipes for this first experiment.
    scores, indices = index.search(
        query_vector,
        index.ntotal
    )

    results = []

    for idx, semantic_score in zip(
        indices[0], scores[0]
    ):
        if idx < 0:
            continue

        recipe = recipes[int(idx)]
        required = get_recipe_ingredients(recipe)

        matched = available & required
        missing = required - available

        # Fraction of user's ingredients used.
        coverage = (
            len(matched) / len(available)
            if available else 0.0
        )

        # Fraction of known recipe ingredients available.
        availability = (
            len(matched) / len(required)
            if required else 0.0
        )

        # Blend semantic and ingredient information.
        # These are initial experimental weights.
        if available and required:
            ingredient_score = (
                0.65 * coverage
                + 0.35 * availability
            )

            hybrid_score = (
                0.40 * float(semantic_score)
                + 0.60 * ingredient_score
            )
        else:
            hybrid_score = float(semantic_score)

        results.append({
            "title": recipe["title"],
            "semantic_score": float(semantic_score),
            "ingredient_score": (
                ingredient_score
                if available and required else None
            ),
            "hybrid_score": hybrid_score,
            "matched": sorted(matched),
            "missing": sorted(missing),
            "text": recipe["text"]
        })

    results.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True
    )

    return results[:top_k]


if __name__ == "__main__":
    while True:
        query = input("\nЧто хочешь приготовить? ").strip()

        if query.lower() in {"exit", "quit", "выход"}:
            break

        if not query:
            continue

        results = hybrid_search(query)

        for rank, result in enumerate(results, 1):
            print(f"\n{rank}. {result['title']}")
            print(
                f"Hybrid score: "
                f"{result['hybrid_score']:.3f}"
            )
            print(
                f"Semantic score: "
                f"{result['semantic_score']:.3f}"
            )
            print(
                "Совпавшие продукты:",
                ", ".join(result["matched"]) or "нет"
            )
            print(
                "Другие распознанные продукты:",
                ", ".join(result["missing"]) or "нет"
            )
            print("-" * 45)
