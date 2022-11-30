from koda_validate._internal import _ExactTypeValidator


class BytesValidator(_ExactTypeValidator[bytes]):
    _TYPE = bytes
