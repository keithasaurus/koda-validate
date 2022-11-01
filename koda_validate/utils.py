from typing import Callable, Final, List, Optional, Tuple

from koda import Err, Ok, Result

from koda_validate._generics import A, FailT
from koda_validate.typedefs import Predicate, PredicateAsync, Processor, Serializable


def _handle_accum(val: A, errors: List[Serializable]) -> Result[A, Serializable]:
    if len(errors) > 0:
        return Err(errors)
    else:
        # has to be original val because there are no
        # errors, and predicates prevent there from being
        # modification to the value
        return Ok(val)


def accum_errors(
    val: A, validators: Tuple[Predicate[A, Serializable], ...]
) -> Result[A, Serializable]:
    return _handle_accum(
        val,
        [
            result.val
            for validator in validators
            if isinstance(result := validator(val), Err)
        ],
    )


async def accum_errors_async(
    val: A,
    predicates: Tuple[Predicate[A, Serializable], ...],
    predicates_async: List[PredicateAsync[A, Serializable]],
) -> Result[A, Serializable]:
    return _handle_accum(
        val,
        [result.val for pred in predicates if isinstance(result := pred(val), Err)]
        + [
            result.val
            for pred in predicates_async
            if isinstance(result := await pred.validate_async(val), Err)
        ],
    )


def _variant_errors(*variants: Serializable) -> Serializable:
    return {f"variant {i + 1}": v for i, v in enumerate(variants)}


def _flat_map_same_type_if_not_none(
    fn: Optional[Callable[[A], Result[A, FailT]]],
    r: Result[A, FailT],
) -> Result[A, FailT]:
    if fn is None:
        return r
    else:
        # optimizing by not using flatmap
        if isinstance(r, Err):
            return r
        else:
            return fn(r.val)


OBJECT_ERRORS_FIELD: Final[str] = "__container__"


def _handle_scalar_processors_and_predicates(
    val: A,
    preprocessors: Optional[List[Processor[A]]],
    predicates: Tuple[Predicate[A, Serializable], ...],
) -> Result[A, Serializable]:
    if preprocessors is not None:
        for proc in preprocessors:
            val = proc(val)

    if len(predicates) > 0:
        errors = [
            result.val for pred in predicates if isinstance(result := pred(val), Err)
        ]
        if len(errors) > 0:
            return Err(errors)
        else:
            # has to be original val because there are no
            # errors, and predicates prevent there from being
            # modification to the value
            return Ok(val)
    else:
        return Ok(val)


async def _handle_scalar_processors_and_predicates_async(
    val: A,
    preprocessors: Optional[List[Processor[A]]],
    predicates: Tuple[Predicate[A, Serializable], ...],
    predicates_async: Optional[List[PredicateAsync[A, Serializable]]],
) -> Result[A, Serializable]:
    if preprocessors is not None:
        for proc in preprocessors:
            val = proc(val)

    errors = []

    if len(predicates) > 0:
        errors.extend(
            [result.val for pred in predicates if isinstance(result := pred(val), Err)]
        )
    if predicates_async is not None:
        errors.extend(
            [
                result.val
                for pred in predicates_async
                if isinstance(result := await pred.validate_async(val), Err)
            ]
        )
    if len(errors) > 0:
        return Err(errors)
    else:
        # has to be original val because there are no
        # errors, and predicates prevent there from being
        # modification to the value
        return Ok(val)


SCALAR_SYNC_ASYNC_SLOTS_AND_MATCH_ARGS: Final[Tuple[str, ...]] = (
    "predicates",
    "predicates_async",
    "preprocessors",
)
