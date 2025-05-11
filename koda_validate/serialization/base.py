from typing import Dict, Union

Serializable = Union[
    None,
    int,
    str,
    bool,
    float,
    list["Serializable"],
    tuple["Serializable", ...],
    Dict[str, "Serializable"],
]
