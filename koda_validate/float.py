from koda_validate.base import _ExactTypeValidator


class FloatValidator(_ExactTypeValidator[float]):
    _TYPE = float
