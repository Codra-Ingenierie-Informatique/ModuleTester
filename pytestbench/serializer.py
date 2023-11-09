# pylint: disable=empty-docstring, missing-class-docstring,
# pylint: disable=missing-function-docstring, missing-module-docstring
import json
from abc import ABC, abstractmethod
from dataclasses import asdict, fields, is_dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar, get_args

from pytestbench.python_helpers import SupportsWrite, get_original_bases

# ============================================================================
#
#           SerializerBase
#
# ============================================================================


ISerializerT = TypeVar("ISerializerT")
IJsonT = TypeVar("IJsonT")


class IJSONSerializer(ABC, Generic[ISerializerT, IJsonT]):
    TYPES: Dict[Any, "IJSONSerializer[ISerializerT, IJsonT]"] = {}

    @classmethod
    def register_data_type(
        cls, data_type: Any, serializer: Optional["IJSONSerializer"] = None
    ) -> None:
        cls.TYPES[data_type] = serializer or cls()

    @abstractmethod
    def serialize(self, obj: ISerializerT) -> IJsonT:
        ...

    @abstractmethod
    def deserialize(self, obj: IJsonT) -> ISerializerT:
        ...


class ObjectSerializerBase(IJSONSerializer[ISerializerT, Dict[str, Any]]):
    DESERIALIZERS: List["ObjectSerializerBase"] = []

    def __init_subclass__(cls, *_args: Any, **_kwargs: Any) -> None:
        cls.DESERIALIZERS.append(cls())

    @classmethod
    def dump(cls, obj: Any, out: SupportsWrite, indent=2, **kwargs: Any) -> None:
        json.dump(obj, out, default=cls.serialize_obj, indent=indent, **kwargs)

    @classmethod
    def serialize_obj(cls, obj: Any) -> Dict[str, Any]:
        serializer = cls.TYPES[type(obj)]
        return serializer.serialize(obj)

    @classmethod
    def load(cls, in_, **kwargs: Any) -> Any:
        return json.load(in_, object_hook=cls.deserialize_obj, **kwargs)

    @classmethod
    def deserialize_obj(cls, obj: Dict[str, Any]) -> Any:
        for deserializer in cls.DESERIALIZERS:
            instance = deserializer.deserialize(obj)
            if instance is not None:
                return instance

        raise ValueError(f"No deserializer found for obj {obj}")


class ValueSerializerBase(IJSONSerializer[ISerializerT, IJsonT]):
    def __init_subclass__(cls, *_args: Any, **_kwargs: Any) -> None:
        data_type = get_args(get_original_bases(cls)[0])[0]
        cls.register_data_type(data_type)


# ============================================================================
#
#       Helpers Serialization class
#
# ============================================================================


class DataclassSerializer(ObjectSerializerBase[Any]):
    DATACLASS_DICT: Dict[Tuple[str, ...], Tuple[Any, Any]] = {}

    @classmethod
    def register(cls, dataclass_type):
        if is_dataclass(dataclass_type):
            cls.register_data_type(dataclass_type)

            field_list = [
                fld
                for fld in sorted(fields(dataclass_type), key=lambda fld: fld.name)
                if not fld.name.startswith("_")
            ]

            attr_names = tuple(fld.name for fld in field_list)
            attr_types = tuple(fld.type for fld in field_list)
            cls.DATACLASS_DICT[attr_names] = (dataclass_type, attr_types)

            return dataclass_type

        raise TypeError("Type not recognized when registering")

    def serialize(self, obj: Any) -> Dict[str, Any]:
        dobj = asdict(obj)
        serial = dict(
            (key, getattr(obj, key)) for key in dobj if not key.startswith("_")
        )

        return serial

    def deserialize(self, obj: Dict[str, Any]) -> Any:
        attr_names = tuple(sorted(obj.keys()))
        if attr_names not in self.DATACLASS_DICT:
            return None

        dataclass_type, attr_types = self.DATACLASS_DICT[attr_names]

        for attr_name, attr_type in zip(attr_names, attr_types):
            if attr_type in self.TYPES:
                value = obj[attr_name]
                if not isinstance(value, attr_type):
                    obj[attr_name] = self.TYPES[attr_type].deserialize(value)

        instance = dataclass_type(**obj)

        return instance


EnumT = TypeVar("EnumT", bound=Enum)


class EnumSerializer(IJSONSerializer[EnumT, str], Generic[EnumT]):
    @classmethod
    def register(cls, enum_type: Type[EnumT]) -> Type[EnumT]:
        cls(enum_type)
        return enum_type

    def __init__(self, enum_type: Type[EnumT]):
        self.enum_type = enum_type
        self.register_data_type(enum_type, self)

    def serialize(self, obj: EnumT) -> str:
        return obj.name

    def deserialize(self, obj: str) -> EnumT:
        return self.enum_type[obj]


class DateTimeSerializer(ValueSerializerBase[datetime, str]):
    DATETIME_FORMAT = "%d/%m/%y %H:%M:%S.%f"

    def serialize(self, obj: datetime) -> str:
        return obj.strftime(self.DATETIME_FORMAT)

    def deserialize(self, obj: str) -> datetime:
        return datetime.strptime(obj, self.DATETIME_FORMAT)


class TimedeltaSerializer(ValueSerializerBase[timedelta, float]):
    def serialize(self, obj: timedelta) -> float:
        return obj.total_seconds()

    def deserialize(self, obj: float) -> timedelta:
        return timedelta(seconds=obj)


def dumper(path: str, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as output:
        ObjectSerializerBase.dump(obj, output)


def loader(path: str) -> Any:
    with open(path, encoding="utf-8") as obj:
        return ObjectSerializerBase.load(obj)
