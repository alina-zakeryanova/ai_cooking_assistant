
import json
from typing import Optional

from ollama import chat
from pydantic import BaseModel, Field


# Define the expected JSON structure
class Ingredient(BaseModel):
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    fat_percent: Optional[float] = None


class RecipeIngredients(BaseModel):
    ingredients: list[Ingredient]


# Example from our dataset
recipe_text = """
Творог 5% - 200 г
Кефир - 150 мл
Яйца - 2 шт
Сахар по вкусу
Мука - 160 г
"""


response = chat(
    model="qwen3:1.7b",
    messages=[
        {
            "role": "system",
            "content": (
                "Ты извлекаешь ингредиенты из рецептов. "
                "Отвечай только на русском языке. "
                "Не добавляй ингредиенты, которых нет в тексте. "
                "Используй названия в единственном числе. "
                "Если количество не указано, используй null. "
                "Процент жирности сохраняй в fat_percent. "
                "Количество и единицу измерения сохраняй отдельно."
            ),
        },
        {
            "role": "user",
            "content": recipe_text,
        },
    ],
    format=RecipeIngredients.model_json_schema(),
    think=False,
    options={
        "temperature": 0,
    },
)

# Validate the model output
result = RecipeIngredients.model_validate_json(
    response.message.content
)

print(
    json.dumps(
        result.model_dump(),
        ensure_ascii=False,
        indent=2,
    )
)
