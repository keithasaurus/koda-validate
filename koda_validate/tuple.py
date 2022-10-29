from typing import Any, Callable, Generic, List, Optional, Tuple, TypeVar, Union, overload

from koda import Err, Ok, Result

from koda_validate._generics import A
from koda_validate.typedefs import Serializable, Validator


class _NotSet:
    pass


_not_set = _NotSet()

_Settable = Union[A, _NotSet]
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")
T7 = TypeVar("T7")
T8 = TypeVar("T8")
T9 = TypeVar("T9")
T10 = TypeVar("T10")
T11 = TypeVar("T11")
T12 = TypeVar("T12")
Ret = TypeVar("Ret")
FailT = TypeVar("FailT")


@overload
def typed_tuple(t1: T1) -> Tuple[T1]:
    ...


@overload
def typed_tuple(t1: T1, t2: T2) -> Tuple[T1, T2]:
    ...


@overload
def typed_tuple(t1: T1, t2: T2, t3: T3) -> Tuple[T1, T2, T3]:
    ...


@overload
def typed_tuple(t1: T1, t2: T2, t3: T3, t4: T4) -> Tuple[T1, T2, T3, T4]:
    ...


@overload
def typed_tuple(t1: T1, t2: T2, t3: T3, t4: T4, t5: T5) -> Tuple[T1, T2, T3, T4, T5]:
    ...


@overload
def typed_tuple(
    t1: T1, t2: T2, t3: T3, t4: T4, t5: T5, t6: T6
) -> Tuple[T1, T2, T3, T4, T5, T6]:
    ...


@overload
def typed_tuple(
    t1: T1, t2: T2, t3: T3, t4: T4, t5: T5, t6: T6, t7: T7
) -> Tuple[T1, T2, T3, T4, T5, T6, T7]:
    ...


@overload
def typed_tuple(
    t1: T1, t2: T2, t3: T3, t4: T4, t5: T5, t6: T6, t7: T7, t8: T8
) -> Tuple[T1, T2, T3, T4, T5, T6, T7, T8]:
    ...


@overload
def typed_tuple(
    t1: T1, t2: T2, t3: T3, t4: T4, t5: T5, t6: T6, t7: T7, t8: T8, t9: T9
) -> Tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9]:
    ...


@overload
def typed_tuple(
    t1: T1, t2: T2, t3: T3, t4: T4, t5: T5, t6: T6, t7: T7, t8: T8, t9: T9, t10: T10
) -> Tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]:
    ...


@overload
def typed_tuple(
    t1: T1,
    t2: T2,
    t3: T3,
    t4: T4,
    t5: T5,
    t6: T6,
    t7: T7,
    t8: T8,
    t9: T9,
    t10: T10,
    t11: T11,
) -> Tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11]:
    ...


@overload
def typed_tuple(
    t1: T1,
    t2: T2,
    t3: T3,
    t4: T4,
    t5: T5,
    t6: T6,
    t7: T7,
    t8: T8,
    t9: T9,
    t10: T10,
    t11: T11,
    t12: T12,
) -> Tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12]:
    ...


def typed_tuple(
    t1: T1,
    t2: Union[T2, _NotSet] = _not_set,
    t3: Union[T3, _NotSet] = _not_set,
    t4: Union[T4, _NotSet] = _not_set,
    t5: Union[T5, _NotSet] = _not_set,
    t6: Union[T6, _NotSet] = _not_set,
    t7: Union[T7, _NotSet] = _not_set,
    t8: Union[T8, _NotSet] = _not_set,
    t9: Union[T9, _NotSet] = _not_set,
    t10: Union[T10, _NotSet] = _not_set,
    t11: Union[T11, _NotSet] = _not_set,
    t12: Union[T12, _NotSet] = _not_set,
) -> Union[
    Tuple[T1],
    Tuple[T1, T2],
    Tuple[T1, T2, T3],
    Tuple[T1, T2, T3, T4],
    Tuple[T1, T2, T3, T4, T5],
    Tuple[T1, T2, T3, T4, T5, T6],
    Tuple[T1, T2, T3, T4, T5, T6, T7],
    Tuple[T1, T2, T3, T4, T5, T6, T7, T8],
    Tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9],
    Tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10],
    Tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11],
    Tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12],
]:
    if isinstance(t2, _NotSet):
        return (t1,)

    elif isinstance(t3, _NotSet):
        return (
            t1,
            t2,
        )

    elif isinstance(t4, _NotSet):
        return (
            t1,
            t2,
            t3,
        )

    elif isinstance(t5, _NotSet):
        return (
            t1,
            t2,
            t3,
            t4,
        )

    elif isinstance(t6, _NotSet):
        return (
            t1,
            t2,
            t3,
            t4,
            t5,
        )

    elif isinstance(t7, _NotSet):
        return (
            t1,
            t2,
            t3,
            t4,
            t5,
            t6,
        )

    elif isinstance(t8, _NotSet):
        return (
            t1,
            t2,
            t3,
            t4,
            t5,
            t6,
            t7,
        )

    elif isinstance(t9, _NotSet):
        return (
            t1,
            t2,
            t3,
            t4,
            t5,
            t6,
            t7,
            t8,
        )

    elif isinstance(t10, _NotSet):
        return (
            t1,
            t2,
            t3,
            t4,
            t5,
            t6,
            t7,
            t8,
            t9,
        )

    elif isinstance(t11, _NotSet):
        return (
            t1,
            t2,
            t3,
            t4,
            t5,
            t6,
            t7,
            t8,
            t9,
            t10,
        )

    elif isinstance(t12, _NotSet):
        return (
            t1,
            t2,
            t3,
            t4,
            t5,
            t6,
            t7,
            t8,
            t9,
            t10,
            t11,
        )

    else:
        return (
            t1,
            t2,
            t3,
            t4,
            t5,
            t6,
            t7,
            t8,
            t9,
            t10,
            t11,
            t12,
        )


class TupleValidator(Generic[Ret], Validator[Any, Ret, Serializable]):
    __slots__ = ("into", "fields", "validate_object")
    __match_args__ = ("into", "fields", "validate_object")

    @overload
    def __init__(
        self,
        into: Callable[[T1], Ret],
        field1: Validator[Any, T1, Serializable],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2], Ret],
        field1: Validator[Any, T1, Serializable],
        field2: Optional[Validator[Any, T2, Serializable]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3], Ret],
        field1: Validator[Any, T1, Serializable],
        field2: Optional[Validator[Any, T2, Serializable]] = None,
        field3: Optional[Validator[Any, T3, Serializable]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4], Ret],
        field1: Validator[Any, T1, Serializable],
        field2: Optional[Validator[Any, T2, Serializable]] = None,
        field3: Optional[Validator[Any, T3, Serializable]] = None,
        field4: Optional[Validator[Any, T4, Serializable]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5], Ret],
        field1: Validator[Any, T1, Serializable],
        field2: Optional[Validator[Any, T2, Serializable]] = None,
        field3: Optional[Validator[Any, T3, Serializable]] = None,
        field4: Optional[Validator[Any, T4, Serializable]] = None,
        field5: Optional[Validator[Any, T5, Serializable]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6], Ret],
        field1: Validator[Any, T1, Serializable],
        field2: Optional[Validator[Any, T2, Serializable]] = None,
        field3: Optional[Validator[Any, T3, Serializable]] = None,
        field4: Optional[Validator[Any, T4, Serializable]] = None,
        field5: Optional[Validator[Any, T5, Serializable]] = None,
        field6: Optional[Validator[Any, T6, Serializable]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7], Ret],
        field1: Validator[Any, T1, Serializable],
        field2: Optional[Validator[Any, T2, Serializable]] = None,
        field3: Optional[Validator[Any, T3, Serializable]] = None,
        field4: Optional[Validator[Any, T4, Serializable]] = None,
        field5: Optional[Validator[Any, T5, Serializable]] = None,
        field6: Optional[Validator[Any, T6, Serializable]] = None,
        field7: Optional[Validator[Any, T7, Serializable]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8], Ret],
        field1: Validator[Any, T1, Serializable],
        field2: Optional[Validator[Any, T2, Serializable]] = None,
        field3: Optional[Validator[Any, T3, Serializable]] = None,
        field4: Optional[Validator[Any, T4, Serializable]] = None,
        field5: Optional[Validator[Any, T5, Serializable]] = None,
        field6: Optional[Validator[Any, T6, Serializable]] = None,
        field7: Optional[Validator[Any, T7, Serializable]] = None,
        field8: Optional[Validator[Any, T8, Serializable]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], Ret],
        field1: Validator[Any, T1, Serializable],
        field2: Optional[Validator[Any, T2, Serializable]] = None,
        field3: Optional[Validator[Any, T3, Serializable]] = None,
        field4: Optional[Validator[Any, T4, Serializable]] = None,
        field5: Optional[Validator[Any, T5, Serializable]] = None,
        field6: Optional[Validator[Any, T6, Serializable]] = None,
        field7: Optional[Validator[Any, T7, Serializable]] = None,
        field8: Optional[Validator[Any, T8, Serializable]] = None,
        field9: Optional[Validator[Any, T9, Serializable]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret],
        field1: Validator[Any, T1, Serializable],
        field2: Optional[Validator[Any, T2, Serializable]] = None,
        field3: Optional[Validator[Any, T3, Serializable]] = None,
        field4: Optional[Validator[Any, T4, Serializable]] = None,
        field5: Optional[Validator[Any, T5, Serializable]] = None,
        field6: Optional[Validator[Any, T6, Serializable]] = None,
        field7: Optional[Validator[Any, T7, Serializable]] = None,
        field8: Optional[Validator[Any, T8, Serializable]] = None,
        field9: Optional[Validator[Any, T9, Serializable]] = None,
        field10: Optional[Validator[Any, T10, Serializable]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret],
        field1: Validator[Any, T1, Serializable],
        field2: Optional[Validator[Any, T2, Serializable]] = None,
        field3: Optional[Validator[Any, T3, Serializable]] = None,
        field4: Optional[Validator[Any, T4, Serializable]] = None,
        field5: Optional[Validator[Any, T5, Serializable]] = None,
        field6: Optional[Validator[Any, T6, Serializable]] = None,
        field7: Optional[Validator[Any, T7, Serializable]] = None,
        field8: Optional[Validator[Any, T8, Serializable]] = None,
        field9: Optional[Validator[Any, T9, Serializable]] = None,
        field10: Optional[Validator[Any, T10, Serializable]] = None,
        field11: Optional[Validator[Any, T11, Serializable]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret],
        field1: Validator[Any, T1, Serializable],
        field2: Optional[Validator[Any, T2, Serializable]] = None,
        field3: Optional[Validator[Any, T3, Serializable]] = None,
        field4: Optional[Validator[Any, T4, Serializable]] = None,
        field5: Optional[Validator[Any, T5, Serializable]] = None,
        field6: Optional[Validator[Any, T6, Serializable]] = None,
        field7: Optional[Validator[Any, T7, Serializable]] = None,
        field8: Optional[Validator[Any, T8, Serializable]] = None,
        field9: Optional[Validator[Any, T9, Serializable]] = None,
        field10: Optional[Validator[Any, T10, Serializable]] = None,
        field11: Optional[Validator[Any, T11, Serializable]] = None,
        field12: Optional[Validator[Any, T12, Serializable]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        ...  # pragma: no cover

    def __init__(
        self,
        into: Union[
            Callable[[T1], Ret],
            Callable[[T1, T2], Ret],
            Callable[[T1, T2, T3], Ret],
            Callable[[T1, T2, T3, T4], Ret],
            Callable[[T1, T2, T3, T4, T5], Ret],
            Callable[[T1, T2, T3, T4, T5, T6], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret],
            Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret],
        ],
        field1: Validator[Any, T1, Serializable],
        field2: Optional[Validator[Any, T2, Serializable]] = None,
        field3: Optional[Validator[Any, T3, Serializable]] = None,
        field4: Optional[Validator[Any, T4, Serializable]] = None,
        field5: Optional[Validator[Any, T5, Serializable]] = None,
        field6: Optional[Validator[Any, T6, Serializable]] = None,
        field7: Optional[Validator[Any, T7, Serializable]] = None,
        field8: Optional[Validator[Any, T8, Serializable]] = None,
        field9: Optional[Validator[Any, T9, Serializable]] = None,
        field10: Optional[Validator[Any, T10, Serializable]] = None,
        field11: Optional[Validator[Any, T11, Serializable]] = None,
        field12: Optional[Validator[Any, T12, Serializable]] = None,
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.fields: Tuple[Validator[Any, Any, Serializable], ...] = tuple(
            f
            for f in (
                field1,
                field2,
                field3,
                field4,
                field5,
                field6,
                field7,
                field8,
                field9,
                field10,
                field11,
                field12,
            )
            if f is not None
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        if not isinstance(data, (tuple, list)) or len(data) != len(self.fields):
            return Err([f"expected a tuple or list of length {len(self.fields)}"])

        args = []
        errs: List[Serializable] = []
        # we know that self.fields and data are tuples / lists of the same length
        for value, validator in zip(data, self.fields):
            result = validator(value)
            if isinstance(result, Err):
                errs.append(result.val)
            else:
                args.append(result.val)

        if len(errs) > 0:
            return Err(errs)
        else:
            obj = self.into(*args)
            if self.validate_object is None:
                return Ok(obj)
            else:
                return self.validate_object(obj)
