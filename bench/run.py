from argparse import ArgumentParser
from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Dict, Generic, List

from bench import (
    list_none,
    min_max,
    nested_object_list,
    one_key_invalid_types,
    string_valid,
    two_keys_invalid_types,
    two_keys_valid,
)
from koda_validate._generics import A


@dataclass
class BenchCompare(Generic[A]):
    gen: Callable[[int], A]
    comparisons: Dict[str, Callable[[List[A]], None]]


KODA_VALIDATE = "KODA VALIDATE"
KV_RECORD_VALIDATOR = f"{KODA_VALIDATE} - RecordValidator"
KV_DATACLASS_VALIDATOR = f"{KODA_VALIDATE} - DataclassValidator"
KV_NAMEDTUPLE_VALIDATOR = f"{KODA_VALIDATE} - NamedTupleValidator"
KV_DICT_VALIDATOR_ANY = f"{KODA_VALIDATE} - DictValidatorAny"
KV_TYPED_DICT_VALIDATOR = f"{KODA_VALIDATE} - TypedDictValidator"


PYDANTIC = "PYDANTIC"
VOLUPTUOUS = "VOLUPTUOUS"

benches = {
    "one_key_invalid_types": BenchCompare(
        lambda i: {"val_1": i},
        {
            KODA_VALIDATE: one_key_invalid_types.run_kv,
            PYDANTIC: one_key_invalid_types.run_pyd,
        },
    ),
    "two_keys_invalid_types": BenchCompare(
        lambda i: {"val_1": i, "val_2": str(i)},
        {
            KODA_VALIDATE: two_keys_invalid_types.run_kv,
            PYDANTIC: two_keys_invalid_types.run_pyd,
            VOLUPTUOUS: two_keys_invalid_types.run_v,
        },
    ),
    "two_keys_valid": BenchCompare(
        lambda i: {"val_1": str(i), "val_2": i},
        {
            KODA_VALIDATE: two_keys_valid.run_kv,
            PYDANTIC: two_keys_valid.run_pyd,
            VOLUPTUOUS: two_keys_valid.run_v,
        },
    ),
    "string_valid": BenchCompare(
        string_valid.get_str,
        {KODA_VALIDATE: string_valid.run_kv, PYDANTIC: string_valid.run_pyd},
    ),
    "list_none": BenchCompare(
        list_none.get_obj, {KODA_VALIDATE: list_none.run_kv, PYDANTIC: list_none.run_pyd}
    ),
    "min_max_all_valid": BenchCompare(
        min_max.gen_valid,
        {
            KV_RECORD_VALIDATOR: min_max.run_kv,
            KV_DICT_VALIDATOR_ANY: min_max.run_kv_dict_any,
            PYDANTIC: min_max.run_pyd,
            VOLUPTUOUS: min_max.run_v,
        },
    ),
    "min_max_all_invalid": BenchCompare(
        min_max.gen_invalid,
        {
            KV_RECORD_VALIDATOR: min_max.run_kv,
            KV_DICT_VALIDATOR_ANY: min_max.run_kv_dict_any,
            PYDANTIC: min_max.run_pyd,
            VOLUPTUOUS: min_max.run_v,
        },
    ),
    "nested_object_list": BenchCompare(
        nested_object_list.get_data,
        {
            KV_RECORD_VALIDATOR: nested_object_list.run_kv,
            KV_DATACLASS_VALIDATOR: nested_object_list.run_kv_dc,
            KV_DICT_VALIDATOR_ANY: nested_object_list.run_kv_dict_any,
            KV_NAMEDTUPLE_VALIDATOR: nested_object_list.run_kv_nt,
            KV_TYPED_DICT_VALIDATOR: nested_object_list.run_kv_td,
            PYDANTIC: nested_object_list.run_pyd,
        },
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
            for subject_name, test in compare_bench.comparisons.items():
                print(subject_name)
                run_bench(args.iterations, args.chunk_size, compare_bench.gen, test)

            print(f"----- END {name} -----\n")
