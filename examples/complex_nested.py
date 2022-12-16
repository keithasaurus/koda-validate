from dataclasses import dataclass
from typing import List, Literal, Optional, TypedDict, Union

from koda_validate import TypedDictValidator, Valid


@dataclass
class Ingredient:
    quantity: Union[int, float]
    unit: Optional[Literal["teaspoon", "tablespoon"]]  # etc...
    name: str


class Recipe(TypedDict):
    title: str
    ingredients: List[Ingredient]
    instructions: str


recipe_validator = TypedDictValidator(Recipe)

result = recipe_validator(
    {
        "title": "Peanut Butter and Jelly Sandwich",
        "ingredients": [
            {"quantity": 2, "unit": None, "name": "slices of bread"},
            {"quantity": 2, "unit": "tablespoon", "name": "peanut butter"},
            {"quantity": 4.5, "unit": "teaspoon", "name": "jelly"},
        ],
        "instructions": "spread the peanut butter and jelly onto the bread",
    }
)

assert result == Valid(
    {
        "title": "Peanut Butter and Jelly Sandwich",
        "ingredients": [
            Ingredient(quantity=2, unit=None, name="slices of bread"),
            Ingredient(quantity=2, unit="tablespoon", name="peanut butter"),
            Ingredient(quantity=4.5, unit="teaspoon", name="jelly"),
        ],
        "instructions": "spread the peanut butter and jelly onto the bread",
    }
)
