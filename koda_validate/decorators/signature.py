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
_DecoratedFunc = TypeVar("_DecoratedFunc", bound=_BaseDecoratedFunc)


def _wrap_fn(
    func: _DecoratedFunc,
    ignore_return: bool,
    ignore_args: Set[str],
    typehint_resolver: Callable[[Any], Validator[Any]],
) -> _DecoratedFunc:
    sig = inspect.signature(func)
    # This value is Optional because we need to keep track of all
    # the argument names. For arguments that either a) don't have
    # an annotation, or b) are being ignore, we keep the value as None
    # If we simply didn't store the keys of arguments we're ignoring, we
    # wouldn't be able to tell the difference between a **kwargs key and a
    # defined argument name
    schema: Dict[str, Optional[Validator[Any]]] = {}

    kwargs_validator: Optional[Validator[Any]] = None
    var_args_key_and_validator: Optional[Tuple[str, Validator[Any]]] = None
    positional_args_names: Set[str] = set()
    positional_validators: List[Optional[Tuple[str, Validator[Any]]]] = []

    # create arg schema
    for key, param in sig.parameters.items():
        if param.kind == param.POSITIONAL_ONLY:
            positional_args_names.add(key)
            if param.annotation == param.empty or key in ignore_args:
                positional_validators.append(None)
            else:
                positional_validators.append((key, typehint_resolver(param.annotation)))

            schema[key] = None
        elif param.kind == param.POSITIONAL_OR_KEYWORD:
            positional_args_names.add(key)
            if param.annotation == param.empty or key in ignore_args:
                positional_validators.append(None)
                schema[key] = None
            else:
                validator = typehint_resolver(param.annotation)
                positional_validators.append((key, validator))
                schema[key] = validator
        elif param.kind == param.VAR_POSITIONAL:
            if param.annotation != param.empty and key not in ignore_args:
                var_args_key_and_validator = key, typehint_resolver(param.annotation)
        elif param.kind == param.KEYWORD_ONLY:
            if param.annotation != param.empty and key not in ignore_args:
                schema[key] = typehint_resolver(param.annotation)
            else:
                schema[key] = None
        elif param.kind == param.VAR_KEYWORD:
            if param.annotation != param.empty and key not in ignore_args:
                kwargs_validator = typehint_resolver(param.annotation)

    if not ignore_return and sig.return_annotation != sig.empty:
        return_validator: Optional[Validator[Any]] = typehint_resolver(
            sig.return_annotation
        )
    else:
        return_validator = None

    # we can allow keys only sent in **kwargs to be ignored as well
    ignored_extra_kwargs = ignore_args.difference(schema)

    if inspect.iscoroutinefunction(func):

        async def inner_async(*args: Any, **kwargs: Any) -> Any:
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
                        if not (
                            result := await arg_validator.validate_async(arg)
                        ).is_valid:
                            errs[key] = result

                else:
                    if var_args_key_and_validator:
                        var_args_key, var_args_validator = var_args_key_and_validator
                        if not (
                            var_args_result := await var_args_validator.validate_async(
                                arg
                            )
                        ).is_valid:
                            var_args_errs.append((arg, var_args_result))

            if var_args_errs and var_args_key_and_validator:
                errs[var_args_key_and_validator[0]] = Invalid(
                    IndexErrs({i: err_ for i, (_, err_) in enumerate(var_args_errs)}),
                    tuple(a for a, _ in var_args_errs),
                    var_args_key_and_validator[1],
                )

            for kw_key, kw_val in kwargs.items():
                if kw_key in schema:
                    if schema_validator := schema[kw_key]:
                        if not (
                            kw_result := await schema_validator.validate_async(kw_val)
                        ).is_valid:
                            errs[kw_key] = kw_result
                elif (
                    kwargs_validator
                    and kw_key not in ignored_extra_kwargs
                    and not (
                        kwargs_result := await kwargs_validator.validate_async(kw_val)
                    ).is_valid
                ):
                    errs[kw_key] = kwargs_result

            if errs:
                raise InvalidArgsError(errs)
            elif return_validator:
                result = await func(*args, **kwargs)
                if (ret_result := await return_validator.validate_async(result)).is_valid:
                    return result
                else:
                    raise InvalidReturnError(ret_result)
            else:
                return await func(*args, **kwargs)

        return cast(_DecoratedFunc, inner_async)

    else:

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
                    if schema_validator := schema[kw_key]:
                        if not (kw_result := schema_validator(kw_val)).is_valid:
                            errs[kw_key] = kw_result
                elif (
                    kwargs_validator
                    and kw_key not in ignored_extra_kwargs
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

        return cast(_DecoratedFunc, inner)


@overload
def validate_signature(
    func: _DecoratedFunc,
    *,
    ignore_return: bool = False,
    ignore_args: Optional[Set[str]] = None,
    typehint_resolver: Callable[[Any], Validator[Any]] = get_typehint_validator,
) -> _DecoratedFunc:
    ...


@overload
def validate_signature(
    func: None = None,
    *,
    ignore_return: bool = False,
    ignore_args: Optional[Set[str]] = None,
    typehint_resolver: Callable[[Any], Validator[Any]] = get_typehint_validator,
) -> Callable[[_DecoratedFunc], _DecoratedFunc]:
    ...


def validate_signature(
    func: Optional[_DecoratedFunc] = None,
    *,
    ignore_return: bool = False,
    ignore_args: Optional[Set[str]] = None,
    typehint_resolver: Callable[[Any], Validator[Any]] = get_typehint_validator,
) -> Union[_DecoratedFunc, Callable[[_DecoratedFunc], _DecoratedFunc]]:
    if func is None:

        def inner(func_inner: _DecoratedFunc) -> _DecoratedFunc:
            return _wrap_fn(
                func_inner,
                ignore_return=ignore_return,
                ignore_args=ignore_args or set(),
                typehint_resolver=typehint_resolver,
            )

        return inner
    else:
        return _wrap_fn(
            func,
            ignore_return=ignore_return,
            ignore_args=ignore_args or set(),
            typehint_resolver=typehint_resolver,
        )


def _trunc_str(s: str, max_chars: int) -> str:
    ellip = "..."
    ellip_len = len(ellip)
    if max_chars < ellip_len:
        raise AssertionError(f"max_chars must be greater than or equal to {ellip_len}")

    return (s[: (max_chars - ellip_len)] + ellip) if len(s) > max_chars else s


def get_arg_fail_message(invalid: Invalid, indent: str = "", prefix: str = "") -> str:
    err_type = invalid.err_type
    next_indent = f"    {indent}"
    ret = indent + prefix
    if isinstance(err_type, TypeErr):
        ret += f"expected {err_type.expected_type}"
    elif isinstance(err_type, PredicateErrs):
        ret += f"{err_type.__class__.__name__}\n"
        ret += "\n".join([f"{next_indent}{repr(p)}" for p in err_type.predicates])
    elif isinstance(err_type, CoercionErr):
        ret += (
            f"expected any of "
            f"{sorted(err_type.compatible_types, key=lambda t: repr(t))} to coerce "
            f"to {repr(err_type.dest_type)}"
        )
    elif isinstance(err_type, ContainerErr):
        return get_arg_fail_message(err_type.child, prefix)
    elif isinstance(err_type, MissingKeyErr):
        ret += "key missing"
    elif isinstance(err_type, UnionErrs):
        variant_errors = [
            get_arg_fail_message(variant, next_indent, prefix=f"variant {i + 1}: ")
            for i, variant in enumerate(err_type.variants)
        ]
        ret += "\n".join([err_type.__class__.__name__] + variant_errors)
    elif isinstance(err_type, KeyErrs):
        ret += f"{err_type.__class__.__name__}\n"
        ret += "\n".join(
            [
                get_arg_fail_message(inv, next_indent, prefix=f"{repr(k)}: ")
                for k, inv in err_type.keys.items()
            ]
        )
    elif isinstance(err_type, ExtraKeysErr):
        ret += f"{err_type.__class__.__name__}\n"
        ret += (
            f"{next_indent}only expected keys {sorted(err_type.expected_keys, key=repr)}"
        )
    elif isinstance(err_type, IndexErrs):
        ret += f"{err_type.__class__.__name__}\n"
        ret += "\n".join(
            [
                get_arg_fail_message(inv, next_indent, prefix=f"{idx}: ")
                for idx, inv in err_type.indexes.items()
            ]
        )
    elif isinstance(err_type, MapErr):
        ret += "MapErr"
        for key, key_val_errs in err_type.keys.items():
            if key_val_errs.key:
                next_ = get_arg_fail_message(
                    key_val_errs.key, next_indent, prefix=f"{repr(key)} (key): "
                )
                ret += f"\n{next_}"
            if key_val_errs.val:
                next_ = get_arg_fail_message(
                    key_val_errs.val, next_indent, prefix=f"{repr(key)} (val): "
                )
                ret += f"\n{next_}"
    elif isinstance(err_type, SetErrs):
        ret += f"{err_type.__class__.__name__}\n"
        ret += "\n".join(
            [
                f"{get_arg_fail_message(e, next_indent)} :: {_trunc_str(repr(e.value), 30)}"  # noqa: E501
                for e in err_type.item_errs
            ]
        )

    return ret


def get_args_fail_msg(errs: Dict[str, Invalid]) -> str:
    messages = [
        f"{k}={_trunc_str(repr(v.value), 60)}\n{get_arg_fail_message(v, '    ')}"
        for k, v in errs.items()
    ]
    return "\n".join(messages)


INVALID_ARGS_MESSAGE_HEADER = "\nInvalid Argument Values\n-----------------------\n"
INVALID_RETURN_MESSAGE_HEADER = "\nInvalid Return Value\n--------------------\n"


class InvalidArgsError(Exception):
    def __init__(self, errs: Dict[str, Invalid]) -> None:
        super().__init__(INVALID_ARGS_MESSAGE_HEADER + get_args_fail_msg(errs))
        self.errs = errs


class InvalidReturnError(Exception):
    def __init__(self, err: Invalid):
        super().__init__(INVALID_RETURN_MESSAGE_HEADER + get_arg_fail_message(err))
        self.err = err
