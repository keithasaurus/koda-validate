from koda_validate._internal import _ExactTypeValidator


class IntValidator(_ExactTypeValidator[int]):
    _TYPE = int
