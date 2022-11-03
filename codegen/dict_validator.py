from typing import List

from codegen.utils import add_type_vars, get_type_vars  # type: ignore

DICT_KEYS_CHECK_CODE: str = """
        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in self._key_set:
                return self._unknown_keys_err 
"""


def generate_code(num_keys: int) -> str:

    dict_validator_into_signatures: List[str] = []
    dict_validator_fields: List[str] = []
    dict_validator_fields_final: List[str] = []
    ret = """from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Final,
    FrozenSet,
    Generic,
    Hashable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload, 
    Awaitable,
)

from koda import Err, Just, Maybe, Ok, Result, mapping_get, nothing

from koda_validate._generics import A
from koda_validate.typedefs import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
)


OBJECT_ERRORS_FIELD: Final[str] = "__container__"

EXPECTED_DICT_ERR: Final[Err[Serializable]] = Err(
    {OBJECT_ERRORS_FIELD: ["expected a dictionary"]}
)

EXPECTED_MAP_ERR: Final[Err[Serializable]] = Err(
    {OBJECT_ERRORS_FIELD: ["expected a map"]}
)

OK_NOTHING: Final[Result[Maybe[Any], Any]] = Ok(nothing)


def _tuples_to_json_dict(data: List[Tuple[str, Serializable]]) -> Serializable:
    return dict(data)


KEY_MISSING_MSG: Final[Serializable] = ["key missing"]
KEY_MISSING_ERR: Final[Err[Serializable]] = Err(KEY_MISSING_MSG)


class KeyNotRequired(Generic[A]):
    \"""
    For complex type reasons in the KeyValidator defintion,
    this does not subclass Validator (even though it probably should)
    \"""

    def __init__(self, validator: Validator[Any, A, Serializable]):
        self.validator = validator

    def __call__(self, maybe_val: Maybe[Any]) -> Result[Maybe[A], Serializable]:
        if maybe_val is nothing:
            return Ok(maybe_val)
        else:
            if TYPE_CHECKING:  # pragma: no cover
                assert isinstance(maybe_val, Just)
            return self.validator(maybe_val.val).map(Just)

    async def validate_async(
        self, maybe_val: Maybe[Any]
    ) -> Result[Maybe[A], Serializable]:
        if maybe_val is nothing:
            return Ok(maybe_val)
        else:
            if TYPE_CHECKING:  # pragma: no cover
                assert isinstance(maybe_val, Just)
            return (await self.validator.validate_async(maybe_val.val)).map(Just)


KeyValidator = Tuple[
    Hashable,
    Union[
        Validator[Any, A, Serializable],
        # this is NOT a validator intentionally; for typing reasons
        # ONLY intended for using KeyNotRequired
        Callable[[Maybe[Any]], Result[A, Serializable]]
    ]
]

"""
    type_vars = get_type_vars(num_keys)
    ret += add_type_vars(type_vars)

    ret += """

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
        key_validator: Validator[Any, T1, Serializable],
        value_validator: Validator[Any, T2, Serializable],
        *,
        predicates: Optional[List[Predicate[Dict[T1, T2], Serializable]]] = None,
        predicates_async: Optional[
            List[PredicateAsync[Dict[T1, T2], Serializable]]
        ] = None,
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
    ) -> None:
        self.key_validator = key_validator
        self.value_validator = value_validator
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def __call__(self, val: Any) -> Result[Dict[T1, T2], Serializable]:
        if isinstance(val, dict):
            if self.preprocessors is not None:
                for preproc in self.preprocessors:
                    val = preproc(val)

            return_dict: Dict[T1, T2] = {}
            errors: Dict[str, Serializable] = {}
            for key, val_ in val.items():
                key_result = self.key_validator(key)
                val_result = self.value_validator(val_)

                if isinstance(key_result, Ok) and isinstance(val_result, Ok):
                    return_dict[key_result.val] = val_result.val
                else:
                    err_key = str(key)
                    if isinstance(key_result, Err):
                        errors[err_key] = {"key_error": key_result.val}

                    if isinstance(val_result, Err):
                        err_dict = {"value_error": val_result.val}
                        errs: Maybe[Serializable] = mapping_get(errors, err_key)
                        if isinstance(errs, Just) and isinstance(errs.val, dict):
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
                    if isinstance(result, Err):
                        dict_validator_errors.append(result.val)

            if len(dict_validator_errors) > 0:
                # in case somehow there are already errors in this field
                if OBJECT_ERRORS_FIELD in errors:
                    dict_validator_errors.append(errors[OBJECT_ERRORS_FIELD])

                errors[OBJECT_ERRORS_FIELD] = dict_validator_errors

            if errors:
                return Err(errors)
            else:
                return Ok(return_dict)
        else:
            return EXPECTED_MAP_ERR

    async def validate_async(self, val: Any) -> Result[Dict[T1, T2], Serializable]:
        if isinstance(val, dict):
            if self.preprocessors is not None:
                for preproc in self.preprocessors:
                    val = preproc(val)

            return_dict: Dict[T1, T2] = {}
            errors: Dict[str, Serializable] = {}

            for key, val_ in val.items():
                key_result = await self.key_validator.validate_async(key)
                val_result = await self.value_validator.validate_async(val_)

                if isinstance(key_result, Ok) and isinstance(val_result, Ok):
                    return_dict[key_result.val] = val_result.val
                else:
                    err_key = str(key)
                    if isinstance(key_result, Err):
                        errors[err_key] = {"key_error": key_result.val}

                    if isinstance(val_result, Err):
                        err_dict = {"value_error": val_result.val}
                        errs: Maybe[Serializable] = mapping_get(errors, err_key)
                        if isinstance(errs, Just) and isinstance(errs.val, dict):
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
                    if isinstance(result, Err):
                        dict_validator_errors.append(result.val)

            if self.predicates_async is not None:
                for pred_async in self.predicates_async:
                    result = await pred_async.validate_async(val)
                    if isinstance(result, Err):
                        dict_validator_errors.append(result.val)

            if len(dict_validator_errors) > 0:
                # in case somehow there are already errors in this field
                if OBJECT_ERRORS_FIELD in errors:
                    dict_validator_errors.append(errors[OBJECT_ERRORS_FIELD])

                errors[OBJECT_ERRORS_FIELD] = dict_validator_errors

            if errors:
                return Err(errors)
            else:
                return Ok(return_dict)
        else:
            return EXPECTED_MAP_ERR


class IsDictValidator(Validator[Any, Dict[Any, Any], Serializable]):
    def __call__(self, val: Any) -> Result[Dict[Any, Any], Serializable]:
        if isinstance(val, dict):
            return Ok(val)
        else:
            return EXPECTED_DICT_ERR

    async def validate_async(self, val: Any) -> Result[Dict[Any, Any], Serializable]:
        if isinstance(val, dict):
            return Ok(val)
        else:
            return EXPECTED_DICT_ERR


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


def _make_keys_err(keys: FrozenSet[Hashable]) -> Err[Serializable]:
    return Err({
        OBJECT_ERRORS_FIELD: [
            "Received unknown keys. " + (
                "Expected empty dictionary."
                if len(keys) == 0
                else "Only expected " + ", ".join(
                    sorted([repr(k) for k in keys])
                ) + "."
            )
        ]
    })

"""
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
class DictValidator(
    Validator[Any, Ret, Serializable]
):
    __slots__ = ("keys", "_key_set", "into", "preprocessors", "validate_object", "validate_object_async")
    __match_args__ = ("keys", "into", "preprocessors", "validate_object", "validate_object_async")

"""
    for i in range(num_keys):
        ret += f"""
    @overload
    def __init__(self,
                 *,
                 into: Callable[[{",".join(type_vars[:i+1])}], Ret],
                 keys: Tuple[
"""
        for j in range(i + 1):
            ret += f"                     {dict_validator_fields[j]},\n"
        ret += """                 ],
                 validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
                 validate_object_async: Optional[Callable[[Ret], Awaitable[Result[Ret, Serializable]]]] = None,
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
        validate_object_async: Optional[Callable[[Ret], Awaitable[Result[Ret, Serializable]]]] = None,
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None
    ) -> None:
"""
    ret += f"""
        self.into = into
        self.keys = keys
         # so we don't need to calculate each time we validate
        _key_set = frozenset(k for k, _ in keys)
        self._key_set = _key_set

        self._unknown_keys_err = _make_keys_err(_key_set)
 
        if validate_object is not None and validate_object_async is not None:
            raise AssertionError(
                "validate_object and validate_object_async cannot both be defined"
            )
        self.validate_object = validate_object
        self.validate_object_async = validate_object_async
        self.preprocessors = preprocessors

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        if not isinstance(data, dict):
            return EXPECTED_DICT_ERR
            
        if self.preprocessors is not None:
            for preproc in self.preprocessors:
                data = preproc(data)
{DICT_KEYS_CHECK_CODE}
        args = []
        errs: Optional[List[Tuple[str, Serializable]]] = None
        for key_, validator in self.keys:
                    args = []
        errs: List[Tuple[str, Serializable]] = []
        for key_, validator in self.keys:
            if key_ in data:
                if isinstance(validator, Validator):
                    result = validator(data[key_])
                else:
                    result = validator(Just(data[key_]))

                if isinstance(result, Err):
                    errs.append((str(key_), result.val))
                else:
                    args.append(result.val)

            else:
                if isinstance(validator, Validator):
                    errs.append((str(key_), KEY_MISSING_MSG))
                else:
                    args.append(nothing)  # type: ignore


        if errs and len(errs) > 0:
            return Err(_tuples_to_json_dict(errs))
        else:
            # we know this should be ret
            obj = self.into(*args)  # type: ignore
            if self.validate_object is None:
                return Ok(obj)
            else:
                return self.validate_object(obj)
                 
    async def validate_async(self, data: Any) -> Result[Ret, Serializable]:
        if not isinstance(data, dict):
            return EXPECTED_DICT_ERR

        if self.preprocessors is not None:
            for preproc in self.preprocessors:
                data = preproc(data)
{DICT_KEYS_CHECK_CODE}
        args = []
        errs: List[Tuple[str, Serializable]] = []
        for key_, validator in self.keys:
            if key_ in data:
                if isinstance(validator, Validator):
                    result = await validator.validate_async(data[key_])
                else:
                    result = await validator.validate_async(Just(data[key_]))  # type: ignore

                # (slightly) optimized; can be simplified if needed
                if isinstance(result, Err):
                    errs.append((str(key_), result.val))
                else:
                    args.append(result.val)
            else:
                if isinstance(validator, Validator):
                    errs.append((str(key_), KEY_MISSING_MSG))
                else:
                    args.append(nothing)
        
        if errs and len(errs) > 0:
            return Err(_tuples_to_json_dict(errs))
        else:
            # we know this should be ret
            obj = self.into(*args) 
            if self.validate_object is not None:
                return self.validate_object(obj)
            elif self.validate_object_async is not None:
                return await self.validate_object_async(obj)
            else:
                return Ok(obj)


class DictValidatorAny(Validator[Any, Any, Serializable]):
    \"""
    This differs from DictValidator in a few ways:
    - if valid, it returns a dict; it does not allow another target to be specified
    - it does not narrow the types of keys / values. It always returns
    `Dict[Hashable, Any]`
    - it allows for any number of `KeyValidator`s

    This class exists for two reasons:
    - because the overloads we use to define `DictValidator` get very slow
    for type checkers beyond a certain point, sa we have a max number of
    type-checkable keys
    - if you don't care about the types in the target object

    VALIDATION WILL STILL WORK PROPERLY, but there won't be much type hinting
    assistance.
    \"""

    __slots__ = ("keys", "_key_set", "preprocessors", "validate_object", "validate_object_async")
    __match_args__ = ("keys", "preprocessors", "validate_object", "validate_object_async")

    def __init__(
        self,
        *,
        keys: Tuple[KeyValidator[Any], ...],
        validate_object: Optional[
            Callable[[Dict[Hashable, Any]], Result[Dict[Hashable, Any], Serializable]]
        ] = None,
        validate_object_async: Optional[
            Callable[
                [Dict[Hashable, Any]],
                Awaitable[Result[Dict[Hashable, Any], Serializable]],
            ]
        ] = None,
        preprocessors: Optional[List[Processor[Dict[Any, Any]]]] = None,
    ) -> None:
        self.keys: Tuple[KeyValidator[Any], ...] = keys
        # so we don't need to calculate each time we validate
        _key_set = frozenset(k for k, _ in keys)
        self._key_set = _key_set

        self._unknown_keys_err = _make_keys_err(_key_set)
        
        self.validate_object = validate_object
        self.validate_object_async = validate_object_async

        if validate_object is not None and validate_object_async is not None:
            raise AssertionError(
                "validate_object and validate_object_async cannot both be defined"
            )
        self.preprocessors = preprocessors

    def __call__(self, data: Any) -> Result[Dict[Hashable, Any], Serializable]:
        if not isinstance(data, dict):
            return EXPECTED_DICT_ERR
            
        if self.preprocessors is not None:
            for preproc in self.preprocessors:
                data = preproc(data)
{DICT_KEYS_CHECK_CODE} 
"""
    ret += (
        """
        success_dict: Dict[Hashable, Any] = {}
        errs: Optional[List[Tuple[str, Serializable]]] = None
        for key_, validator in self.keys:
            if key_ in data:
                if isinstance(validator, Validator):
                    result = validator(data[key_])
                else:
                    result = validator(Just(data[key_]))

            else:
                if isinstance(validator, Validator):
                    result = KEY_MISSING_ERR
                else:
                    result = OK_NOTHING

            # (slightly) optimized; can be simplified if needed
            if isinstance(result, Err):
                err = (str(key_), result.val)
                if errs is None:
                    errs = [err]
                else:
                    errs.append(err)
            elif errs is None:
                success_dict[key_] = result.val

        if errs and len(errs) > 0:
            return Err(_tuples_to_json_dict(errs))
        else:
            if self.validate_object is None:
                return Ok(success_dict)
            else:
                return self.validate_object(success_dict)

    async def validate_async(
        self, data: Any
    ) -> Result[Dict[Hashable, Any], Serializable]:
        if not isinstance(data, dict):
            return EXPECTED_DICT_ERR

        if self.preprocessors is not None:
            for preproc in self.preprocessors:
                data = preproc(data)
"""
        + DICT_KEYS_CHECK_CODE
        + """
        success_dict: Dict[Hashable, Any] = {}
        errs: Optional[List[Tuple[str, Serializable]]] = None
        for key_, validator in self.keys:
            if key_ in data:
                if isinstance(validator, Validator):
                    result = await validator.validate_async(data[key_])
                else:
                    # ignore because it's difficult to make `validate_async` 
                    # apparent to KeyValidator...
                    result = await validator.validate_async(    # type: ignore
                        Just(data[key_])
                    )

            else:
                if isinstance(validator, Validator):
                    result = KEY_MISSING_ERR
                else:
                    result = OK_NOTHING

            # (slightly) optimized; can be simplified if needed
            if isinstance(result, Err):
                err = (str(key_), result.val)
                if errs is None:
                    errs = [err]
                else:
                    errs.append(err)
            elif errs is None:
                success_dict[key_] = result.val

        if errs and len(errs) > 0:
            return Err(_tuples_to_json_dict(errs))
        else:
            if self.validate_object is not None:
                return self.validate_object(success_dict)
            elif self.validate_object_async is not None:
                return await self.validate_object_async(success_dict)
            else:
                return Ok(success_dict)

"""
    )
    return ret


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="generate code.")
    parser.add_argument("--max_keys", type=int, default=20)
    args = parser.parse_args()

    print(generate_code(args.max_keys))
