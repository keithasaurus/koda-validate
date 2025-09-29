from dataclasses import dataclass
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
    from koda_validate.errors import IndexErrs, CoercionErr, KeyErrs, ContainerErr, ExtraKeysErr, MapErr, KeyValErrs, SetErrs, PredicateErrs, UnionErrs

    next_indent_str = indent + (" " * 4)
    match err:
        case PredicateErrs(predicates):
            return f"\n{next_indent_str}".join(
                ["PredicateErrs(predicates=[", ] + [
                    f"{repr(pred)}"","
                    for pred in predicates
                ]
            ) + f"\n{indent}])"
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
                    f"{repr(key)}: {_make_invalid_repr(next_indent_str, k_err)},"
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
        case ContainerErr(child):
            return f"\n{next_indent_str}".join(
                [f"ContainerErr(",
                 f"child={_make_invalid_repr(next_indent_str, child)}",]
            ) + f"\n{indent})"
        case ExtraKeysErr(expected_keys):
            return f"\n{next_indent_str}".join(
                [f"ExtraKeysErr(",
                 f"expected_keys={{{", ".join(sorted([repr(k) for k in expected_keys]))}}},""}",]
            ) + f"\n{indent})"
        case MapErr(keys):
            return f"\n{next_indent_str}".join(
                ["MapErr(keys={", ] + [
                    f"{repr(key)}: {_render_err_type(next_indent_str, k_err)},"
                    for key, k_err in keys.items()
                ]
            ) + f"\n{indent}}})"
        case KeyValErrs(key, val):
            to_join = [
                "KeyValErrs(",
                f"key={'None' if key is None else _make_invalid_repr(next_indent_str, key)},",
                f"val={'None' if val is None else _make_invalid_repr(next_indent_str, val)}",
            ]
            return f"\n{next_indent_str}".join(to_join) + f"\n{indent})"
        case SetErrs(item_errs):
            return f"\n{next_indent_str}".join(
                ["SetErrs(item_errs=[",] + [
                    f"{_make_invalid_repr(next_indent_str, item)},"
                    for item in item_errs
                ]
            ) + f"\n{indent}])"
        case UnionErrs(variants):
            return f"\n{next_indent_str}".join(
                ["UnionErrs(variants=[",] + [
                    f"{_make_invalid_repr(next_indent_str, variant)},"
                    for variant in variants
                ]
            ) + f"\n{indent}])"
        case _:
            return repr(err)


ValidationResult = Union[Valid[A], Invalid]
