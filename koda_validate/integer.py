from koda_validate.base import _ExactTypeValidator


class IntValidator(_ExactTypeValidator[int]):
    _TYPE = int
