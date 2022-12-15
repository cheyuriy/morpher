from pprint import pprint
from morpher import morph, register_function, create_morph
import json

register_function("process_tags", lambda x: [x, len(x)])

pprint(
    morph(
        source_json_path="example.json",
        recipe_path="example.morph"
    )
)

with open("example.json") as f:
    s = json.loads(f.read())

f = create_morph(recipe_path="example.morph")
pprint(
    f(s)
)