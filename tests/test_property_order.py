import logging

from jsonschema import (
    ValidationError,
    SchemaError,
    Draft7Validator,
    validators,
)
from ruamel import yaml

logger = logging.getLogger(__name__)


def load_yaml_file(path: str) -> dict:
    with open(path, "r") as stream:
        return yaml.safe_load(stream)


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
    all_validators = dict(Draft7Validator.VALIDATORS)
    all_validators["propertyOrder"] = _property_order
    my_validator = validators.create(
        meta_schema=Draft7Validator.META_SCHEMA, validators=all_validators
    )
    my_validator = my_validator(schema=load_yaml_file("schema/schema_ordered.yaml"))
    try:
        my_validator.validate(instance=load_yaml_file("schema/instance_ordered.yaml"))
    except (SchemaError, ValidationError) as ex:
        logger.error("%s, schema=%s, instance=%s", ex.message, ex.schema, ex.EXAMPLE)
        raise
