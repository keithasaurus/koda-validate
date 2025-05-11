from typing import Union

Serializable = Union[
    None,
    int,
    str,
    bool,
    float,
    list["Serializable"],
    tuple["Serializable", ...],
    dict[str, "Serializable"],
]
