import re
from datetime import date, datetime
from decimal import Decimal
from functools import partial
from typing import Any, Callable, Dict, List, NoReturn, Type, Union
from uuid import UUID

from koda_validate import NotBlank, UUIDValidator
from koda_validate.base import CacheValidatorBase, Predicate, PredicateAsync, Validator
from koda_validate.boolean import BoolValidator
from koda_validate.bytes import BytesValidator
from koda_validate.dataclasses import DataclassValidator
from koda_validate.decimal import DecimalValidator
from koda_validate.dictionary import (
    DictValidatorAny,
    IsDictValidator,
    KeyNotRequired,
    MapValidator,
    MaxKeys,
    MinKeys,
    RecordValidator,
)
from koda_validate.float import FloatValidator
from koda_validate.generic import (
    Choices,
    EndsWith,
    EqualsValidator,
    EqualTo,
    ExactLength,
    Lazy,
    Max,
    MaxItems,
    MaxLength,
    Min,
    MinItems,
    MinLength,
    StartsWith,
    UniqueItems,
)
from koda_validate.integer import IntValidator
from koda_validate.list import ListValidator
from koda_validate.namedtuple import NamedTupleValidator
from koda_validate.none import OptionalValidator
from koda_validate.serialization.base import Serializable
from koda_validate.string import EmailPredicate, RegexPredicate, StringValidator
from koda_validate.time import DatetimeValidator, DateValidator
from koda_validate.tuple import NTupleValidator, UniformTupleValidator
from koda_validate.typeddict import TypedDictValidator
from koda_validate.union import UnionValidator

AnyValidatorOrPredicate = Union[Validator[Any], Predicate[Any], PredicateAsync[Any]]
ValidatorToSchema = Callable[[AnyValidatorOrPredicate], Dict[str, Serializable]]


def unhandled_type(obj: Any) -> NoReturn:
    raise TypeError(
        f"type {type(obj)} not handled. You may want to write a wrapper function."
    )


def get_base(t: Type[Any]) -> Dict[str, Any]:
    if t is str:
        return {"type": "string"}
    elif t is bytes:
        return {"type": "string", "format": "byte"}
    elif t is int:
        return {"type": "integer"}
    elif t is Decimal:
        return {
            "type": "string",
            "format": "number",
            # based on BigDecimal (Java) but without exponent support. At least one
            # digit required, before or after comma
            # valid values:  "100.234567", "010", "-.05", "+1", "10", "100."
            "pattern": r"^(\-|\+)?((\d+(\.\d*)?)|(\.\d+))$",
        }
    elif t is float:
        return {"type": "number"}
    elif t is date:
        return {"type": "string", "format": "date"}
    elif t is datetime:
        return {"type": "string", "format": "date-time"}
    elif t is bool:
        return {"type": "boolean"}
    elif t is UUID:
        return {"type": "string", "format": "uuid"}
    raise TypeError(f"Got unexpected type: {t}")


def string_schema(
    to_schema_fn: ValidatorToSchema, validator: StringValidator
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = get_base(str)

    for pred in list(validator.predicates) + (validator.predicates_async or []):
        ret.update(to_schema_fn(pred))

    return ret


def bytes_schema(
    to_schema_fn: ValidatorToSchema, validator: BytesValidator
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = get_base(bytes)
    for pred in list(validator.predicates) + (validator.predicates_async or []):
        ret.update(to_schema_fn(pred))

    return ret


def integer_schema(
    to_schema_fn: ValidatorToSchema, validator: IntValidator
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = get_base(int)
    for pred in list(validator.predicates) + (validator.predicates_async or []):
        ret.update(to_schema_fn(pred))

    return ret


def decimal_schema(
    to_schema_fn: ValidatorToSchema, validator: DecimalValidator
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = get_base(Decimal)
    for pred in list(validator.predicates) + (validator.predicates_async or []):
        ret.update(to_schema_fn(pred))
    return ret


def float_schema(
    to_schema_fn: ValidatorToSchema, validator: FloatValidator
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = get_base(float)
    for pred in list(validator.predicates) + (validator.predicates_async or []):
        ret.update(to_schema_fn(pred))
    return ret


def date_schema(
    to_schema_fn: ValidatorToSchema, validator: DateValidator
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = get_base(date)
    for pred in list(validator.predicates) + (validator.predicates_async or []):
        ret.update(to_schema_fn(pred))
    return ret


def datetime_schema(
    to_schema_fn: ValidatorToSchema, validator: DatetimeValidator
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = get_base(datetime)
    for pred in list(validator.predicates) + (validator.predicates_async or []):
        ret.update(to_schema_fn(pred))
    return ret


def equals_schema(
    to_schema_fn: ValidatorToSchema, validator: EqualsValidator[Any]
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = get_base(type(validator.match))
    ret.update(to_schema_fn(validator.predicate))
    return ret


def boolean_schema(
    to_schema_fn: ValidatorToSchema, validator: BoolValidator
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = get_base(bool)
    for pred in list(validator.predicates) + (validator.predicates_async or []):
        ret.update(to_schema_fn(pred))
    return ret


def uuid_schema(
    to_schema_fn: ValidatorToSchema, validator: UUIDValidator
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = get_base(UUID)
    for pred in list(validator.predicates) + (validator.predicates_async or []):
        ret.update(to_schema_fn(pred))
    return ret


def array_of_schema(
    to_schema_fn: ValidatorToSchema,
    validator: Union[ListValidator[Any], UniformTupleValidator[Any]],
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = {
        "type": "array",
        "items": to_schema_fn(validator.item_validator),
    }

    for pred in (validator.predicates or []) + (validator.predicates_async or []):
        ret.update(to_schema_fn(pred))

    return ret


def obj_schema(
    to_schema_fn: ValidatorToSchema,
    obj: RecordValidator[Any],
) -> Dict[str, Serializable]:
    required: List[str] = []
    properties: Dict[str, Serializable] = {}
    for label, field in obj.keys:
        str_label = str(label)
        if not isinstance(field, KeyNotRequired):
            required.append(str_label)

        properties[str_label] = to_schema_fn(field)
    return {
        "type": "object",
        "additionalProperties": not obj.fail_on_unknown_keys,
        "required": required,  # type: ignore
        "properties": properties,
    }


def dict_validator_schema(
    to_schema_fn: ValidatorToSchema,
    obj: DictValidatorAny,
) -> Dict[str, Serializable]:
    required: List[str] = []
    properties: Dict[str, Serializable] = {}
    for label, field in obj.schema.items():
        str_label = str(label)
        if not isinstance(field, KeyNotRequired):
            required.append(str_label)

        properties[str_label] = to_schema_fn(field)
    return {
        "type": "object",
        "additionalProperties": not obj.fail_on_unknown_keys,
        "required": required,  # type: ignore
        "properties": properties,
    }


def dataclass_validator_schema(
    to_schema_fn: ValidatorToSchema,
    obj: DataclassValidator[Any],
) -> Dict[str, Serializable]:
    properties: Dict[str, Serializable] = {}
    for label, field in obj.schema.items():
        str_label = str(label)
        properties[str_label] = to_schema_fn(field)
    return {
        "type": "object",
        "additionalProperties": not obj.fail_on_unknown_keys,
        "required": obj.required_fields,  # type: ignore
        "properties": properties,
    }


def namedtuple_validator_schema(
    to_schema_fn: ValidatorToSchema,
    obj: NamedTupleValidator[Any],
) -> Dict[str, Serializable]:
    properties: Dict[str, Serializable] = {}
    for label, field in obj.schema.items():
        str_label = str(label)
        properties[str_label] = to_schema_fn(field)
    return {
        "type": "object",
        "additionalProperties": not obj.fail_on_unknown_keys,
        "required": obj.required_fields,  # type: ignore
        "properties": properties,
    }


def typeddict_validator_schema(
    to_schema_fn: ValidatorToSchema,
    obj: TypedDictValidator[Any],
) -> Dict[str, Serializable]:
    properties: Dict[str, Serializable] = {}
    for label, field in obj.schema.items():
        str_label = str(label)
        properties[str_label] = to_schema_fn(field)
    return {
        "type": "object",
        "additionalProperties": not obj.fail_on_unknown_keys,
        "required": sorted(obj.required_keys),  # type: ignore
        "properties": properties,
    }


def map_of_schema(
    to_schema_fn: ValidatorToSchema, validator: MapValidator[Any, Any]
) -> Dict[str, Serializable]:
    ret: Dict[str, Serializable] = {
        "type": "object",
        "additionalProperties": to_schema_fn(validator.value_validator),
    }

    for pred in (validator.predicates or []) + (validator.predicates_async or []):
        ret.update(to_schema_fn(pred))

    return ret


def generate_schema_predicate(
    pred: Union[Predicate[Any], PredicateAsync[Any]]
) -> Dict[str, Serializable]:
    # strings
    if isinstance(pred, EmailPredicate):
        return {"format": "email"}
    elif isinstance(pred, MaxLength):
        return {"maxLength": pred.length}
    elif isinstance(pred, MinLength):
        return {"minLength": pred.length}
    elif isinstance(pred, ExactLength):
        return {"minLength": pred.length, "maxLength": pred.length}
    elif isinstance(pred, Choices):
        return {"enum": (list(sorted(pred.choices)))}
    elif isinstance(pred, NotBlank):
        return {"pattern": r"^(?!\s*$).+"}
    elif isinstance(pred, RegexPredicate):
        return {"pattern": pred.pattern.pattern}
    elif isinstance(pred, StartsWith):
        return {"pattern": rf"^{re.escape(pred.prefix)}"}
    elif isinstance(pred, EndsWith):
        return {"pattern": rf"{re.escape(pred.suffix)}$"}
    # numbers
    elif isinstance(pred, Min):
        min_t = type(pred.minimum)
        if min_t is Decimal:
            min_ = str(pred.minimum)
        elif min_t is date or min_t is datetime:
            min_ = pred.minimum.isoformat()
        else:
            min_ = pred.minimum
        # non-standard format min / max
        if min_t in {Decimal, date, datetime}:
            return (
                {"formatExclusiveMinimum": min_}
                if pred.exclusive_minimum
                else {"formatMinimum": min_}
            )
        else:
            return (
                {"exclusiveMinimum": min_}
                if pred.exclusive_minimum
                else {"minimum": min_}
            )
    elif isinstance(pred, Max):
        max_t = type(pred.maximum)
        if max_t is Decimal:
            max_ = str(pred.maximum)
        elif max_t is date or max_t is datetime:
            max_ = pred.maximum.isoformat()
        else:
            max_ = pred.maximum

        # non-standard format min / max
        if max_t in {Decimal, date, datetime}:
            return (
                {"formatExclusiveMaximum": max_}
                if pred.exclusive_maximum
                else {"formatMaximum": max_}
            )
        else:
            return (
                {"exclusiveMaximum": max_}
                if pred.exclusive_maximum
                else {"maximum": max_}
            )
    elif isinstance(pred, EqualTo):
        # todo: is there a better way to do this than using enum?
        match_t = type(pred.match)
        if (
            match_t is str
            or match_t is int
            or match_t is None
            or match_t is float
            or match_t is bool
        ):
            choice = pred.match
        elif match_t is date:
            choice = pred.match.isoformat()
        elif match_t is datetime:
            choice = pred.match.isoformat()
        elif match_t is Decimal:
            choice = str(pred.match)
        elif match_t is UUID:
            choice = str(pred.match)
        elif match_t is bytes:
            choice = pred.match.decode("utf-8")
        else:
            raise TypeError(f"got unexpected type: {type(pred.match)}")

        return {"enum": [choice]}
    # objects
    elif isinstance(pred, MinKeys):
        return {"minProperties": pred.size}
    elif isinstance(pred, MaxKeys):
        return {"maxProperties": pred.size}
    # arrays
    elif isinstance(pred, MinItems):
        return {"minItems": pred.item_count}
    elif isinstance(pred, MaxItems):
        return {"maxItems": pred.item_count}
    elif isinstance(pred, UniqueItems):
        return {"uniqueItems": True}
    else:
        unhandled_type(pred)


def generate_schema_validator(
    to_schema_fn: ValidatorToSchema, obj: Validator[Any]
) -> Dict[str, Serializable]:
    r"""
    Produces a JSON Schema compatible Serializable from a ``Validator``

    :param to_schema_fn: the function to use for describing the Validator at the next
        depth -- for nested ``Validator``\s, ``Predicate``\s, and ``PredicateAsync``\s
    :param obj: the ``Validator`` being described
    :return: a JSON Schema compatible Serializable
    :raises AssertionError: only on a misconfiguration with ``OptionalValidator``\s
    :raises TypeError: if there's no implementation for a given type (this can usually be
        resolved with wrapper functions)
    """
    # caution, mutation below!
    if isinstance(obj, BoolValidator):
        return boolean_schema(to_schema_fn, obj)
    if isinstance(obj, StringValidator):
        return string_schema(to_schema_fn, obj)
    elif isinstance(obj, IntValidator):
        return integer_schema(to_schema_fn, obj)
    elif isinstance(obj, FloatValidator):
        return float_schema(to_schema_fn, obj)
    elif isinstance(obj, OptionalValidator):
        maybe_val_ret = to_schema_fn(obj.non_none_validator)
        if type(maybe_val_ret) is not dict:
            raise AssertionError("must be a dict")
        maybe_val_ret["nullable"] = True
        return maybe_val_ret
    elif isinstance(obj, UUIDValidator):
        return uuid_schema(to_schema_fn, obj)
    elif isinstance(obj, MapValidator):
        return map_of_schema(to_schema_fn, obj)
    elif isinstance(obj, RecordValidator):
        return obj_schema(to_schema_fn, obj)
    elif isinstance(obj, DataclassValidator):
        return dataclass_validator_schema(to_schema_fn, obj)
    elif isinstance(obj, TypedDictValidator):
        return typeddict_validator_schema(to_schema_fn, obj)
    elif isinstance(obj, NamedTupleValidator):
        return namedtuple_validator_schema(to_schema_fn, obj)
    elif isinstance(obj, EqualsValidator):
        return equals_schema(to_schema_fn, obj)
    elif isinstance(obj, KeyNotRequired):
        return to_schema_fn(obj.validator)
    elif isinstance(obj, DictValidatorAny):
        return dict_validator_schema(to_schema_fn, obj)
    elif isinstance(obj, ListValidator):
        return array_of_schema(to_schema_fn, obj)
    elif isinstance(obj, UniformTupleValidator):
        return array_of_schema(to_schema_fn, obj)
    elif isinstance(obj, IsDictValidator):
        return {"type": "object"}
    elif isinstance(obj, UnionValidator):
        return {"oneOf": [to_schema_fn(s) for s in obj.validators]}
    elif isinstance(obj, NTupleValidator):
        return {
            "description": f'a {len(obj.fields)}-tuple of the fields in "prefixItems"',
            "type": "array",
            "additionalItems": False,
            "maxItems": len(obj.fields),
            "minItems": len(obj.fields),
            "prefixItems": [to_schema_fn(s) for s in obj.fields],
        }
    elif isinstance(obj, DateValidator):
        return date_schema(to_schema_fn, obj)
    elif isinstance(obj, DatetimeValidator):
        return datetime_schema(to_schema_fn, obj)
    elif isinstance(obj, DecimalValidator):
        return decimal_schema(to_schema_fn, obj)
    elif isinstance(obj, BytesValidator):
        return bytes_schema(to_schema_fn, obj)
    elif isinstance(obj, CacheValidatorBase):
        return to_schema_fn(obj.validator)
    elif isinstance(obj, Lazy):
        raise TypeError(
            "`Lazy` type was not handled -- perhaps you need to use "
            "`generate_named_schema`?"
        )
    else:
        unhandled_type(obj)


def generate_schema_base(
    obj: Union[Validator[Any], Predicate[Any], PredicateAsync[Any]]
) -> Dict[str, Serializable]:
    if isinstance(obj, Validator):
        return generate_schema_validator(generate_schema_base, obj)
    elif isinstance(obj, (Predicate, PredicateAsync)):
        return generate_schema_predicate(obj)
    else:
        unhandled_type(obj)


def generate_named_schema_base(
    ref_location: str, schema_name: str, obj: AnyValidatorOrPredicate
) -> Dict[str, Serializable]:
    if isinstance(obj, Validator):
        to_schema_fn = partial(generate_named_schema_base, ref_location, schema_name)
        if isinstance(obj, Lazy):
            if obj.recurrent:
                return {"$ref": f"{ref_location}{schema_name}"}
            else:
                # cannot_proceed_from_here since the validator is a thunk
                return {}
        else:
            return generate_schema_validator(to_schema_fn, obj)
    elif isinstance(obj, (Predicate, PredicateAsync)):
        return generate_schema_predicate(obj)
    else:
        unhandled_type(obj)


def to_named_json_schema(
    schema_name: str,
    obj: AnyValidatorOrPredicate,
    ref_location: str = "#/components/schemas/",
) -> Dict[str, Serializable]:
    """
    Produces a ``Serializable`` from a ``Validator``, ``Predicate`` or ``PredicateAsync``
    that conforms to a valid JSON Schema. The root dict's only key is the schema name,
    which has the full JSON Schema as its value.

    :param schema_name: mainly required when recursive objects need to related to
        themselves
    :param obj: the Validator being described
    :param ref_location: where the schema name will be found if/when making a recursive
        reference to it
    :return: a ``Serializable`` compatible with JSON Schema
    """
    return {schema_name: generate_named_schema_base(ref_location, schema_name, obj)}


def to_json_schema(obj: AnyValidatorOrPredicate) -> Dict[str, Serializable]:
    """
    Produces a ``Serializable`` from a ``Validator``, ``Predicate`` or ``PredicateAsync``
    that conforms to a valid JSON Schema.

    :param obj: the Validator being described
    :return: a ``Serializable`` compatible with JSON Schema
    """
    return generate_schema_base(obj)
