from pathlib import Path

from codegen import dict_validator, validate_and_map  # type: ignore

if __name__ == "__main__":
    num_iterations = 20

    dict_code = dict_validator.generate_code(num_iterations)
    with open(
        Path(__file__).parent.parent / "koda_validate" / "validators" / "dicts.py", "w"
    ) as f:
        f.write(dict_code)

    validate_and_map_code = validate_and_map.generate_code(num_iterations)
    with open(
        Path(__file__).parent.parent
        / "koda_validate"
        / "validators"
        / "validate_and_map.py",
        "w",
    ) as f:
        f.write(validate_and_map_code)
