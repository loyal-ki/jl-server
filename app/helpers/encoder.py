import dataclasses
import json
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import PurePath
from types import GeneratorType
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from pydantic import BaseModel
from pydantic.json import ENCODERS_BY_TYPE

SetIntStr = Set[Union[int, str]]
DictIntStrAny = Dict[Union[int, str], Any]
TupleIntStr = Tuple[str]


class JsonEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        # Return a list of objects.
        if isinstance(o, set):
            return list(o)
        # Convert datetime to a string.
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        # Convert a Decimal to a string.
        if isinstance(o, Decimal):
            return str(o)
        # Decode o as a bytes object.
        if isinstance(o, bytes):
            return o.decode(encoding="utf-8")
        return self.default(o)


def generate_encoders_by_class_tuples(
    type_encoder_map: Dict[Any, Callable[[Any], Any]]
) -> Dict[Callable[[Any], Any], Tuple[Any, ...]]:
    encoders_by_class_tuples: Dict[
        Callable[[Any], Any], Tuple[Any, ...]
    ] = defaultdict(tuple)
    # Add the type_encoder_map to the map of encoders_by_class_tuples.
    for type_, encoder in type_encoder_map.items():
        encoders_by_class_tuples[encoder] += (type_,)
    return encoders_by_class_tuples


encoders_by_class_tuples = generate_encoders_by_class_tuples(ENCODERS_BY_TYPE)


def jsonable_encoder(
    obj: Any,
    include: Optional[Union[SetIntStr, DictIntStrAny, TupleIntStr]] = None,
    exclude: Optional[Union[SetIntStr, DictIntStrAny, TupleIntStr]] = None,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    custom_encoder: Optional[Dict[Any, Callable[[Any], Any]]] = None,
    sqlalchemy_safe: bool = True,
) -> Any:
    custom_encoder = custom_encoder or {}
    # Returns the encoder instance for the given object.
    if custom_encoder:
        # Returns the encoder for the given object.
        if type(obj) in custom_encoder:
            return custom_encoder[type(obj)](obj)
        else:
            # Returns the encoder instance for the given encoder type.
            for encoder_type, encoder_instance in custom_encoder.items():
                # Return the encoder instance of obj.
                if isinstance(obj, encoder_type):
                    return encoder_instance(obj)
    # Set of include values to include.
    if include is not None and not isinstance(include, (set, dict)):
        include = set(include)
    # Set exclude to exclude if exclude is not None.
    if exclude is not None and not isinstance(exclude, (set, dict)):
        exclude = set(exclude)
    # Returns a jsonable encoder for the given model.
    if isinstance(obj, BaseModel):
        encoder = getattr(obj.__config__, "json_encoders", {})
        # Update the encoder if any.
        if custom_encoder:
            encoder.update(custom_encoder)
        obj_dict = obj.dict(
            include=include,  # type: ignore # in Pydantic
            exclude=exclude,  # type: ignore # in Pydantic
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
        )
        # Return the root of the object dictionary.
        if "__root__" in obj_dict:
            obj_dict = obj_dict["__root__"]
        return jsonable_encoder(
            obj_dict,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
            custom_encoder=encoder,
            sqlalchemy_safe=sqlalchemy_safe,
        )
    # Returns a dictionary of data classes.
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    # Return the value of the enum.
    if isinstance(obj, Enum):
        return obj.value
    # Returns the string representation of the object.
    if isinstance(obj, PurePath):
        return str(obj)
    # Return the object if it is a string int float or None.
    if isinstance(obj, (str, int, float, type(None))):
        return obj
    # Returns a JSON encoded dictionary.
    if isinstance(obj, dict):
        encoded_dict = {}
        # Encode the keys and values in the dictionary.
        for key, value in obj.items():
            if (
                (
                    not sqlalchemy_safe
                    or (not isinstance(key, str))
                    or (not key.startswith("_sa"))
                )
                and (value is not None or not exclude_none)
                and (
                    (include and key in include)
                    or not exclude
                    or key not in exclude
                )
            ):
                encoded_key = jsonable_encoder(
                    key,
                    exclude=exclude,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_value = jsonable_encoder(
                    value,
                    by_alias=by_alias,
                    exclude=exclude,
                    exclude_unset=exclude_unset,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_dict[encoded_key] = encoded_value
        return encoded_dict
    # Returns a JSON encoded list of objects.
    if isinstance(obj, (list, set, frozenset, GeneratorType, tuple)):
        encoded_list = []
        # Encode the JSON encoded list of items in the object.
        for item in obj:
            encoded_list.append(
                jsonable_encoder(
                    item,
                    include=include,
                    exclude=exclude,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
            )
        return encoded_list

    # Returns the encoding of the given object.
    if type(obj) in ENCODERS_BY_TYPE:
        return ENCODERS_BY_TYPE[type(obj)](obj)
    # Returns the encoder for the given object.
    for encoder, classes_tuple in encoders_by_class_tuples.items():
        # Return the encoder for obj.
        if isinstance(obj, classes_tuple):
            return encoder(obj)

    errors: List[Exception] = []
    try:
        data = dict(obj)
    except Exception as e:
        errors.append(e)
        try:
            data = vars(obj)
        except Exception as e:
            errors.append(e)
            raise ValueError(errors)
    return jsonable_encoder(
        data,
        by_alias=by_alias,
        exclude=exclude,
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults,
        exclude_none=exclude_none,
        custom_encoder=custom_encoder,
        sqlalchemy_safe=sqlalchemy_safe,
    )
