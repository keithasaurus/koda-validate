from argparse import ArgumentParser
from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from bench import (
    nested_object_list,
    one_key_invalid_types,
    two_keys_invalid_types,
    two_keys_valid,
)


@dataclass
class BenchCompare:
    kv_run: Callable[[int], None]
    pyd_run: Callable[[int], None]


benches = {
    "one_key_invalid_types": BenchCompare(
        one_key_invalid_types.run_kv, one_key_invalid_types.run_pyd
    ),
    "two_keys_invalid_types": BenchCompare(
        two_keys_invalid_types.run_kv, two_keys_invalid_types.run_pyd
    ),
    "two_keys_valid": BenchCompare(two_keys_valid.run_kv, two_keys_valid.run_pyd),
    "nested_object_list": BenchCompare(
        nested_object_list.run_kv, nested_object_list.run_pyd
    ),
}


def run_bench(iterations: int, fn: Callable[[int], None]) -> None:
    start = perf_counter()
    fn(iterations)
    t_ = perf_counter() - start
    print(f"Execution time: {t_:.4f} secs\n")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "tests",
        type=str,
        nargs="*",
        help="which tests to run",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100_000,
        help="How many iterations of each test we'll run",
    )
    args = parser.parse_args()

    print(f"{args.iterations} ITERATIONS")

    for name, compare_bench in benches.items():
        if args.tests == [] or name in args.tests:
            print(f"----- BEGIN {name} -----\n")
            print("KODA_VALIDATE")
            run_bench(args.iterations, compare_bench.kv_run)
            print("PYDANTIC")
            run_bench(args.iterations, compare_bench.pyd_run)
            print(f"----- END {name} -----\n")
