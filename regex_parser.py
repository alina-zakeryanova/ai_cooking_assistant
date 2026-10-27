
import re
import json

ALIASES = {
    "яйца": "яйцо",
    "яиц": "яйцо",
    "кабачки": "кабачок",
    "цукини": "кабачок",
    "бананы": "банан",
    "яблоки": "яблоко",
    "помидоры": "помидор",
    "томаты": "помидор",
}

AMOUNT_PATTERN = re.compile(
    r"(?P<min>\d+(?:[.,]\d+)?)"
    r"(?:\s*[-–—]\s*(?P<max>\d+(?:[.,]\d+)?))?"
    r"\s*(?P<unit>ст\.?\s*л\.?|ч\.?\s*л\.?|"
    r"г|гр|кг|мл|л|шт)\b",
    re.IGNORECASE,
)

FAT_PATTERN = re.compile(r"(\d+(?:[.,]\d+)?)\s*%")


def parse_ingredient(line):
    raw_text = line.strip()

    optional = "по желанию" in raw_text.lower()
    to_taste = "по вкусу" in raw_text.lower()

    amount_match = AMOUNT_PATTERN.search(raw_text)
    fat_match = FAT_PATTERN.search(raw_text)

    quantity_min = None
    quantity_max = None
    unit = None

    if amount_match:
        quantity_min = float(
            amount_match.group("min").replace(",", ".")
        )

        if amount_match.group("max"):
            quantity_max = float(
                amount_match.group("max").replace(",", ".")
            )

        unit = amount_match.group("unit").lower()

    # Remove quantities, fat percentage and qualifiers
    name = raw_text

    name = AMOUNT_PATTERN.sub("", name)
    name = FAT_PATTERN.sub("", name)

    name = re.sub(
        r"\b(по вкусу|по желанию)\b",
        "",
        name,
        flags=re.IGNORECASE,
    )

    name = name.strip(" -–—(),.").lower()
    name = re.sub(r"\s+", " ", name)

    name = ALIASES.get(name, name)

    return {
        "name": name,
        "quantity_min": quantity_min,
        "quantity_max": quantity_max,
        "unit": unit,
        "fat_percent": (
            float(fat_match.group(1).replace(",", "."))
            if fat_match else None
        ),
        "optional": optional,
        "to_taste": to_taste,
        "raw_text": raw_text,
    }


if __name__ == "__main__":
    examples = [
        "Творог 5% - 200 г",
        "Мука - 150-170 г",
        "Яйца - 2 шт",
        "Сахар по вкусу",
        "Пармезан по желанию",
        "Сметана 20% - 350 г",
    ]

    results = [parse_ingredient(x) for x in examples]

    print(json.dumps(
        results,
        ensure_ascii=False,
        indent=2,
    ))
