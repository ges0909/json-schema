import logging

import pytest
from jsonschema import (
    ValidationError,
    SchemaError,
    validate,
)
from ruamel import yaml

json_schema = {
    "type": "object",
    "properties": {
        "price": {
            "type": "number",
        },
        "name": {
            "type": "string",
        },
    },
}


def test_validate_ok():
    json_instance = {"name": "Eggs", "price": 34.99}
    validate(instance=json_instance, schema=json_schema)


def test_validate_error():
    json_instance = {"name": "Eggs", "price": "Invalid"}
    with pytest.raises(ValidationError):
        # raises an exception if validation fails
        validate(instance=json_instance, schema=json_schema)


yaml_schema = """
type: object
properties:
    price:
        type: number
    name:
        type: string
"""


def test_validate_yaml_ok():
    yaml_instance = """
        name: Eggs
        price: 34.99
    """
    validate(instance=yaml.load(yaml_instance), schema=yaml.load(yaml_schema))


def load_yaml_file(path: str) -> dict:
    with open(path, "r") as stream:
        return yaml.safe_load(stream)


def test_yaml_validate():
    logger = logging.getLogger(__name__)
    try:
        validate(
            instance=load_yaml_file("schema/instance.yaml"),
            schema=load_yaml_file("schema/schema.yaml"),
        )
    except (SchemaError, ValidationError) as error:
        logger.error("%s, schema=%s, instance=%s", error.message, error.schema, error.EXAMPLE)
        raise
