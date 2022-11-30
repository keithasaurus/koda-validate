from koda_validate._internal import _ExactTypeValidator


class FloatValidator(_ExactTypeValidator[float]):
    _TYPE = float
