from koda_validate.base import _ExactTypeValidator


class BoolValidator(_ExactTypeValidator[bool]):
    _TYPE = bool
