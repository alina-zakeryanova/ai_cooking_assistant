
import json
import re
from pathlib import Path

from regex_parser import parse_ingredient


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

INPUT_PATH = DATA_DIR / "recipes_raw.json"
OUTPUT_PATH = DATA_DIR / "recipes_structured.json"
REVIEW_PATH = DATA_DIR / "ingredients_to_review.json"

SECTION_NAMES = {
    "ингредиенты": "main",
    "начинка": "filling",
    "тесто": "dough",
    "основа": "base",
    "соус": "sauce",
    "сухарики": "croutons",
    "салат": "salad",
    "сборка": "assembly",
    "сборка салата": "assembly",
    "овощи": "vegetables",
    "фрикадельки": "meatballs",
    "штрейзель": "streusel",
    "посыпать": "topping",
    "соус для подачи": "serving_sauce",
    "для подачи по желанию": "optional_serving",
    "сметанная заливка": "filling",
}

def detect_section(line):
    clean = line.strip().lower().rstrip(":")

    # Handles "Ингредиенты на 2 порции:"
    if clean.startswith("ингредиенты"):
        return "main"

    return SECTION_NAMES.get(clean)


def extract_ingredient_lines(caption):
    lines = caption.splitlines()

    current_section = None
    items = []
    skipped = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        section = detect_section(line)

        if section:
            current_section = section
            continue

        # Ignore content before ingredients heading
        if current_section is None:
            continue

        # Stop at hashtags / video links
        if (
            line.startswith("#")
            or "https://" in line
            or "http://" in line
            or line.lower().startswith("для тех, у кого")
        ):
            break

        # Detect metadata accidentally included
        if re.fullmatch(r"\d+[.,]?\d*[kK]?views.*", line):
            break

        # Parse potential ingredient
        ingredient = parse_ingredient(line)
        ingredient["section"] = current_section

        if ingredient["name"]:
            items.append(ingredient)
        else:
            skipped.append(line)

    return items, skipped


def main():
    with INPUT_PATH.open(encoding="utf-8") as f:
        recipes = json.load(f)

    structured = []
    review = []

    for i, recipe in enumerate(recipes):
        # Support alternative source field names
        caption = (
            recipe.get("caption")
            or recipe.get("raw_text")
            or recipe.get("text")
            or ""
        )

        ingredients, skipped = extract_ingredient_lines(caption)

        result = {
            **recipe,
            "ingredients": ingredients,
            "ingredient_count": len(ingredients),
        }

        structured.append(result)

        if skipped or not ingredients:
            review.append({
                "id": recipe.get("id", i + 1),
                "title": recipe.get("title"),
                "skipped": skipped,
                "ingredient_count": len(ingredients),
            })

    OUTPUT_PATH.write_text(
        json.dumps(structured, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    REVIEW_PATH.write_text(
        json.dumps(review, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Recipes processed: {len(structured)}")
    print(
        "Recipes with ingredients:",
        sum(bool(r["ingredients"]) for r in structured)
    )
    print(
        "Total ingredient entries:",
        sum(r["ingredient_count"] for r in structured)
    )
    print("Recipes flagged for review:", len(review))

    for recipe in structured[:3]:
        print(
            f"\n{recipe.get('title')}: "
            f"{recipe['ingredient_count']} ingredients"
        )
        for ingredient in recipe["ingredients"][:5]:
            print(" -", ingredient["raw_text"])


if __name__ == "__main__":
    main()
