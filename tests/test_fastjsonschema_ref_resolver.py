import json
from typing import Any

import fastjsonschema
import pytest
from fastjsonschema import JsonSchemaDefinitionException, JsonSchemaValueException

EXAMPLE = {
    "my_string": "Hello world!",
    "my_number": 42,
}

SCHEMA_DIR = "schema"


def load_json(name: str) -> dict[str, Any]:
    with open(name, "r") as stream:
        return json.load(fp=stream)


def ref_handler(uri: str) -> dict[str, Any]:
    return load_json(f"{SCHEMA_DIR}/{uri}")


def test_resolve_internal_ref():
    validate = fastjsonschema.compile(
        definition=load_json("schema/base.json"),
        handlers={"": ref_handler},
    )
    validate(data=EXAMPLE)


def test_resolve_external_ref():
    validate = fastjsonschema.compile(
        definition=load_json("schema/derived.json"),
        handlers={"": ref_handler},
    )
    validate(data=EXAMPLE)


def test_json_schema_definition_error():
    with pytest.raises(JsonSchemaDefinitionException):
        fastjsonschema.compile(
            definition=load_json("schema/wrong.json"), handlers={"": ref_handler}
        )


def test_json_schema_value_error():
    validate = fastjsonschema.compile(
        definition=load_json("schema/base.json"), handlers={"": ref_handler}
    )
    with pytest.raises(JsonSchemaValueException):
        validate(data={"my_string": 1.0})
