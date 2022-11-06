import os.path
from argparse import ArgumentParser
from pathlib import Path

from codegen import dict_validator, tuple_  # type: ignore

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "directory", type=str, nargs="?", help="directory to put the files"
    )
    parser.add_argument("--num-keys", type=int, default=10)
    args = parser.parse_args()

    if args.directory:
        target_dir = Path(args.directory)
        target_dir.mkdir(exist_ok=True, parents=True)
    else:
        target_dir = Path(os.path.abspath(__file__)).parent.parent / "koda_validate"

    dict_code = dict_validator.generate_code(args.num_keys)
    with open(target_dir / "dictionary.py", "w") as f:
        f.write(dict_code)
