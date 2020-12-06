import logging

import pytest
from jsonschema import (
    validate,
    ValidationError,
    SchemaError,
    Draft7Validator,
    validators,
)
from ruamel import yaml

json_schema = {
    "type": "object",
    "properties": {"price": {"type": "number"}, "name": {"type": "string"}},
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
    except (SchemaError, ValidationError) as ex:
        logger.error("%s, schema=%s, instance=%s", ex.message, ex.schema, ex.instance)
        raise


def _property_order(validator, value, instance, schema):
    instance_keys: list = list(instance.keys())
    schema_keys: list = schema.get("propertyOrder")
    for index, schema_key in enumerate(schema_keys):
        instance_key = instance_keys[index]
        if schema_key != instance_key:
            yield ValidationError(
                f"keyword '{instance_key}' occurs in wrong order (expected order is {schema_keys})"
            )


def test_yaml_ordered_keys():
    logger = logging.getLogger(__name__)

    all_validators = dict(Draft7Validator.VALIDATORS)
    all_validators["propertyOrder"] = _property_order
    my_validator = validators.create(
        meta_schema=Draft7Validator.META_SCHEMA, validators=all_validators
    )
    my_validator = my_validator(schema=load_yaml_file("schema/schema_ordered.yaml"))
    try:
        my_validator.validate(instance=load_yaml_file("schema/instance_ordered.yaml"))
    except (SchemaError, ValidationError) as ex:
        logger.error("%s, schema=%s, instance=%s", ex.message, ex.schema, ex.instance)
        raise


def test_allof():
    try:
        validate(
            schema=yaml.load(
                open("schema/schema_allof.yaml", "r"),
                Loader=yaml.Loader,
            ),
            instance=yaml.load(
                open("schema/instance_allof.yaml", "r"),
                Loader=yaml.Loader,
            ),
        )
    except ValidationError as error:
        print(f"\n{error.message}")
