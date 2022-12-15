import json
from typing import Callable
from .recipe import SourceFieldStrategy, Recipe
from .recipe.state import MorphState
from .lexer import Lexer
from .morpher_parser import Parser

def morph(
    source_dict: dict = None, 
    source_json_path: str = None, 
    recipe: Recipe = None, 
    recipe_str: str = None, 
    recipe_path: str = None, 
    source_fields_stategy: SourceFieldStrategy = SourceFieldStrategy.AUTO_DROP, 
    with_source_fields_timestamp_cast: bool = False
) -> tuple[dict, dict, MorphState] :
    _source_dict = None 
    if source_dict:
        _source_dict = source_dict
    elif source_json_path:
        with open(source_json_path) as f:
            s = json.loads(f.read())
        _source_dict = s 
    else:
        print("Either source_dict or source_json_path should be provided!")
        raise ValueError

    _recipe = None 
    _recipe_str = recipe_str
    if recipe:
        _recipe = recipe
    elif recipe_path:
        with open(recipe_path) as f:
            _recipe_str = f.read()

    if _recipe_str:
        tokens = Lexer().tokenize(_recipe_str)
        instructions = Parser().parse(tokens)
        _recipe = Recipe(
            source_fields_stategy=source_fields_stategy, 
            with_source_fields_timestamp_cast=with_source_fields_timestamp_cast
        ).translate(instructions)

    return _recipe.morph(_source_dict)

def create_morph(    
    recipe: Recipe = None, 
    recipe_str: str = None, 
    recipe_path: str = None, 
    source_fields_stategy: SourceFieldStrategy = SourceFieldStrategy.AUTO_DROP, 
    with_source_fields_timestamp_cast: bool = False
) -> Callable[[dict], tuple[dict, dict, MorphState]]:
    def f(
        source_dict: dict
    ) -> Callable[[dict], tuple[dict, dict, MorphState]]:
        return morph(
            source_dict=source_dict, 
            recipe=recipe, 
            recipe_str=recipe_str, 
            recipe_path=recipe_path, 
            source_fields_stategy=source_fields_stategy, 
            with_source_fields_timestamp_cast=with_source_fields_timestamp_cast
        )

    return f