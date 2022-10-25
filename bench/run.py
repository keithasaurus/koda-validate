from argparse import ArgumentParser
from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from bench import one_key_invalid_types, two_keys_invalid_types


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
}


def run_bench(iterations: int, fn: Callable[[int], None]) -> None:
    start = perf_counter()
    fn(iterations)
    t_ = perf_counter() - start
    print(f"Execution time: {t_:.4f} secs\n")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--iterations",
        type=int,
        default=100_000,
        help="How many iterations of each test we'll run",
    )
    args = parser.parse_args()

    print(f"{args.iterations} ITERATIONS")

    for name, compare_bench in benches.items():
        print(f"----- BEGIN {name} -----\n")
        print("KODA_VALIDATE")
        run_bench(args.iterations, compare_bench.kv_run)
        print("PYDANTIC")
        run_bench(args.iterations, compare_bench.pyd_run)
        print(f"----- END {name} -----\n")
