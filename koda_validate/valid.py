from dataclasses import dataclass
from pprint import pformat
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Generic, Literal, Union

from koda_validate._generics import A, B

if TYPE_CHECKING:
    from koda_validate.base import Validator


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


def _make_invalid_repr(indent: str, inv: Invalid) -> str:
    next_indent = indent + " " * 4
    return f"\n{next_indent}".join([
        "Invalid(",
        f"err_type={_render_err_type(next_indent, inv.err_type)},",
        f"value={repr(inv.value)},",
        f"validator={repr(inv.validator)}",
    ]) + f"\n{indent})"


def _render_err_type(indent: str, err: "ErrType") -> str:
    from koda_validate.errors import ErrType, IndexErrs, TypeErr, CoercionErr, KeyErrs
    # CoercionErr,
    # ContainerErr,
    # ExtraKeysErr,
    # IndexErrs,
    # KeyErrs,
    # MapErr,
    # MissingKeyErr,
    # # This seems like a type exception worth making..., but that might change in the
    # # future. This is backwards compatible with existing code
    # PredicateErrs[Any],
    # SetErrs,
    # TypeErr,
    # ValidationErrBase,
    # UnionErrs,

    next_indent_str = indent + (" " * 4)
    match err:
        case CoercionErr(compatible_types, dest_type):
            return f"\n{next_indent_str}".join(
                ["CoercionErr(",
                f"compatible_types={{{", ".join([repr(ct) for ct in compatible_types])}}},",
                f"dest_type={repr(dest_type)}",
                ]
            ) + f"\n{indent})"
        case KeyErrs(keys):
            return f"\n{next_indent_str}".join(
                ["KeyErrs(keys={", ] + [
                    f"{key}: {_make_invalid_repr(next_indent_str, k_err)},"
                    for key, k_err in keys.items()
                ]
            ) + f"\n{indent}}})"
        case IndexErrs(i_errs):
            return f"\n{next_indent_str}".join(
                ["IndexErrs(index_errs={",] + [
                    f"{key}: {_make_invalid_repr(next_indent_str, i_err)},"
                    for key, i_err in i_errs.items()
                ]
            ) + f"\n{indent}}})"
        case TypeErr(err):
            return repr(err)
        case _:
            return repr(err)


ValidationResult = Union[Valid[A], Invalid]
