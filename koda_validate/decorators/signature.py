import functools
import inspect
import typing as t
from datetime import date, datetime
from uuid import UUID

from _decimal import Decimal

from koda_validate import *
from koda_validate.typehints import get_typehint_validator, get_typehint_validator_base

_BaseDecoratedFunc = t.Callable[..., t.Any]
DecoratedFunc = t.TypeVar("DecoratedFunc", bound=_BaseDecoratedFunc)


def validate_signature(
    func: DecoratedFunc,
    *,
    ignore_return: bool = False,
    ignore_args: t.Optional[t.Set[str]] = None,
    typehint_resolver: t.Callable[[t.Any], Validator[t.Any]] = get_typehint_validator,
) -> DecoratedFunc:

    sig = inspect.signature(func)
    schema: dict[str, Validator[t.Any]] = {}

    for key, param in sig.parameters.items():
        if param.annotation == param.empty:
            continue
        else:
            schema[key] = typehint_resolver(param.annotation)

    @functools.wraps(func)
    def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
        errs: t.Dict[str, Invalid] = {}
        for arg, (key, validator) in zip(args, schema.items()):
            if not (result := validator(arg)).is_valid:
                errs[key] = result

        for kw_key, kw_val in kwargs.items():
            if kw_key in schema and not (kw_result := schema[kw_key](kw_val)).is_valid:
                errs[kw_key] = kw_result

        if errs:
            raise InvalidArgs(errs)
        else:
            return t.cast(DecoratedFunc, func(*args, **kwargs))

    return wrapper


def get_arg_fail_message(invalid: Invalid, depth=0, prefix="") -> str:
    err_type = invalid.err_type
    ret = depth * "    " + prefix
    if isinstance(err_type, TypeErr):
        ret += f"expected {err_type.expected_type}; got {type(invalid.value)}"
    elif isinstance(err_type, PredicateErrs):
        ret += "failed predicates"
    elif isinstance(err_type, UnionErrs):
        variant_errors = [
            get_arg_fail_message(variant, depth + 1, f"variant {i}: ")
            for i, variant in enumerate(err_type.variants)
        ]
        ret += "\n".join(["Union Errors"] + variant_errors)

    return ret


class InvalidArgs(Exception):
    def __init__(self, errs: dict[str, Invalid]) -> None:
        messages = [f"{k}: {get_arg_fail_message(v)}" for k, v in errs.items()]
        super().__init__("\n" + "\n".join(messages))
        self.errs = errs
