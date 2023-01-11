import functools
import inspect
from typing import Any, Callable, Dict, Optional, Set, TypeVar, Union, cast, overload

from koda_validate import *
from koda_validate.typehints import get_typehint_validator

_BaseDecoratedFunc = Callable[..., Any]
DecoratedFunc = TypeVar("DecoratedFunc", bound=_BaseDecoratedFunc)

RETURN_VALUE_KEY = "_RETURN_VALUE_"


def _wrap_fn(
    func: DecoratedFunc,
    ignore_return: bool,
    typehint_resolver: Callable[[Any], Validator[Any]],
) -> DecoratedFunc:

    sig = inspect.signature(func)
    schema: dict[str, Validator[Any]] = {}

    kwargs_validator: Optional[Validator[Any]] = None

    for key, param in sig.parameters.items():
        if param.annotation != param.empty:
            if param.kind == param.VAR_KEYWORD:
                schema[key] = MapValidator(
                    key=StringValidator(), value=typehint_resolver(param.annotation)
                )
            else:
                kwargs_validator = typehint_resolver(param.annotation)

    if not ignore_return and sig.return_annotation != sig.empty:
        return_validator: Optional[Validator[Any]] = typehint_resolver(
            sig.return_annotation
        )
    else:
        return_validator = None

    @functools.wraps(func)
    def inner(*args: Any, **kwargs: Any) -> Any:
        errs: Dict[str, Invalid] = {}
        for arg, (key, validator) in zip(args, schema.items()):
            if not (result := validator(arg)).is_valid:
                errs[key] = result

        for kw_key, kw_val in kwargs.items():
            if kw_key in schema:
                if not (kw_result := schema[kw_key](kw_val)).is_valid:
                    errs[kw_key] = kw_result
            elif (
                kwargs_validator
                and not (kwargs_result := kwargs_validator(kw_val)).is_valid
            ):
                errs[kw_key] = kwargs_result

        if errs:
            raise InvalidArgs(errs)
        elif return_validator:
            result = func(*args, **kwargs)
            if (ret_result := return_validator(result)).is_valid:
                return result
            else:
                raise InvalidArgs({RETURN_VALUE_KEY: ret_result})
        else:
            return func(*args, **kwargs)

    return cast(DecoratedFunc, inner)


@overload
def validate_signature(
    func: DecoratedFunc,
    *,
    ignore_return: bool = False,
    ignore_args: Optional[Set[str]] = None,
    typehint_resolver: Callable[[Any], Validator[Any]] = get_typehint_validator,
) -> DecoratedFunc:
    ...


@overload
def validate_signature(
    func: None = None,
    *,
    ignore_return: bool = False,
    ignore_args: Optional[Set[str]] = None,
    typehint_resolver: Callable[[Any], Validator[Any]] = get_typehint_validator,
) -> Callable[[DecoratedFunc], DecoratedFunc]:
    ...


def validate_signature(
    func: Optional[DecoratedFunc] = None,
    *,
    ignore_return: bool = False,
    ignore_args: Optional[Set[str]] = None,
    typehint_resolver: Callable[[Any], Validator[Any]] = get_typehint_validator,
) -> Union[DecoratedFunc, Callable[[DecoratedFunc], DecoratedFunc]]:
    if func is None:

        def inner(func_inner: DecoratedFunc) -> DecoratedFunc:
            return _wrap_fn(
                func_inner,
                ignore_return=ignore_return,
                typehint_resolver=typehint_resolver,
            )

        return inner
    else:
        return _wrap_fn(
            func, ignore_return=ignore_return, typehint_resolver=typehint_resolver
        )


def get_arg_fail_message(invalid: Invalid, depth: int = 0, prefix: str = "") -> str:
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


def get_args_fail_msg(errs: dict[str, Invalid]) -> str:
    messages = [f"{k}: {get_arg_fail_message(v)}" for k, v in errs.items()]
    return "\n" + "\n".join(messages)


class InvalidArgs(Exception):
    def __init__(self, errs: dict[str, Invalid]) -> None:
        super().__init__(get_args_fail_msg(errs))
        self.errs = errs
