from json import dumps, loads
from typing import Any, AnyStr, Dict, List, Tuple, TypeVar, Union

from koda.result import Err, Ok, Result

A = TypeVar("A")

_Scalar = Union[str, int, float, bool, None]


_Deserialized_container = Union[Dict[str, A], List[A]]
_JsonDeserialized3 = Union[_Scalar, _Deserialized_container[Any]]
_JsonDeserialized2 = Union[_Scalar, _Deserialized_container[_JsonDeserialized3]]

# after deserialization
JsonDeserialized = Union[_Scalar, _Deserialized_container[_JsonDeserialized2]]


_Serializable_container = Union[Dict[str, A], List[A], Tuple[A, ...]]
_JsonSerializable3 = Union[_Scalar, _Serializable_container[Any]]
_JsonSerializable2 = Union[_Scalar, _Serializable_container[_JsonSerializable3]]

# can be serialized to json; includes tuples, which are never decoded
JsonSerializable = Union[_Scalar, _Serializable_container[_JsonSerializable2]]

Json = JsonSerializable


def str_to_json(json_str: AnyStr) -> Result[Json, Exception]:
    try:
        return Ok(loads(json_str))
    except Exception as exc:
        return Err(exc)


def str_to_json_deserialized_type(
    json_str: AnyStr,
) -> Result[JsonDeserialized, Exception]:
    try:
        return Ok(loads(json_str))
    except Exception as exc:
        return Err(exc)


def json_to_str(jsonable_obj: Json) -> str:
    return dumps(jsonable_obj)
