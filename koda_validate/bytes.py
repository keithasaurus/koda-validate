from koda_validate.base import _ExactTypeValidator


class BytesValidator(_ExactTypeValidator[bytes]):
    _TYPE = bytes
