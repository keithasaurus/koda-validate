from koda_validate._cruft import _chain


def expected(val: str) -> str:
    return f"expected {val}"


chain = _chain