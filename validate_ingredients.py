
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

with (DATA_DIR / "recipes_structured.json").open(
    encoding="utf-8"
) as f:
    recipes = json.load(f)

issues = []

QUANTITY_PATTERN = re.compile(
    r"\d+(?:[.,]\d+)?\s*(?:г|гр|кг|мл|л|шт)\b",
    re.IGNORECASE
)

for recipe in recipes:
    for ingredient in recipe["ingredients"]:
        raw = ingredient["raw_text"]
        name = ingredient["name"]
        reasons = []

        # Multiple ingredients in one line
        if re.search(r",|\s+и\s+", name):
            reasons.append("possible_multiple_ingredients")

        # Multiple quantities in one line
        if len(QUANTITY_PATTERN.findall(raw)) > 1:
            reasons.append("multiple_quantities")

        # Alternative ingredients
        if re.search(r"\s+или\s+|/", name):
            reasons.append("possible_alternatives")

        # No quantity specified
        if ingredient["quantity_min"] is None:
            reasons.append("missing_quantity")

        # Name is unusually long
        if len(name.split()) > 5:
            reasons.append("long_ingredient_name")

        if reasons:
            issues.append({
                "recipe": recipe["title"],
                "raw_text": raw,
                "parsed_name": name,
                "reasons": reasons,
            })

output = DATA_DIR / "ingredient_issues.json"

output.write_text(
    json.dumps(issues, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print("Recipes:", len(recipes))
print(
    "Ingredients:",
    sum(len(r["ingredients"]) for r in recipes)
)
print("Potential issues:", len(issues))

for issue in issues[:20]:
    print(
        issue["recipe"],
        "|", issue["raw_text"],
        "|", ", ".join(issue["reasons"])
    )
