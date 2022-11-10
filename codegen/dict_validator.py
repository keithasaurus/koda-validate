from typing import List

from codegen.utils import get_type_vars


def get_dict_keys_check_code(key_source: str) -> str:
    return f"""
        if not isinstance(data, dict):
            return EXPECTED_DICT_ERR
            
        if self.preprocessors:
            for preproc in self.preprocessors:
                data = preproc(data)

        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in {key_source}:
                return self._unknown_keys_err 
"""


def generate_code(num_keys: int) -> str:
    dict_validator_into_signatures: List[str] = []
    dict_validator_fields: List[str] = []
    dict_validator_fields_final: List[str] = []
    type_vars = get_type_vars(num_keys)
    ret = """from typing import (
    Any,
    Callable,
    Dict,
    Final,
    FrozenSet,
    Hashable,
    List,
    Literal,
    Optional,
    Tuple,
    TYPE_CHECKING,
    Union,
    overload,
    Awaitable,
    KeysView,
)

from koda import Just, Maybe, mapping_get, nothing

"""
    import_type_vars = "\n".join(f"    {tv}," for tv in type_vars)
    ret += (
        f""" 
from koda_validate._generics import (
    A,
    {import_type_vars}
    Ret
) 
"""
        + """
from koda_validate._internals import OBJECT_ERRORS_FIELD, _async_predicates_warning
from koda_validate.base import (
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
)
from koda_validate.validated import Invalid, Valid, Validated


EXPECTED_DICT_MSG: Final[Serializable] = {OBJECT_ERRORS_FIELD: ["expected a dictionary"]}
EXPECTED_DICT_ERR: Final[Tuple[Literal[False], Serializable]] = False, EXPECTED_DICT_MSG

EXPECTED_MAP_ERR: Final[Invalid[Serializable]] = Invalid(
    {OBJECT_ERRORS_FIELD: ["expected a map"]}
)

VALID_NOTHING: Final[Validated[Maybe[Any], Any]] = Valid(nothing)

KEY_MISSING_MSG: Final[Serializable] = ["key missing"]
KEY_MISSING_ERR: Final[Invalid[Serializable]] = Invalid(KEY_MISSING_MSG)

class KeyNotRequired(Validator[Any, Maybe[A], Serializable]):
    \"""
    For complex type reasons in the KeyValidator definition,
    this does not subclass Validator (even though it probably should)
    \"""

    def __init__(self, validator: Validator[Any, A, Serializable]):
        self.validator = validator

    def __call__(self, val: Any) -> Validated[Maybe[A], Serializable]:
        return self.validator(val).map(Just)

    async def validate_async(self, val: Any) -> Validated[Maybe[A], Serializable]:
        return (await self.validator.validate_async(val)).map(Just)


KeyValidator = Tuple[
    Hashable,
    Validator[Any, A, Serializable],
]


class MapValidator(Validator[Any, Dict[T1, T2], Serializable]):
    __slots__ = (
        "key_validator",
        "value_validator",
        "predicates",
        "predicates_async",
        "preprocessors",
    )
    __match_args__ = (
        "key_validator",
        "value_validator",
        "predicates",
        "predicates_async",
        "preprocessors",
    )

    def __init__(
        self,
        *,
        key: Validator[Any, T1, Serializable],
        value: Validator[Any, T2, Serializable],
        predicates: Optional[List[Predicate[Dict[T1, T2], Serializable]]] = None,
        predicates_async: Optional[
            List[PredicateAsync[Dict[T1, T2], Serializable]]
        ] = None,
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
    ) -> None:
        self.key_validator = key
        self.value_validator = value
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def __call__(self, val: Any) -> Validated[Dict[T1, T2], Serializable]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if isinstance(val, dict):
            if self.preprocessors is not None:
                for preproc in self.preprocessors:
                    val = preproc(val)

            return_dict: Dict[T1, T2] = {}
            errors: Dict[str, Serializable] = {}
            for key, val_ in val.items():
                key_result = self.key_validator(key)
                val_result = self.value_validator(val_)

                if key_result.is_valid and val_result.is_valid:
                    return_dict[key_result.val] = val_result.val
                else:
                    err_key = str(key)
                    if not key_result.is_valid:
                        errors[err_key] = {"key_error": key_result.val}

                    if not val_result.is_valid:
                        err_dict = {"value_error": val_result.val}
                        errs: Maybe[Serializable] = mapping_get(errors, err_key)
                        if errs.is_just and isinstance(errs.val, dict):
                            errs.val.update(err_dict)
                        else:
                            errors[err_key] = err_dict

            dict_validator_errors: List[Serializable] = []
            if self.predicates is not None:
                for predicate in self.predicates:
                    # Note that the expectation here is that validators will likely
                    # be doing json like number of keys; they aren't expected
                    # to be drilling down into specific keys and values. That may be
                    # an incorrect assumption; if so, some minor refactoring is probably
                    # necessary.
                    result = predicate(val)
                    if not result.is_valid:
                        dict_validator_errors.append(result.val)

            if len(dict_validator_errors) > 0:
                # in case somehow there are already errors in this field
                if OBJECT_ERRORS_FIELD in errors:
                    dict_validator_errors.append(errors[OBJECT_ERRORS_FIELD])

                errors[OBJECT_ERRORS_FIELD] = dict_validator_errors

            if errors:
                return Invalid(errors)
            else:
                return Valid(return_dict)
        else:
            return EXPECTED_MAP_ERR

    async def validate_async(self, val: Any) -> Validated[Dict[T1, T2], Serializable]:
        if isinstance(val, dict):
            if self.preprocessors is not None:
                for preproc in self.preprocessors:
                    val = preproc(val)

            return_dict: Dict[T1, T2] = {}
            errors: Dict[str, Serializable] = {}

            for key, val_ in val.items():
                key_result = await self.key_validator.validate_async(key)
                val_result = await self.value_validator.validate_async(val_)

                if key_result.is_valid and val_result.is_valid:
                    return_dict[key_result.val] = val_result.val
                else:
                    err_key = str(key)
                    if not key_result.is_valid:
                        errors[err_key] = {"key_error": key_result.val}

                    if not val_result.is_valid:
                        err_dict = {"value_error": val_result.val}
                        errs: Maybe[Serializable] = mapping_get(errors, err_key)
                        if errs.is_just and isinstance(errs.val, dict):
                            errs.val.update(err_dict)
                        else:
                            errors[err_key] = err_dict

            dict_validator_errors: List[Serializable] = []
            if self.predicates is not None:
                for predicate in self.predicates:
                    # Note that the expectation here is that validators will likely
                    # be doing json like number of keys; they aren't expected
                    # to be drilling down into specific keys and values. That may be
                    # an incorrect assumption; if so, some minor refactoring is probably
                    # necessary.
                    result = predicate(val)
                    if not result.is_valid:
                        dict_validator_errors.append(result.val)

            if self.predicates_async is not None:
                for pred_async in self.predicates_async:
                    result = await pred_async.validate_async(val)
                    if not result.is_valid:
                        dict_validator_errors.append(result.val)

            if len(dict_validator_errors) > 0:
                # in case somehow there are already errors in this field
                if OBJECT_ERRORS_FIELD in errors:
                    dict_validator_errors.append(errors[OBJECT_ERRORS_FIELD])

                errors[OBJECT_ERRORS_FIELD] = dict_validator_errors

            if errors:
                return Invalid(errors)
            else:
                return Valid(return_dict)
        else:
            return EXPECTED_MAP_ERR


class IsDictValidator(_ToTupleValidatorUnsafe[Any, Dict[Any, Any], Serializable]):
    def validate_to_tuple(self, val: Any) -> _ResultTupleUnsafe:
        if isinstance(val, dict):
            return True, val
        else:
            return EXPECTED_DICT_ERR

    async def validate_to_tuple_async(self, val: Any) -> _ResultTupleUnsafe:
        return self.validate_to_tuple(val) 


is_dict_validator = IsDictValidator()


class MinKeys(Predicate[Dict[Any, Any], Serializable]):
    __slots__ = ("size",)
    __match_args__ = ("size",)

    def __init__(self, size: int) -> None:
        self.size = size

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) >= self.size

    def err(self, val: Dict[Any, Any]) -> str:
        return f"minimum allowed properties is {self.size}"


class MaxKeys(Predicate[Dict[Any, Any], Serializable]):
    __slots__ = ("size",)
    __match_args__ = ("size",)

    def __init__(self, size: int) -> None:
        self.size = size

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) <= self.size

    def err(self, val: Dict[Any, Any]) -> str:
        return f"maximum allowed properties is {self.size}"


def _make_keys_err(keys: Union[FrozenSet[Hashable], KeysView[Hashable]]) -> Serializable:
    return {
        OBJECT_ERRORS_FIELD: [
            "Received unknown keys. " + (
                "Expected empty dictionary."
                if len(keys) == 0
                else "Only expected " + ", ".join(
                    sorted([repr(k) for k in keys])
                ) + "."
            )
        ]
    }

"""
    )
    for i in range(num_keys):
        key_type_vars = type_vars[: i + 1]
        generic_vals = ", ".join(key_type_vars)
        dict_validator_into_signatures.append(f"Callable[[{generic_vals}], Ret]")

        dict_validator_fields.append(f"KeyValidator[{type_vars[i]}]")
        final_tuple_fields = [
            f"            KeyValidator[{type_vars[j]}]" for j in range(i + 1)
        ]
        dict_validator_fields_final.append(
            "Tuple[" + ",\n".join(final_tuple_fields) + "]"
        )

    ret += """
class RecordValidator(
    _ToTupleValidatorUnsafe[Any, Ret, Serializable]
):
    __slots__ = ("_fast_keys", "_key_set", "keys", "into", "preprocessors", "validate_object", "validate_object_async")
    __match_args__ = ("keys", "into", "preprocessors", "validate_object", "validate_object_async")

"""
    for i in range(num_keys):
        ret += f"""
    @overload
    def __init__(self,
                 *,
                 into: Callable[[{",".join(type_vars[:i + 1])}], Ret],
                 keys: Tuple[
"""
        for j in range(i + 1):
            ret += f"                     {dict_validator_fields[j]},\n"
        ret += """                 ],
                 validate_object: Optional[Callable[[Ret], Validated[Ret, Serializable]]] = None,
                 validate_object_async: Optional[Callable[[Ret], Awaitable[Validated[Ret, Serializable]]]] = None,
                 preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None
                 ) -> None: 
        ...  # pragma: no cover

"""

    dv_fields_2: str = ",\n".join([f"         {f}" for f in dict_validator_fields_final])

    ret += f"""

    def __init__( 
        self,
        into: Union[
            {", ".join(dict_validator_into_signatures)}
        ],
        keys: Union[
    {dv_fields_2},
        ],
        validate_object: Optional[Callable[[Ret], Validated[Ret, Serializable]]] = None,
        validate_object_async: Optional[Callable[[Ret], Awaitable[Validated[Ret, Serializable]]]] = None,
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None
    ) -> None:
"""
    ret += (
        f"""
        self.into = into
        # needs to be `Any` until we have variadic generics presumably
        self.keys: Tuple[KeyValidator[Any], ...] = keys
        if validate_object is not None and validate_object_async is not None:
            raise AssertionError(
                "validate_object and validate_object_async cannot both be defined"
            )
        self.validate_object = validate_object
        self.validate_object_async = validate_object_async
        self.preprocessors = preprocessors

        # so we don't need to calculate each time we validate
        _key_set = frozenset(k for k, _ in keys)
        self._key_set = _key_set
        self._fast_keys = [
            (key,
             val,
             not isinstance(val, KeyNotRequired),
             isinstance(val, _ToTupleValidatorUnsafe),
             str(key)) for key, val in keys
        ]
        self._unknown_keys_err = False, _make_keys_err(_key_set)

    def validate_to_tuple(self, data: Any) -> _ResultTupleUnsafe:
{get_dict_keys_check_code("self._key_set")}

        args: List[Any] = []
        errs: List[Tuple[str, Serializable]] = []
        for key_, validator, key_required, is_tuple_validator, str_key in self._fast_keys:
            try:
                val = data[key_]
            except KeyError:
                if key_required: 
                    errs.append((str_key, KEY_MISSING_MSG))
                else:
                    args.append(nothing)
            else:
                if is_tuple_validator:
                    if TYPE_CHECKING:
                        assert isinstance(validator, _ToTupleValidatorUnsafe)
                    success, new_val = validator.validate_to_tuple(val)  
                else:
                    success, new_val = ( 
                        (True, result_.val)
                        if (result_ := validator(val)).is_valid  # type: ignore
                        else (False, result_.val)
                    )
                
                if not success:
                    errs.append((str_key, new_val))
                elif not errs:
                    args.append(new_val)

        if errs:
            return False, dict(errs)
        else:
            # we know this should be ret
            obj = self.into(*args)
            if self.validate_object is None:
                return True, obj
            else:
                result = self.validate_object(obj)
                if result.is_valid:
                    return True, result.val
                else:
                    return False, result.val


    async def validate_to_tuple_async(self, data: Any) -> _ResultTupleUnsafe:
{get_dict_keys_check_code("self._key_set")}
        args: List[Any] = []
        errs: List[Tuple[str, Serializable]] = []
        for key_, validator, key_required, is_tuple_validator, str_key in self._fast_keys:
            try:
                val = data[key_]
            except KeyError:
                if key_required:
                    errs.append((str_key, KEY_MISSING_MSG))
                else:
                    args.append(nothing)
            else:
                if is_tuple_validator:
                    success, new_val = await validator.validate_to_tuple_async(val)  # type: ignore  # noqa: E501
                else:
                    success, new_val = ( 
                        (True, result_.val)
                        if (result_ := await validator.validate_async(val)).is_valid  # type: ignore  # noqa: E501
                        else (False, result_.val)
                    )

                if not success:
                    errs.append((str_key, new_val))
                elif not errs:
                    args.append(new_val)

        if errs:
            return False, dict(errs)
        else:
            obj = self.into(*args)
            if self.validate_object is not None:
                result = self.validate_object(obj)
                if result.is_valid:
                    return True, result.val
                else:
                    return False, result.val
            elif self.validate_object_async is not None:
                result = await self.validate_object_async(obj)
                if result.is_valid:
                    return True, result.val
                else:
                    return False, result.val
            else:
                return True, obj


class DictValidatorAny(_ToTupleValidatorUnsafe[Any, Any, Serializable]):
    \"""
    This differs from RecordValidator in a few ways:
    - if valid, it returns a dict; it does not allow another target to be specified
    - it does not narrow the types of keys / values. It always returns
    `Dict[Hashable, Any]`
    - it allows for any number of `KeyValidator`s

    This class exists for two reasons:
    - because the overloads we use to define `RecordValidator` get very slow
    for type checkers beyond a certain point, sa we have a max number of
    type-checkable keys
    - if you don't care about the types in the target object

    VALIDATION WILL STILL WORK PROPERLY, but there won't be much type hinting
    assistance.
    \"""

    __slots__ = (
        "schema",
        "_key_set",
        "_fast_keys",
        "_unknown_keys_err",
        "preprocessors",
        "validate_object",
        "validate_object_async",
    )
    __match_args__ = (
        "schema",
        "preprocessors",
        "validate_object",
        "validate_object_async",
    )

    def __init__(
        self,
        schema: Dict[Any, Validator[Any, Any, Serializable]],
        *,
        validate_object: Optional[
            Callable[[Dict[Hashable, Any]], Validated[Dict[Any, Any], Serializable]]
        ] = None,
        validate_object_async: Optional[
            Callable[
                [Dict[Any, Any]],
                Awaitable[Validated[Dict[Any, Any], Serializable]],
            ]
        ] = None,
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
    ) -> None:
        self.schema: Dict[Any, Validator[Any, Any, Serializable]] = schema
        self.validate_object = validate_object
        self.validate_object_async = validate_object_async

        if validate_object is not None and validate_object_async is not None:
            raise AssertionError(
                "validate_object and validate_object_async cannot both be defined"
            )
        self.preprocessors = preprocessors

        # so we don't need to calculate each time we validate
        self._fast_keys = [
            (
                key,
                val,
                not isinstance(val, KeyNotRequired),
                isinstance(val, _ToTupleValidatorUnsafe),
                str(key),
            )
            for key, val in schema.items()
        ]

        self._unknown_keys_err = False, _make_keys_err(schema.keys())

    def validate_to_tuple(self, data: Any) -> _ResultTupleUnsafe:
"""
        + get_dict_keys_check_code("self.schema")
        + """

        success_dict: Dict[Hashable, Any] = {}
        errs: List[Tuple[str, Serializable]] = []
        for key_, validator, key_required, is_tuple_validator, str_key in self._fast_keys:
            try:
                val = data[key_]
            except KeyError:
                if key_required: 
                    errs.append((str_key, KEY_MISSING_MSG))
                elif not errs:
                    success_dict[key_] = nothing
            else:
                if is_tuple_validator:
                    if TYPE_CHECKING:
                        assert isinstance(validator, _ToTupleValidatorUnsafe)
                    success, new_val = validator.validate_to_tuple(val) 
                else:
                    success, new_val = ( 
                        (True, result_.val)
                        if (result_ := validator(val)).is_valid
                        else (False, result_.val)
                    )
                
                if not success:
                    errs.append((str_key, new_val))
                elif not errs:
                    success_dict[key_] = new_val
 
        if errs:
            return False, dict(errs)
        else:
            if self.validate_object is None:
                return True, success_dict
            else:
                vo_result = self.validate_object(success_dict)
                if vo_result.is_valid:
                    return True, vo_result.val
                else:
                    return False, vo_result.val 

    async def validate_to_tuple_async(
        self, data: Any
    ) -> _ResultTupleUnsafe:
"""
        + get_dict_keys_check_code("self.schema")
        + """ 

        success_dict: Dict[Hashable, Any] = {}
        errs: List[Tuple[str, Serializable]] = []
        for key_, validator, key_required, is_tuple_validator, str_key in self._fast_keys:
            try:
                val = data[key_]
            except KeyError:
                if key_required:
                    errs.append((str_key, KEY_MISSING_MSG))
                elif not errs:
                    success_dict[key_] = nothing
            else:
                if is_tuple_validator:
                    if TYPE_CHECKING:
                        assert isinstance(validator, _ToTupleValidatorUnsafe)
                    success, new_val = await validator.validate_to_tuple_async(val)
                else:
                    success, new_val = (
                        (True, result_.val)
                        if (result_ := await validator.validate_async(val)).is_valid 
                        else (False, result_.val)
                    )

                if not success:
                    errs.append((str_key, new_val))
                elif not errs:
                    success_dict[key_] = new_val

        if errs:
            return False, dict(errs)
        else:
            if self.validate_object is not None:
                result = self.validate_object(success_dict)
                if result.is_valid:
                    return True, result.val
                else:
                    return False, result.val
            elif self.validate_object_async is not None:
                result = await self.validate_object_async(success_dict)
                if result.is_valid:
                    return True, result.val
                else:
                    return False, result.val
            else:
                return True, success_dict 
"""
    )

    return ret


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="generate code.")
    parser.add_argument("--max_keys", type=int, default=20)
    args = parser.parse_args()

    print(generate_code(args.max_keys))
