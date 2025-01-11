from typing import Dict, List, Tuple, Union

Serializable = Union[
    None,
    int,
    str,
    bool,
    float,
    list["Serializable"],
    Tuple["Serializable", ...],
    Dict[str, "Serializable"],
]
