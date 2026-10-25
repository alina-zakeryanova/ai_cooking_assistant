
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

INPUT_PATH = DATA_DIR / "recipes_raw.json"
OUTPUT_PATH = DATA_DIR / "recipes_prepared.json"

# 1. Load recipes
with INPUT_PATH.open("r", encoding="utf-8") as f:
    recipes = json.load(f)

print(f"Loaded {len(recipes)} recipes")

# 2. Prepare searchable documents
documents = []

for recipe in recipes:
    title = recipe["title"]
    ingredients = recipe.get("ingredients_text", "")
    caption = recipe.get("caption", "")

    # Text that will later be converted to an embedding
    searchable_text = (
        f"Название блюда: {title}\n"
        f"Ингредиенты:\n{ingredients}\n\n"
        f"Описание рецепта:\n{caption}"
    )

    document = {
        "id": recipe["id"],
        "title": title,
        "text": searchable_text,
        "source_url": recipe.get("source_url"),
    }

    documents.append(document)

# 3. Save prepared documents
with OUTPUT_PATH.open("w", encoding="utf-8") as f:
    json.dump(
        documents,
        f,
        ensure_ascii=False,
        indent=2,
    )

print(f"Prepared {len(documents)} documents")
print(f"Saved to: {OUTPUT_PATH}")

# 4. Inspect the first document
print("\nFIRST DOCUMENT:\n")
print(documents[0]["text"])
