from jsonschema import (
    validate,
    ValidationError,
    SchemaError,
    Draft7Validator,
)
from ruamel import yaml
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError


def test_all_of():
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


def test_all_of_2():
    schema = yaml.load(open("schema/schema_allof.yaml", "r"), Loader=yaml.Loader)
    instance = yaml.load(open("schema/instance_allof.yaml", "r"), Loader=yaml.Loader)
    v = Draft7Validator(schema)
    errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
    for error in errors:
        for suberror in sorted(error.context, key=lambda e: e.schema_path):
            print(list(suberror.schema_path), suberror.message, sep=", ")
