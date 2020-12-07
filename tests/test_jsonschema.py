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
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError

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
    file = "schema/instance_allof.yaml"
    try:
        with open("schema/schema_allof.yaml", "r") as stream:
            schema = yaml.load(stream, Loader=yaml.RoundTripLoader)
        with open(file, "r") as stream:
            instance = yaml.load(stream, Loader=yaml.RoundTripLoader)
        validate(schema=schema, instance=instance)
    except ScannerError as error:
        header = f"{error.problem_mark.name or ''}, line {error.problem_mark.line}, column {error.problem_mark.column}"
        print(f"\n{header}, yaml scanner error: {error.context} {error.problem}")
    except ParserError as error:
        header = f"{error.problem_mark.name}, line {error.problem_mark.line}, column {error.problem_mark.column}"
        print(f"\n{header}, yaml parser error: {error.context} {error.problem}")
    except SchemaError as error:
        # msg = f"message={error.message}\nvalidator={error.validator}\nvalidator_value={error.validator_value}"
        # msg = f"{msg}\nschema={error.schema}\nrelative_schema_path={error.relative_schema_path}"
        # msg = f"{msg}\nabsolute_schema_path={error.absolute_schema_path}\nschema_path={error.schema_path}"
        # msg = f"{msg}\nrelative_path={error.relative_path}\nabsolute_path={error.absolute_path}"
        # msg = f"{msg}\npath={error.path}\ninstance={error.instance}\ncontext={error.context}"
        # msg = f"{msg}\ncause={error.cause}\nparent={error.parent}"
        # print(f"\nSchemaError\n{msg}")
        print(f"\n{file}, schema error, {error.message}")
    except ValidationError as error:
        print(f"\n{file}, validation error, {error.message}")


def test_allof2():
    schema = yaml.load(open("schema/schema_allof.yaml", "r"), Loader=yaml.Loader)
    instance = yaml.load(open("schema/instance_allof.yaml", "r"), Loader=yaml.Loader)
    v = Draft7Validator(schema)
    errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
    for error in errors:
        for suberror in sorted(error.context, key=lambda e: e.schema_path):
            print(list(suberror.schema_path), suberror.message, sep=", ")
