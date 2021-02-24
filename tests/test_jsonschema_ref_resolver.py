import json
from pathlib import Path
from typing import Any

from jsonschema import validate, RefResolver

EXAMPLE = {
    "my_string": "Hello world!",
    "my_number": 42,
    "my_other_string": "Hello Jan.",
}


def load_json(name: str) -> dict[str, Any]:
    with open(name, "r") as stream:
        return json.load(fp=stream)


def test_resolve_internal_ref():
    schema_path = Path("schema/base.json").absolute()
    schema = load_json(schema_path)
    resolver = RefResolver(
        base_uri=schema_path.as_uri(),
        referrer=schema,  # !!! required for file internal references
    )
    validate(
        instance=EXAMPLE,
        schema=schema,
        resolver=resolver,  # None
    )


def test_resolve_external_ref():
    schema_path = Path("schema/derived.json").absolute()
    schema = load_json(schema_path)
    resolver = RefResolver(
        base_uri=schema_path.as_uri(),
        referrer=schema,
    )
    validate(
        instance=EXAMPLE,
        schema=schema,
        resolver=resolver,
    )
