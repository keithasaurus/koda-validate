from typing import Any, Callable, Generic, List, Optional, Tuple, TypeVar, Union, overload

from koda import Err, Ok, Result

from koda_validate.typedefs import Serializable, Validator

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
            elif errs is None:
                args.append(result.val)

        if len(errs) > 0:
            return Err(errs)
        else:
            obj = self.into(*args)
            if self.validate_object is None:
                return Ok(obj)
            else:
                return self.validate_object(obj)
