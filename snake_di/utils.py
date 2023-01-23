from typing import Any, get_args


def get_generic_first_type(class_or_instance: Any) -> Any:
    return get_args(class_or_instance.__orig_bases__[0])[0]
