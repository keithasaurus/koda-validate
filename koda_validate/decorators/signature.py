import functools
import inspect
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)

from koda_validate import *
from koda_validate.typehints import get_typehint_validator

_BaseDecoratedFunc = Callable[..., Any]
DecoratedFunc = TypeVar("DecoratedFunc", bound=_BaseDecoratedFunc)


def _wrap_fn(
    func: DecoratedFunc,
    ignore_return: bool,
    typehint_resolver: Callable[[Any], Validator[Any]],
) -> DecoratedFunc:
    sig = inspect.signature(func)
    schema: dict[str, Validator[Any]] = {}

    kwargs_validator: Optional[Validator[Any]] = None
    var_args_key_and_validator: Optional[Tuple[str, Validator[Any]]] = None
    positional_args_names: Set[str] = set()

    positional_validators: List[Optional[Tuple[str, Validator[Any]]]] = []
    for key, param in sig.parameters.items():
        # if param.annotation != param.empty:
        if param.kind == param.POSITIONAL_ONLY:
            positional_args_names.add(key)
            if param.annotation == param.empty:
                positional_validators.append(None)
            else:
                positional_validators.append((key, typehint_resolver(param.annotation)))
        if param.kind == param.POSITIONAL_OR_KEYWORD:
            positional_args_names.add(key)
            if param.annotation == param.empty:
                positional_validators.append(None)
            else:
                validator = typehint_resolver(param.annotation)
                positional_validators.append((key, validator))
                schema[key] = validator
        if param.kind == param.VAR_POSITIONAL:
            if param.annotation != param.empty:
                var_args_key_and_validator = key, typehint_resolver(param.annotation)
        if param.kind == param.KEYWORD_ONLY:
            if param.annotation != param.empty:
                schema[key] = typehint_resolver(param.annotation)

        if param.kind == param.VAR_KEYWORD:
            if param.annotation != param.empty:
                kwargs_validator = typehint_resolver(param.annotation)
            else:
                schema[key] = typehint_resolver(param.annotation)

    if not ignore_return and sig.return_annotation != sig.empty:
        return_validator: Optional[Validator[Any]] = typehint_resolver(
            sig.return_annotation
        )
    else:
        return_validator = None

    @functools.wraps(func)
    def inner(*args: Any, **kwargs: Any) -> Any:
        errs: Dict[str, Invalid] = {}
        var_args_errs: List[Tuple[Any, Invalid]] = []
        for i, arg in enumerate(args):
            if len(positional_validators) >= i + 1:
                arg_details = positional_validators[i]
                if arg_details is None:
                    # not an annotated argument
                    continue
                else:
                    key, arg_validator = arg_details
                    if not (result := arg_validator(arg)).is_valid:
                        errs[key] = result

            else:
                if var_args_key_and_validator:
                    var_args_key, var_args_validator = var_args_key_and_validator
                    if not (var_args_result := var_args_validator(arg)).is_valid:
                        var_args_errs.append((arg, var_args_result))

        if var_args_errs and var_args_key_and_validator:
            errs[var_args_key_and_validator[0]] = Invalid(
                IndexErrs({i: err_ for i, (_, err_) in enumerate(var_args_errs)}),
                tuple(a for a, _ in var_args_errs),
                var_args_key_and_validator[1],
            )

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
            raise InvalidArgsError(errs)
        elif return_validator:
            result = func(*args, **kwargs)
            if (ret_result := return_validator(result)).is_valid:
                return result
            else:
                raise InvalidReturnError(ret_result)
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


def _trunc_str(s: str, max_chars: int = 50) -> str:
    ellip = "..."
    ellip_len = len(ellip)
    if max_chars < ellip_len:
        raise AssertionError(f"max_chars must be greater than or equal to {ellip_len}")

    return (s[: (max_chars - ellip_len)] + ellip) if len(s) > max_chars else s


def get_arg_fail_message(invalid: Invalid, depth: int = 0, prefix: str = "") -> str:
    err_type = invalid.err_type
    ret = depth * "    " + prefix
    if isinstance(err_type, TypeErr):
        ret += f"expected {err_type.expected_type}; got {_trunc_str(repr(invalid.value))}"
    elif isinstance(err_type, PredicateErrs):
        ret += "failed predicates"
    elif isinstance(err_type, UnionErrs):
        variant_errors = [
            get_arg_fail_message(variant, depth + 1, f"variant {i}: ")
            for i, variant in enumerate(err_type.variants)
        ]
        ret += "\n".join(["Union Errors"] + variant_errors)
    elif isinstance(err_type, KeyErrs):
        ret += "Key Errors\n"
        ret += "\n".join(
            [
                get_arg_fail_message(inv, depth + 1, f"{repr(k)}: ")
                for k, inv in err_type.keys.items()
            ]
        )

    return ret


def get_args_fail_msg(errs: dict[str, Invalid]) -> str:
    messages = [f"{k}: {get_arg_fail_message(v)}" for k, v in errs.items()]
    return "\n" + "\n".join(messages)


class InvalidArgsError(Exception):
    def __init__(self, errs: dict[str, Invalid]) -> None:
        super().__init__(get_args_fail_msg(errs))
        self.errs = errs


class InvalidReturnError(Exception):
    def __init__(self, err: Invalid):
        super().__init__(get_arg_fail_message(err))
        self.err = err
