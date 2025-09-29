from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Generic, Literal, Union

from koda_validate._generics import A, B

if TYPE_CHECKING:
    from koda_validate.base import Validator
    from koda_validate.errors import ErrType, KeyValErrs


@dataclass
class Valid(Generic[A]):
    """
    A wrapper for valid data, e.g. ``Valid("abc")``
    """

    val: A
    """
    The value that has succeeded validation
    """

    is_valid: ClassVar[Literal[True]] = True
    """
    This is always ``True`` on :class:`Valid` instances. It's useful for ``if``
    statements. Mypy understands it as a tag for a tagged union.
    """

    def map(self, func: Callable[[A], B]) -> "ValidationResult[B]":
        return Valid(func(self.val))


@dataclass
class Invalid:
    """
    Represents validation failure. Contains relevant failure data so use case-specific
    error objects (or other data) can be produced.
    """

    err_type: "ErrType"
    """
    Any of a number of classes that contain data about the type of error, e.g.
    :class:`TypeErr`, :class:`CoercionErr`, :class:`KeyMissingErr`, etc.
    """

    value: Any
    """
    The invalid value that was being validated
    """

    validator: "Validator[Any]"
    """
    The validator that determined ``value`` to be invalid
    """

    is_valid: ClassVar[Literal[False]] = False
    """
    This is always ``False`` on :class:`Invalid` instances. It’s useful for ``if``
    statements. Mypy understands it as a tag for a tagged union.
    """

    def map(self, func: Callable[[Any], B]) -> "ValidationResult[B]":
        return self

    def __repr__(self) -> str:
        return _make_invalid_repr("", self)


def _render_key_val_err(indent: str, err: "KeyValErrs") -> str:
    next_indent_str = indent + (" " * 4)
    k = err.key
    v = err.val
    to_join = [
        "KeyValErrs(",
        f"key={'None' if k is None else _make_invalid_repr(next_indent_str, k)},",
        f"val={'None' if v is None else _make_invalid_repr(next_indent_str, v)}",
    ]
    return f"\n{next_indent_str}".join(to_join) + f"\n{indent})"


def _make_invalid_repr(indent: str, inv: Invalid) -> str:
    next_indent = indent + " " * 4
    return f"\n{next_indent}".join([
        "Invalid(",
        f"err_type={_render_err_type(next_indent, inv.err_type)},",
        f"value={repr(inv.value)},",
        f"validator={repr(inv.validator)}",
    ]) + f"\n{indent})"


def _render_err_type(indent: str, err: "ErrType") -> str:
    from koda_validate.errors import (IndexErrs, CoercionErr, KeyErrs, ContainerErr,
                                      ExtraKeysErr, MapErr, SetErrs, PredicateErrs,
                                      UnionErrs)

    next_indent_str = indent + (" " * 4)
    if isinstance(err, PredicateErrs):
        return f"\n{next_indent_str}".join(
            ["PredicateErrs(predicates=[", ] + [
                f"{repr(pred)}"","
                for pred in err.predicates
            ]
        ) + f"\n{indent}])"
    elif isinstance(err, CoercionErr):
        return f"\n{next_indent_str}".join([
            "CoercionErr(",
            f"compatible_types={{{', '.join([repr(ct) for ct in err.compatible_types])}}},",  # noqa: E501
            f"dest_type={repr(err.dest_type)}",
        ]) + f"\n{indent})"
    elif isinstance(err, KeyErrs):
        return f"\n{next_indent_str}".join(
            ["KeyErrs(keys={", ] + [
                f"{repr(key)}: {_make_invalid_repr(next_indent_str, k_err)},"
                for key, k_err in err.keys.items()
            ]
        ) + f"\n{indent}}})"
    elif isinstance(err, IndexErrs):
        return f"\n{next_indent_str}".join(
            ["IndexErrs(index_errs={",] + [
                f"{key}: {_make_invalid_repr(next_indent_str, i_err)},"
                for key, i_err in err.indexes.items()
            ]
        ) + f"\n{indent}}})"
    elif isinstance(err, ContainerErr):
        return f"\n{next_indent_str}".join(
            ["ContainerErr(",
             f"child={_make_invalid_repr(next_indent_str, err.child)}",]
        ) + f"\n{indent})"
    elif isinstance(err, ExtraKeysErr):
        return f"\n{next_indent_str}".join(
            ["ExtraKeysErr(",
             f"expected_keys={{{', '.join(sorted([repr(k) for k in err.expected_keys]))}}},""}",]  # noqa: E501
        ) + f"\n{indent})"
    elif isinstance(err, MapErr):
        return f"\n{next_indent_str}".join(
            ["MapErr(keys={", ] + [
                f"{repr(key)}: {_render_key_val_err(next_indent_str, k_err)},"
                for key, k_err in err.keys.items()
            ]
        ) + f"\n{indent}}})"
    elif isinstance(err, SetErrs):
        return f"\n{next_indent_str}".join(
            ["SetErrs(item_errs=[",] + [
                f"{_make_invalid_repr(next_indent_str, item)},"
                for item in err.item_errs
            ]
        ) + f"\n{indent}])"
    elif isinstance(err, UnionErrs):
        return f"\n{next_indent_str}".join(
            ["UnionErrs(variants=[",] + [
                f"{_make_invalid_repr(next_indent_str, variant)},"
                for variant in err.variants
            ]
        ) + f"\n{indent}])"
    else:
        return repr(err)


ValidationResult = Union[Valid[A], Invalid]
