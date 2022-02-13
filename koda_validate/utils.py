from koda_validate._cruft import _chain, _validate_and_map


def expected(val: str) -> str:
    return f"expected {val}"


chain = _chain
validate_and_map = _validate_and_map