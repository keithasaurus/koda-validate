from typing import Any, Dict, List, NoReturn, Union

from koda_validate import (
    BoolValidator,
    FloatValidator,
    IntValidator,
    KeyNotRequired,
    ListValidator,
    MapValidator,
    MaxKeys,
    MinKeys,
    NTupleValidator,
    OneOf2,
    OneOf3,
    OptionalValidator,
    RecordValidator,
)
from koda_validate.base import Predicate, PredicateAsync, Validator
from koda_validate.generic import Choices, Lazy, Max, MaxItems, Min, MinItems, UniqueItems
from koda_validate.serialization import Serializable
from koda_validate.string import (
    EmailPredicate,
    MaxLength,
    MinLength,
    NotBlank,
    RegexPredicate,
    StringValidator,
)


def unhandled_type(obj: Any) -> NoReturn:
    raise TypeError(f"type {type(obj)} not handled")


def string_schema(
    schema_name: str, validator: StringValidator
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = {"type": "string"}
    for pred in list(validator.predicates) + (validator.predicates_async or []):
        ret.update(generate_schema_base(schema_name, pred))

    return ret


def integer_schema(schema_name: str, validator: IntValidator) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = {"type": "integer"}
    for pred in list(validator.predicates) + (validator.predicates_async or []):
        ret.update(generate_schema_base(schema_name, pred))

    return ret


def float_schema(schema_name: str, validator: FloatValidator) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = {"type": "number"}
    for pred in list(validator.predicates) + (validator.predicates_async or []):
        ret.update(generate_schema_base(schema_name, pred))
    return ret


def boolean_schema(schema_name: str, validator: BoolValidator) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = {"type": "boolean"}
    for pred in list(validator.predicates) + (validator.predicates_async or []):
        ret.update(generate_schema_base(schema_name, pred))
    return ret


def array_of_schema(
    schema_name: str, validator: ListValidator[Any]
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = {
        "type": "array",
        "items": generate_schema_base(schema_name, validator.item_validator),
    }

    for pred in (validator.predicates or []) + (validator.predicates_async or []):
        ret.update(generate_schema_base(schema_name, pred))

    return ret


def obj_schema(
    schema_name: str,
    obj: RecordValidator[Any],
) -> Dict[str, Serializable]:
    required: List[str] = []
    properties: Dict[str, Serializable] = {}
    for label, field in obj.keys:
        str_label = str(label)
        if not isinstance(field, KeyNotRequired):
            required.append(str_label)

        properties[str_label] = generate_schema_base(schema_name, field)
    return {
        "type": "object",
        "additionalProperties": False,
        "required": required,  # type: ignore
        "properties": properties,
    }


def map_of_schema(
    schema_name: str, validator: MapValidator[Any, Any]
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = {
        "type": "object",
        "additionalProperties": generate_schema_base(
            schema_name, validator.value_validator
        ),
    }

    for pred in (validator.predicates or []) + (validator.predicates_async or []):
        ret.update(generate_schema_base(schema_name, pred))

    return ret


def generate_schema_predicate(
    validator: Union[Predicate[Any], PredicateAsync[Any]]
) -> Dict[str, Serializable]:
    # strings
    if isinstance(validator, EmailPredicate):
        return {"format": "email"}
    elif isinstance(validator, MaxLength):
        return {"maxLength": validator.length}
    elif isinstance(validator, MinLength):
        return {"minLength": validator.length}
    elif isinstance(validator, Choices):
        return {"enum": list(sorted(validator.choices))}
    elif isinstance(validator, NotBlank):
        return {"pattern": r"^(?!\s*$).+"}
    elif isinstance(validator, RegexPredicate):
        return {"pattern": validator.pattern.pattern}
    # numbers
    elif isinstance(validator, Min):
        return {
            "minimum": validator.minimum,
            "exclusiveMinimum": validator.exclusive_minimum,
        }
    elif isinstance(validator, Max):
        return {
            "maximum": validator.maximum,
            "exclusiveMaximum": validator.exclusive_maximum,
        }
    # objects
    elif isinstance(validator, MinKeys):
        return {"minProperties": validator.size}
    elif isinstance(validator, MaxKeys):
        return {"maxProperties": validator.size}
    # arrays
    elif isinstance(validator, MinItems):
        return {"minItems": validator.item_count}
    elif isinstance(validator, MaxItems):
        return {"maxItems": validator.item_count}
    elif isinstance(validator, UniqueItems):
        return {"uniqueItems": True}
    else:
        unhandled_type(validator)


def generate_schema_transformable(
    schema_name: str, obj: Validator[Any]
) -> Dict[str, Serializable]:
    # caution, mutation below!
    if isinstance(obj, BoolValidator):
        return boolean_schema(schema_name, obj)
    if isinstance(obj, StringValidator):
        return string_schema(schema_name, obj)
    elif isinstance(obj, IntValidator):
        return integer_schema(schema_name, obj)
    elif isinstance(obj, FloatValidator):
        return float_schema(schema_name, obj)
    elif isinstance(obj, OptionalValidator):
        maybe_val_ret = generate_schema_base(schema_name, obj.non_none_validator)
        if type(maybe_val_ret) is not dict:
            raise AssertionError("must be a dict")
        maybe_val_ret["nullable"] = True
        return maybe_val_ret
    elif isinstance(obj, MapValidator):
        return map_of_schema(schema_name, obj)
    elif isinstance(obj, RecordValidator):
        return obj_schema(schema_name, obj)
    # todo: add TupleHomogenousValidator
    elif isinstance(obj, ListValidator):
        return array_of_schema(schema_name, obj)
    elif isinstance(obj, Lazy):
        if obj.recurrent:
            return {"$ref": f"#/components/schemas/{schema_name}"}
        else:
            return generate_schema_base(schema_name, obj.validator)
    # todo: add UnionValidator
    elif isinstance(obj, OneOf2):
        return {
            "oneOf": [
                generate_schema_base(schema_name, s)
                for s in [obj.variant_1, obj.variant_2]
            ]
        }
    elif isinstance(obj, OneOf3):
        return {
            "oneOf": [
                generate_schema_base(schema_name, s)
                for s in [obj.variant_1, obj.variant_2, obj.variant_3]
            ]
        }
    elif isinstance(obj, NTupleValidator):

        return {
            "description": f"a {len(obj.fields)}-tuple; schemas for slots are listed "
            f'in order in "items" > "anyOf"',
            "type": "array",
            "maxItems": len(obj.fields),
            "items": {
                "anyOf": [generate_schema_base(schema_name, s) for s in [obj.fields]]
            },
        }
    else:
        unhandled_type(obj)


def generate_schema_base(schema_name: str, obj: Any) -> Dict[str, Serializable]:
    if isinstance(obj, Validator):
        return generate_schema_transformable(schema_name, obj)
    elif isinstance(obj, (Predicate, PredicateAsync)):
        return generate_schema_predicate(obj)
    else:
        unhandled_type(obj)


def generate_schema(schema_name: str, obj: Any) -> Dict[str, Serializable]:
    return {schema_name: generate_schema_base(schema_name, obj)}
