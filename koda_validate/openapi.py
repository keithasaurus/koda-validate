from typing import Any, Dict, List, NoReturn, Union

from koda_validate.serialization import JsonSerializable
from koda_validate.typedefs import PredicateValidator, TransformableValidator

from koda_validate.validation import Obj1, Obj2, Obj3, Obj4, Obj5, Obj6, Obj7, Obj8, Obj9, Obj10, String, Integer, \
    Float, OneOf3, OneOf2, Tuple2, RequiredField, MaybeField, MapOf, Boolean, ArrayOf, MaxLength, Email, MinLength, \
    Enum, NotBlank, RegexValidator, Minimum, Maximum, MinProperties, MaxProperties, MinItems, MaxItems, UniqueItems, \
    Nullable, Lazy, Tuple3


def unhandled_type(obj: Any) -> NoReturn:
    raise TypeError(f"type {type(obj)} not handled")


def string_schema(schema_name: str, validator: String) -> Dict[str, JsonSerializable]:
    ret: Dict[str, JsonSerializable] = {"type": "string"}
    for sub_validator in validator.validators:
        ret.update(generate_schema_base(schema_name, sub_validator))

    return ret


def integer_schema(
    schema_name: str, validator: Integer
) -> Dict[str, JsonSerializable]:
    ret: Dict[str, JsonSerializable] = {"type": "integer"}
    for sub_validator in validator.validators:
        ret.update(generate_schema_base(schema_name, sub_validator))
    return ret


def float_schema(schema_name: str, validator: Float) -> Dict[str, JsonSerializable]:
    ret: Dict[str, JsonSerializable] = {"type": "number"}
    for sub_validator in validator.validators:
        ret.update(generate_schema_base(schema_name, sub_validator))
    return ret


def boolean_schema(
    schema_name: str, validator: Boolean
) -> Dict[str, JsonSerializable]:
    ret: Dict[str, JsonSerializable] = {"type": "boolean"}
    for sub_validator in validator.validators:
        ret.update(generate_schema_base(schema_name, sub_validator))
    return ret


def array_of_schema(
    schema_name: str, validator: ArrayOf[Any]
) -> Dict[str, JsonSerializable]:
    ret: Dict[str, JsonSerializable] = {
        "type": "array",
        "items": generate_schema_base(schema_name, validator.item_validator),
    }

    for sub_validator in validator.list_validators:
        ret.update(generate_schema_base(schema_name, sub_validator))

    return ret


def obj_schema(
    schema_name: str,
    obj: Union[
        Obj1[Any, Any],
        Obj2[Any, Any, Any],
        Obj3[Any, Any, Any, Any],
        Obj4[Any, Any, Any, Any, Any],
        Obj5[Any, Any, Any, Any, Any, Any],
        Obj6[Any, Any, Any, Any, Any, Any, Any],
        Obj7[Any, Any, Any, Any, Any, Any, Any, Any],
        Obj8[Any, Any, Any, Any, Any, Any, Any, Any, Any],
        Obj9[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any],
        Obj10[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any],
    ],
) -> Dict[str, JsonSerializable]:
    required: List[str] = []
    properties: Dict[str, JsonSerializable] = {}
    for label, field in obj.fields:
        if isinstance(field, RequiredField):
            required.append(label)
        if isinstance(field, (RequiredField, MaybeField)):
            properties[label] = generate_schema_base(schema_name, field.validator)
        else:
            # TODO: is this correct? has the result of this for "some-label":
            #   {"properties: {"some-label": {}, ...}}
            properties[label] = {}

    return {
        "type": "object",
        "additionalProperties": False,
        # ignoring because of a mypy bug where it doesn't understnad List[str] can be
        #   JsonSerializable; as of mypy 0.812
        "required": required,  # type: ignore
        "properties": properties,
    }


def map_of_schema(
    schema_name: str, obj: MapOf[Any, Any]
) -> Dict[str, JsonSerializable]:
    ret: Dict[str, JsonSerializable] = {
        "type": "object",
        "additionalProperties": generate_schema_base(schema_name, obj.value_validator),
    }

    for dict_validator in obj.dict_validators:
        ret.update(generate_schema_base(schema_name, dict_validator))

    return ret


def generate_schema_predicate(
    validator: PredicateValidator[Any, Any]
) -> Dict[str, JsonSerializable]:
    # strings
    if isinstance(validator, Email):
        return {"format": "email"}
    elif isinstance(validator, MaxLength):
        return {"maxLength": validator.length}
    elif isinstance(validator, MinLength):
        return {"minLength": validator.length}
    elif isinstance(validator, Enum):
        return {"enum": list(sorted(validator.choices))}
    elif isinstance(validator, NotBlank):
        return {"pattern": r"^(?!\s*$).+"}
    elif isinstance(validator, RegexValidator):
        return {"pattern": validator.pattern.pattern}
    # enums
    elif isinstance(validator, Enum):
        return {"enum": list(sorted(validator.choices))}
    # numbers
    elif isinstance(validator, Minimum):
        return {
            "minimum": validator.minimum,
            "exclusiveMinimum": validator.exclusive_minimum,
        }
    elif isinstance(validator, Maximum):
        return {
            "maximum": validator.maximum,
            "exclusiveMaximum": validator.exclusive_maximum,
        }
    # objects
    elif isinstance(validator, MinProperties):
        return {"minProperties": validator.size}
    elif isinstance(validator, MaxProperties):
        return {"maxProperties": validator.size}
    # arrays
    elif isinstance(validator, MinItems):
        return {"minItems": validator.length}
    elif isinstance(validator, MaxItems):
        return {"maxItems": validator.length}
    elif isinstance(validator, UniqueItems):
        return {"uniqueItems": True}
    else:
        unhandled_type(validator)


def generate_schema_transformable(
    schema_name: str, obj: TransformableValidator[Any, Any, Any]
) -> Dict[str, JsonSerializable]:
    # caution, mutation below!
    if isinstance(obj, Boolean):
        return boolean_schema(schema_name, obj)
    if isinstance(obj, String):
        return string_schema(schema_name, obj)
    elif isinstance(obj, Integer):
        return integer_schema(schema_name, obj)
    elif isinstance(obj, Float):
        return float_schema(schema_name, obj)
    elif isinstance(obj, Nullable):
        maybe_val_ret = generate_schema_base(schema_name, obj.validator)
        assert isinstance(maybe_val_ret, dict)
        maybe_val_ret["nullable"] = True
        return maybe_val_ret
    elif isinstance(obj, MapOf):
        return map_of_schema(schema_name, obj)
    elif isinstance(
        obj,
        (
            Obj1,
            Obj2,
            Obj3,
            Obj4,
            Obj5,
            Obj6,
            Obj7,
            Obj8,
            Obj9,
            Obj10,
        ),
    ):
        return obj_schema(schema_name, obj)
    elif isinstance(obj, ArrayOf):
        return array_of_schema(schema_name, obj)
    elif isinstance(obj, Lazy):
        if obj.recurrent:
            return {"$ref": f"#/components/schemas/{schema_name}"}
        else:
            return generate_schema_base(schema_name, obj.validator)
    elif isinstance(obj, OneOf2):
        return {
            "oneOf": [
                generate_schema_base(schema_name, s)
                for s in [obj.variant_one, obj.variant_two]
            ]
        }
    elif isinstance(obj, OneOf3):
        return {
            "oneOf": [
                generate_schema_base(schema_name, s)
                for s in [obj.variant_one, obj.variant_two, obj.variant_three]
            ]
        }
    elif isinstance(obj, Tuple2):
        return {
            "description": 'a 2-tuple; schemas for slots are listed in order in "items" > "anyOf"',
            "type": "array",
            "maxItems": 2,
            "items": {
                "anyOf": [
                    generate_schema_base(schema_name, s)
                    for s in [obj.slot1_validator, obj.slot2_validator]
                ]
            },
        }
    elif isinstance(obj, Tuple3):
        return {
            "description": 'a 3-tuple; schemas for slots are listed in order in "items" > "anyOf"',
            "type": "array",
            "maxItems": 3,
            "items": {
                "anyOf": [
                    generate_schema_base(schema_name, s)
                    for s in [
                        obj.slot1_validator,
                        obj.slot2_validator,
                        obj.slot3_validator,
                    ]
                ]
            },
        }
    else:
        unhandled_type(obj)


def generate_schema_base(schema_name: str, obj: Any) -> Dict[str, JsonSerializable]:
    if isinstance(obj, TransformableValidator):
        return generate_schema_transformable(schema_name, obj)
    elif isinstance(obj, PredicateValidator):
        return generate_schema_predicate(obj)
    else:
        unhandled_type(obj)


def generate_schema(schema_name: str, obj: Any) -> Dict[str, JsonSerializable]:
    return {schema_name: generate_schema_base(schema_name, obj)}
