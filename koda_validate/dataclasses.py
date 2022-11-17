from dataclasses import is_dataclass
from typing import Any, ClassVar, Dict, Protocol, Type, TypeVar, get_type_hints

from koda_validate import (
    DictValidatorAny,
    IntValidator,
    Invalid,
    Serializable,
    StringValidator,
    Valid,
    Validated,
    Validator,
)


class DataclassLike(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Any]]


_DCT = TypeVar("_DCT", bound=DataclassLike)


class DataclassValidator(Validator[Any, _DCT, Serializable]):
    def __init__(self, data_cls: Type[_DCT]) -> None:
        self.data_cls = data_cls
        fields = {}
        for field, annotations in get_type_hints(self.data_cls).items():
            if annotations is str:
                fields[field] = StringValidator()
            elif annotations is int:
                fields[field] = IntValidator()
            else:
                raise TypeError(f"got unhandled annotation: {type(annotations)}")

        self.validator = DictValidatorAny(fields)

    def __call__(self, val: Any) -> Validated[_DCT, Serializable]:
        if isinstance(val, self.data_cls):
            result = self.validator(val.__dict__)
            if result.is_valid:
                return Valid(self.data_cls(**result.val))
            else:
                return result
        elif isinstance(val, dict):
            result = self.validator(val)
            if result.is_valid:
                return Valid(self.data_cls(**result.val))
            else:
                return result
        else:
            return Invalid([f"expected a dict or {self.data_cls.__name__} instance"])
