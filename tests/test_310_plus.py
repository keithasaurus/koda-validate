from koda_validate import BooleanValidator, DecimalValidator


def test_match_args() -> None:
    match BooleanValidator():
        case BooleanValidator(predicates):
            assert predicates == ()
        case _:
            assert False

    match DecimalValidator():
        case DecimalValidator(predicates):
            assert predicates == ()
        case _:
            assert False
