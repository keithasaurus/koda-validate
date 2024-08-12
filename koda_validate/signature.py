import functools
import inspect
from dataclasses import is_dataclass
from datetime import date, datetime
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    overload,
)
from uuid import UUID

from _decimal import Decimal

from koda_validate import DataclassValidator, NamedTupleValidator
from koda_validate._internal import _is_typed_dict_cls
from koda_validate.base import Validator
from koda_validate.dataclasses import dataclass_no_coerce
from koda_validate.errors import (
    CoercionErr,
    ContainerErr,
    ExtraKeysErr,
    IndexErrs,
    KeyErrs,
    MapErr,
    MissingKeyErr,
    PredicateErrs,
    SetErrs,
    TypeErr,
    UnionErrs,
)
from koda_validate.generic import always_valid
from koda_validate.namedtuple import namedtuple_no_coerce
from koda_validate.time import DatetimeValidator, DateValidator
from koda_validate.tuple import NTupleValidator, UniformTupleValidator
from koda_validate.typeddict import TypedDictValidator
from koda_validate.typehints import (
    annotation_is_naked_tuple,
    annotation_is_namedtuple,
    get_typehint_validator_base,
)
from koda_validate.uuid import UUIDValidator
from koda_validate.valid import Invalid

_BaseDecoratedFunc = Callable[..., Any]
_DecoratedFunc = TypeVar("_DecoratedFunc", bound=_BaseDecoratedFunc)

# for overrides - just to avoid parameter name conflicts
ReturnOverrideKey = Tuple[Literal["return_key"]]
RETURN_OVERRIDE_KEY: ReturnOverrideKey = ("return_key",)

OverridesDictKey = Union[str, ReturnOverrideKey]
OverridesDict = Dict[OverridesDictKey, Validator[Any]]


def resolve_signature_typehint_default(annotation: Any) -> Validator[Any]:
    if annotation is Decimal:
        from koda_validate.decimal import DecimalValidator

        return DecimalValidator(coerce=None)
    elif _is_typed_dict_cls(annotation):
        return TypedDictValidator(annotation)
    elif annotation is UUID:
        return UUIDValidator(coerce=None)
    elif annotation is date:
        return DateValidator(coerce=None)
    elif annotation is datetime:
        return DatetimeValidator(coerce=None)
    elif annotation_is_naked_tuple(annotation):
        return UniformTupleValidator(always_valid, coerce=None)
    elif is_dataclass(annotation):
        return DataclassValidator(annotation, coerce=dataclass_no_coerce(annotation))
    elif annotation_is_namedtuple(annotation):
        return NamedTupleValidator(annotation, coerce=namedtuple_no_coerce(annotation))
    else:
        origin, args = get_origin(annotation), get_args(annotation)
        if annotation_is_naked_tuple(origin):
            if len(args) == 2 and args[1] is Ellipsis:
                return UniformTupleValidator(
                    resolve_signature_typehint_default(args[0]), coerce=None
                )
            else:
                return NTupleValidator.untyped(
                    fields=tuple(resolve_signature_typehint_default(a) for a in args),
                    coerce=None,
                )

    return get_typehint_validator_base(resolve_signature_typehint_default, annotation)


def _get_validator(
    overrides: OverridesDict,
    typehint_resolver: Callable[[Any], Validator[Any]],
    param_name: OverridesDictKey,
    annotation: Any,
) -> Validator[Any]:
    return (
        overrides[param_name]
        if param_name in overrides
        else typehint_resolver(annotation)
    )


def _wrap_fn(
    func: _DecoratedFunc,
    ignore_args: Set[str],
    ignore_return: bool,
    typehint_resolver: Callable[[Any], Validator[Any]],
    overrides: OverridesDict,
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
    _get_validator_partial = functools.partial(
        _get_validator, overrides, typehint_resolver
    )

    # create arg schema
    for key, param in sig.parameters.items():
        annotation = param.annotation
        if param.kind == param.POSITIONAL_ONLY:
            positional_args_names.add(key)
            if annotation == param.empty or key in ignore_args:
                positional_validators.append(None)
            else:
                positional_validators.append(
                    (key, _get_validator_partial(key, annotation))
                )

            schema[key] = None
        elif param.kind == param.POSITIONAL_OR_KEYWORD:
            positional_args_names.add(key)
            if annotation == param.empty or key in ignore_args:
                positional_validators.append(None)
                schema[key] = None
            else:
                validator = _get_validator_partial(key, annotation)
                positional_validators.append((key, validator))
                schema[key] = validator
        elif param.kind == param.VAR_POSITIONAL:
            if annotation != param.empty and key not in ignore_args:
                var_args_key_and_validator = key, _get_validator_partial(key, annotation)
        elif param.kind == param.KEYWORD_ONLY:
            if annotation != param.empty and key not in ignore_args:
                schema[key] = _get_validator_partial(key, annotation)
            else:
                schema[key] = None
        elif param.kind == param.VAR_KEYWORD:
            if annotation != param.empty and key not in ignore_args:
                kwargs_validator = _get_validator_partial(key, annotation)

    if not ignore_return and sig.return_annotation != sig.empty:
        return_validator: Optional[Validator[Any]] = _get_validator_partial(
            RETURN_OVERRIDE_KEY, sig.return_annotation
        )
    else:
        return_validator = None

    # we can allow keys only sent in **kwargs to be ignored as well
    ignored_extra_kwargs = ignore_args.difference(schema)

    if inspect.iscoroutinefunction(func) or inspect.iscoroutinefunction(
        getattr(func, "__call__", None)
    ):

        async def inner_async(*args: Any, **kwargs: Any) -> Any:
            errs: Dict[str, Invalid] = {}
            var_args_errs: List[Tuple[Any, Invalid]] = []
            # in case the values get mutated during validation
            ok_args: List[Any] = list(args)
            ok_kw_args: Dict[str, Any] = kwargs.copy()
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
                            ok_args[i] = result.val

                else:
                    if var_args_key_and_validator:
                        var_args_key, var_args_validator = var_args_key_and_validator
                        if not (
                            var_args_result := await var_args_validator.validate_async(
                                arg
                            )
                        ).is_valid:
                            var_args_errs.append((arg, var_args_result))
                        else:
                            ok_args[i] = var_args_result.val

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
                        else:
                            ok_kw_args[kw_key] = kw_result.val
                elif kwargs_validator and kw_key not in ignored_extra_kwargs:
                    if not (
                        kwargs_result := await kwargs_validator.validate_async(kw_val)
                    ).is_valid:
                        errs[kw_key] = kwargs_result
                    else:
                        ok_kw_args[kw_key] = kwargs_result.val

            if errs:
                raise InvalidArgsError(errs)
            elif return_validator:
                result = await func(*ok_args, **ok_kw_args)
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
            # in case the values get mutated during validation
            ok_args: List[Any] = list(args)
            ok_kw_args: Dict[str, Any] = kwargs.copy()
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
                            ok_args[i] = result.val

                else:
                    if var_args_key_and_validator:
                        var_args_key, var_args_validator = var_args_key_and_validator
                        if not (var_args_result := var_args_validator(arg)).is_valid:
                            var_args_errs.append((arg, var_args_result))
                        else:
                            ok_args[i] = var_args_result.val

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
                        else:
                            ok_kw_args[kw_key] = kw_result.val
                elif kwargs_validator and kw_key not in ignored_extra_kwargs:
                    if (kwargs_result := kwargs_validator(kw_val)).is_valid:
                        ok_kw_args[kw_key] = kwargs_result.val
                    else:
                        errs[kw_key] = kwargs_result

            if errs:
                raise InvalidArgsError(errs)
            elif return_validator:
                result = func(*ok_args, **ok_kw_args)
                if (ret_result := return_validator(result)).is_valid:
                    return result
                else:
                    raise InvalidReturnError(ret_result)
            else:
                return func(*ok_args, **kwargs)

        return cast(_DecoratedFunc, inner)


@overload
def validate_signature(
    func: _DecoratedFunc,
    *,
    ignore_args: Optional[Set[str]] = None,
    ignore_return: bool = False,
    typehint_resolver: Callable[
        [Any], Validator[Any]
    ] = resolve_signature_typehint_default,  # noqa: E501
    overrides: Optional[OverridesDict] = None,
) -> _DecoratedFunc:
    ...


@overload
def validate_signature(
    func: None = None,
    *,
    ignore_args: Optional[Set[str]] = None,
    ignore_return: bool = False,
    typehint_resolver: Callable[
        [Any], Validator[Any]
    ] = resolve_signature_typehint_default,  # noqa: E501
    overrides: Optional[OverridesDict] = None,
) -> Callable[[_DecoratedFunc], _DecoratedFunc]:
    ...


def validate_signature(
    func: Optional[_DecoratedFunc] = None,
    *,
    ignore_return: bool = False,
    ignore_args: Optional[Set[str]] = None,
    typehint_resolver: Callable[
        [Any], Validator[Any]
    ] = resolve_signature_typehint_default,  # noqa: E501
    overrides: Optional[OverridesDict] = None,
) -> Union[_DecoratedFunc, Callable[[_DecoratedFunc], _DecoratedFunc]]:
    r"""
    Validates a function's arguments and / or return value adhere to the respective
    typehints and / or any custom-specified Validation.Because we want to preserve the
    type signature of the function when it's wrapped, we raise exceptions to represent
    failure (as opposed to returning ``ValidationResult[ReturnType]``, which would change
    the function's type signature).

    :param func: the function being validated
    :param ignore_return: whether or not to ignore the return annotation
    :param ignore_args: any arguments that should be ignored
    :param typehint_resolver: the function responsible for resolving type annotations
        to :class:`koda_validate.Validator`\s
    :param overrides: explicit `Validator`s for arguments that takes priority over
        `typehint_resolver` and `Annotated` types
    :return: the decorated function
    """
    _wrap_fn_partial = functools.partial(
        _wrap_fn,
        ignore_return=ignore_return,
        ignore_args=ignore_args or set(),
        typehint_resolver=typehint_resolver,
        overrides=overrides or {},
    )

    if func is None:

        def inner(func_inner: _DecoratedFunc) -> _DecoratedFunc:
            # there may be a good way to replace this cast with ParamSpec in the future
            return _wrap_fn_partial(func_inner)

        return inner
    else:
        # there may be a good way to replace this cast with ParamSpec in the future
        return _wrap_fn_partial(func)


def _trunc_str(s: str, max_chars: int) -> str:
    ellip = "..."
    ellip_len = len(ellip)
    if max_chars < ellip_len:
        raise AssertionError(f"max_chars must be greater than or equal to {ellip_len}")

    return (s[: (max_chars - ellip_len)] + ellip) if len(s) > max_chars else s


def _get_arg_fail_message(invalid: Invalid, indent: str = "", prefix: str = "") -> str:
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
        return _get_arg_fail_message(err_type.child, prefix)
    elif isinstance(err_type, MissingKeyErr):
        ret += "key missing"
    elif isinstance(err_type, UnionErrs):
        variant_errors = [
            _get_arg_fail_message(variant, next_indent, prefix=f"variant {i + 1}: ")
            for i, variant in enumerate(err_type.variants)
        ]
        ret += "\n".join([err_type.__class__.__name__] + variant_errors)
    elif isinstance(err_type, KeyErrs):
        ret += f"{err_type.__class__.__name__}\n"
        ret += "\n".join(
            [
                _get_arg_fail_message(inv, next_indent, prefix=f"{repr(k)}: ")
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
                _get_arg_fail_message(inv, next_indent, prefix=f"{idx}: ")
                for idx, inv in err_type.indexes.items()
            ]
        )
    elif isinstance(err_type, MapErr):
        ret += "MapErr"
        for key, key_val_errs in err_type.keys.items():
            if key_val_errs.key:
                next_ = _get_arg_fail_message(
                    key_val_errs.key, next_indent, prefix=f"{repr(key)} (key): "
                )
                ret += f"\n{next_}"
            if key_val_errs.val:
                next_ = _get_arg_fail_message(
                    key_val_errs.val, next_indent, prefix=f"{repr(key)} (val): "
                )
                ret += f"\n{next_}"
    elif isinstance(err_type, SetErrs):
        ret += f"{err_type.__class__.__name__}\n"
        ret += "\n".join(
            [
                f"{_get_arg_fail_message(e, next_indent)} :: {_trunc_str(repr(e.value), 30)}"  # noqa: E501
                # noqa: E501
                for e in err_type.item_errs
            ]
        )

    return ret


def _get_args_fail_msg(errs: Dict[str, Invalid]) -> str:
    messages = [
        f"{k}={_trunc_str(repr(v.value), 60)}\n{_get_arg_fail_message(v, '    ')}"
        for k, v in errs.items()
    ]
    return "\n".join(messages)


_INVALID_ARGS_MESSAGE_HEADER = "\nInvalid Argument Values\n-----------------------\n"
_INVALID_RETURN_MESSAGE_HEADER = "\nInvalid Return Value\n--------------------\n"


class InvalidArgsError(Exception):
    """
    Represents the validation failure of one or more arguments.
    """

    def __init__(self, errs: Dict[str, Invalid]) -> None:
        super().__init__(_INVALID_ARGS_MESSAGE_HEADER + _get_args_fail_msg(errs))
        self.errs = errs


class InvalidReturnError(Exception):
    """
    Represents a return value that has failed validation.
    """

    def __init__(self, err: Invalid):
        super().__init__(_INVALID_RETURN_MESSAGE_HEADER + _get_arg_fail_message(err))
        self.err = err
