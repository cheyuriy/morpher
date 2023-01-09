from dataclasses import dataclass
from typing import Any
from .value_types import ValueType, TempType

@dataclass
class Value:
    original_name: str = None 
    actual_name: str = None 
    original_type: TempType = None 
    actual_type: ValueType = None
    value: Any = None 

    @classmethod
    def inherit(cls, prev_value, new_name: str=None, new_type: ValueType=None, new_value: Any=None):
        return cls(
            prev_value.original_name,
            new_name if new_name else prev_value.actual_name,
            prev_value.original_type,
            new_type if new_type else prev_value.actual_type,
            new_value
        )

    @classmethod
    def create_value_from_previous(cls, value, s: Any):
        if isinstance(s, int):
            new_value = ScalarValue.inherit(value, new_type=TempType.INTEGER, new_value=s)
        elif isinstance(s, float):
            new_value = ScalarValue.inherit(value, new_type=TempType.FLOAT, new_value=s)
        elif isinstance(s, str):
            new_value = ScalarValue.inherit(value, new_type=TempType.STRING, new_value=s)
        elif isinstance(s, bool):
            new_value = ScalarValue.inherit(value, new_type=TempType.BOOL, new_value=s)
        elif isinstance(s, list):
            new_value = ListValue.inherit(value, new_type=TempType.LIST, new_value=s)
        elif isinstance(s, dict):
            new_value = ObjectValue.inherit(value, new_type=TempType.OBJECT, new_value=s)
        elif s is None:
            new_value = NullValue.inherit(value)
        else:
            raise ValueError

        return new_value

    @classmethod
    def create_value(cls, name, s):
        if isinstance(s, int):
            new_value = ScalarValue(original_name=name, actual_name=name, original_type=TempType.INTEGER, actual_type=TempType.INTEGER, value=s)
        elif isinstance(s, float):
            new_value = ScalarValue(original_name=name, actual_name=name, original_type=TempType.FLOAT, actual_type=TempType.FLOAT, value=s)
        elif isinstance(s, str):
            new_value = ScalarValue(original_name=name, actual_name=name, original_type=TempType.STRING, actual_type=TempType.STRING, value=s)
        elif isinstance(s, bool):
            new_value = ScalarValue(original_name=name, actual_name=name, original_type=TempType.BOOL, actual_type=TempType.BOOL, value=s)
        elif isinstance(s, list):
            new_value = ListValue(original_name=name, actual_name=name, original_type=TempType.LIST, actual_type=TempType.LIST, value=s)
        elif isinstance(s, dict):
            new_value = ObjectValue(original_name=name, actual_name=name, original_type=TempType.OBJECT, actual_type=TempType.OBJECT, value=s)
        elif s is None:
            new_value = NullValue(original_name=name, actual_name=name)
        else:
            raise ValueError

        return new_value

@dataclass
class AbsentValue(Value):
    pass

@dataclass
class NullValue(Value):
    pass 

@dataclass
class ListValue(Value):
    def __getitem__(self, i):
        return self.value[i]

@dataclass
class ScalarValue(Value):
    pass 

@dataclass
class ObjectValue(Value):
    pass