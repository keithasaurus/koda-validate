from argparse import ArgumentParser
from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Generic, List

from bench import (
    min_max,
    nested_object_list,
    one_key_invalid_types,
    two_keys_invalid_types,
    two_keys_valid,
    validate_string,
)
from koda_validate._generics import A


@dataclass
class BenchCompare(Generic[A]):
    gen: Callable[[int], A]
    kv_run: Callable[[List[A]], None]
    pyd_run: Callable[[List[A]], None]


benches = {
    "one_key_invalid_types": BenchCompare(
        lambda i: {"val_1": i},
        one_key_invalid_types.run_kv,
        one_key_invalid_types.run_pyd,
    ),
    "two_keys_invalid_types": BenchCompare(
        lambda i: {"val_1": i, "val_2": str(i)},
        two_keys_invalid_types.run_kv,
        two_keys_invalid_types.run_pyd,
    ),
    "two_keys_valid": BenchCompare(
        lambda i: {"val_1": str(i), "val_2": i},
        two_keys_valid.run_kv,
        two_keys_valid.run_pyd,
    ),
    "nested_object_list": BenchCompare(
        nested_object_list.get_valid_data,
        nested_object_list.run_kv,
        nested_object_list.run_pyd,
    ),
    "string_valid": BenchCompare(
        validate_string.get_str, validate_string.run_kv, validate_string.run_pyd
    ),
    "min_max_all_valid": BenchCompare(min_max.gen_valid, min_max.run_kv, min_max.run_pyd),
    "min_max_all_invalid": BenchCompare(
        min_max.gen_invalid, min_max.run_kv, min_max.run_pyd
    ),
}


def run_bench(
    chunks: int, chunk_size: int, gen: Callable[[int], A], fn: Callable[[List[A]], None]
) -> None:
    total_time: float = 0.0
    for i in range(chunks):
        # generate in chunks so generation isn't included in the
        # measured time
        objs = [gen((i * chunk_size) + j + 1) for j in range(chunk_size)]
        start = perf_counter()
        fn(objs)
        total_time += perf_counter() - start

    print(f"Execution time: {total_time:.4f} secs\n")


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
        default=50,
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1_000,
    )

    args = parser.parse_args()

    print(f"{args.iterations} ITERATIONS of {args.chunk_size}")

    for name, compare_bench in benches.items():
        if args.tests == [] or name in args.tests:
            print(f"----- BEGIN {name} -----\n")
            print("KODA_VALIDATE")
            run_bench(
                args.iterations, args.chunk_size, compare_bench.gen, compare_bench.kv_run
            )
            print("PYDANTIC")
            run_bench(
                args.iterations, args.chunk_size, compare_bench.gen, compare_bench.pyd_run
            )
            print(f"----- END {name} -----\n")
