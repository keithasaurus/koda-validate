from koda_validate._internal import _ExactTypeValidator


class BoolValidator(_ExactTypeValidator[bool]):
    _TYPE = bool
