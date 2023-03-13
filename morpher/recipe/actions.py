import jsonpath_ng
from abc import ABC, abstractmethod
from copy import copy
from .state import MorphState
from .values import Value, AbsentValue, NullValue, ObjectValue, ListValue, ScalarValue
from .value_types import FinalType
from .functions import registered_functions

#All actions and corresponding transformations are there
#Every action "runs" by applying different transformations to the passed state

str_to_final_type = {
    "string": FinalType.STRING,
    "integer": FinalType.INTEGER,
    "decimal": FinalType.DECIMAL,
    "float": FinalType.FLOAT,
    "timestamp": FinalType.TIMESTAMP,
    "unixtime": FinalType.UNIXTIME,
    "unixtime_ms": FinalType.UNIXTIME_MS,
    "bool": FinalType.BOOL,
    "json": FinalType.JSON,
    "date": FinalType.DATE
}

class Action(ABC):
    """Base class for Actiona. 
    Every action can be run through the usage of `run` method, which should receive some state and return updated state.
    """
    @abstractmethod
    def run(self, input: MorphState) -> MorphState:
        input.value = input.source_fields 

class Take(Action):
    def __init__(self, args) -> None:
        super().__init__()
        self.name = args[0]

    def run(self, input: MorphState) -> MorphState:
        if self.name in input.temp_fields:
            input.value = input.temp_fields[self.name]
        elif self.name in input.source_fields:
            input.value = input.source_fields[self.name]
        else: 
            if len(input.temp_fields):
                for k,v in input.temp_fields.items():
                    name_wo_delimiter = k.split("$")[0]
                    if self.name == k.split("$")[0]:
                        input.value = v 
                        input.value.actual_name = name_wo_delimiter
                        return input
            input.value = AbsentValue(original_name=self.name)

        return input

class Drop(Action):
    def __init__(self, args) -> None:
        super().__init__()
        self.name = args[0]

    def run(self, input: MorphState) -> MorphState:
        input.value = AbsentValue(original_name=self.name, actual_name=self.name)
        if self.name in input.dropped_fields:
            return input 
        elif self.name in input.source_fields:
            value_to_drop = input.source_fields[self.name]
            input.dropped_fields.update({self.name: value_to_drop})
            return input

class Full(Action):
    def __init__(self, args=None) -> None:
        super().__init__()

    def run(self, input: MorphState) -> MorphState:
        return input

class Partial(Action):
    def __init__(self, args) -> None:
        super().__init__()
        self.fields_to_keep = args 

    def run(self, input: MorphState) -> MorphState:
        if isinstance(input.value, AbsentValue):
            return input
        if isinstance(input.value, NullValue):
            return input
        if not isinstance(input.value, ObjectValue):
            raise ValueError
        old_v = input.value.value
        new_v = {k: v for k,v in old_v.items() if k in self.fields_to_keep}
        input.value.value = new_v
        return input

class First(Action):
    def __init__(self, args=None) -> None:
        super().__init__()

    def run(self, input: MorphState) -> MorphState:
        #TODO: move NullValue processing as a decorator
        if isinstance(input.value, AbsentValue):
            return input
        if isinstance(input.value, NullValue):
            return input
        if not isinstance(input.value, ListValue):
            raise ValueError
        old_v = input.value.value
        if len(old_v) == 0:
            null_value = NullValue.inherit(input.value)
            input.value = null_value
            return input
        else:
            new_v = old_v[0]
            input.value = Value.create_value_from_previous(input.value, new_v)
            return input

class Last(Action):
    def __init__(self, args=None) -> None:
        super().__init__()

    def run(self, input: MorphState) -> MorphState:
        if isinstance(input.value, AbsentValue):
            return input
        if isinstance(input.value, NullValue):
            return input
        if not isinstance(input.value, ListValue):
            raise ValueError
        old_v = input.value.value
        if len(old_v) == 0:
            null_value = NullValue.inherit(input.value)
            input.value = null_value
            return input
        else:
            new_v = old_v[-1]
            input.value = Value.create_value_from_previous(input.value, new_v)
            return input

class Nth(Action):
    def __init__(self, args) -> None:
        super().__init__()
        self.index = int(args[0])

    def run(self, input: MorphState) -> MorphState:
        if isinstance(input.value, AbsentValue):
            return input
        if isinstance(input.value, NullValue):
            return input
        if not isinstance(input.value, ListValue):
            raise ValueError
        old_v = input.value.value
        if abs(self.index) >= len(old_v):
            null_value = NullValue.inherit(input.value)
            input.value = null_value
            return input
        else:
            new_v = old_v[self.index]
            input.value = Value.create_value_from_previous(input.value, new_v)
            return input

class ID(Action):
    def __init__(self, args=None) -> None:
        super().__init__()

    def run(self, input: MorphState) -> MorphState:
        return input

class Extract(Action):
    def __init__(self, args) -> None:
        super().__init__()
        self.path = jsonpath_ng.parse(args[0])

    def run(self, input: MorphState) -> MorphState:
        if isinstance(input.value, AbsentValue):
            return input
        if isinstance(input.value, NullValue):
            return input
        if not isinstance(input.value, ObjectValue):
            raise ValueError
        old_v = input.value.value
        new_v = self.path.find(old_v)
        if len(new_v) > 1:
            new_v = [match.value for match in new_v]
        elif len(new_v) == 1:
            new_v = new_v[0].value
        else:
            null_value = NullValue.inherit(input.value)
            input.value = null_value
            return input

        input.value = Value.create_value_from_previous(input.value, new_v)
        
        return input

class Flatten(Action):
    def __init__(self, args=None) -> None:
        super().__init__()

    def run(self, input: MorphState) -> MorphState:
        if isinstance(input.value, AbsentValue):
            return input
        if isinstance(input.value, NullValue):
            return input
        if not isinstance(input.value, ObjectValue):
            raise ValueError

        old_v = input.value.value
        flatten_v = ListValue.inherit(input.value, new_value=[])
        for k, v in old_v.items():
            new_value = Value.create_value_from_previous(input.value, v)
            new_value.actual_name = input.value.actual_name + "_" + k
            flatten_v.value.append(new_value)

        input.value = flatten_v
        return input

class Apply(Action):
    def __init__(self, args) -> None:
        super().__init__()

        self.f = registered_functions().get(args[0])
        if self.f is None:
            raise ValueError

    def run(self, input: MorphState) -> MorphState:
        if isinstance(input.value, AbsentValue):
            return input
        results = self.f(input.value.value)
        if isinstance(results, list):
            list_of_values = []
            for i in results:
                list_of_values.append(Value.create_value_from_previous(input.value, i))
            new_v = ListValue.inherit(input.value, new_value=list_of_values)
            input.value = new_v
        elif isinstance(results, dict):
            new_v = ObjectValue.inherit(input.value, new_value=results)
            input.value = new_v
        elif any([
            isinstance(results, int),
            isinstance(results, float),
            isinstance(results, bool),
            isinstance(results, str)
        ]):
            new_v = Value.create_value_from_previous(input.value, results)
            input.value = new_v
        else:
            raise ValueError
        
        return input

class Lower(Action):
    def __init__(self, args=None) -> None:
        super().__init__()

    def run(self, input: MorphState) -> MorphState:
        if isinstance(input.value, AbsentValue):
            return input
        if not isinstance(input.value, ScalarValue):
            return input
        
        old_v = input.value.value
        new_v = old_v.lower() if isinstance(old_v, str) else old_v

        input.value = Value.create_value_from_previous(input.value, new_v)
        
        return input

class Upper(Action):
    def __init__(self, args=None) -> None:
        super().__init__()

    def run(self, input: MorphState) -> MorphState:
        if isinstance(input.value, AbsentValue):
            return input
        if not isinstance(input.value, ScalarValue):
            return input
        
        old_v = input.value.value
        new_v = old_v.upper() if isinstance(old_v, str) else old_v

        input.value = Value.create_value_from_previous(input.value, new_v)
        
        return input

class Alias(Action):
    def __init__(self, args=None) -> None:
        super().__init__()
        
        self.name = None
        if args:
            self.name = args[0]

    def run(self, input: MorphState) -> MorphState:
        if self.name:
            input.value.actual_name = self.name
            #input.temp_fields[input.value.actual_name] = copy(input.value)
        else:
            input.value.actual_name = input.value.original_name

        input.temp_fields[input.value.actual_name] = copy(input.value) 

        return input

class Prefix(Action):
    def __init__(self, args) -> None:
        super().__init__()

        self.prefix = args[0]

    def run(self, input: MorphState) -> MorphState:
        if input.value.actual_name: 
            input.value.actual_name = self.prefix + input.value.actual_name
        else:
            input.value.actual_name = self.prefix + input.value.original_name

        input.temp_fields[input.value.actual_name] = copy(input.value)

        return input

class Suffix(Action):
    def __init__(self, args) -> None:
        super().__init__()

        self.suffix = args[0]

    def run(self, input: MorphState) -> MorphState:
        if input.value.actual_name: 
            input.value.actual_name = input.value.actual_name + self.suffix
        else:
            input.value.actual_name = input.value.original_name + self.suffix

        input.temp_fields[input.value.actual_name] = copy(input.value)

        return input

class Split(Action):
    def __init__(self, args=None) -> None:
        super().__init__()

    def run(self, input: MorphState) -> MorphState:
        if isinstance(input.value, AbsentValue):
            return input
        if isinstance(input.value, NullValue):
            return input
        if not isinstance(input.value, ListValue):
            raise ValueError

        for i, v in enumerate(input.value):
            input.temp_fields["{}${}".format(v.actual_name, i)] = copy(v)

        return input    

class Cast(Action):
    def __init__(self, args) -> None:
        super().__init__()

        self.target_type = str_to_final_type[args[0]]

    def run(self, input: MorphState) -> MorphState:
        new_v = self.target_type.cast(input.value.value, is_safe=False)
        input.value.value = new_v
        input.value.actual_type = self.target_type

        input.final_fields[input.value.actual_name] = copy(input.value)
        input.value = AbsentValue()

        return input

class SafeCast(Action):
    def __init__(self, args) -> None:
        super().__init__()

        self.target_type = str_to_final_type[args[0]]

    def run(self, input: MorphState) -> MorphState:
        new_v = self.target_type.cast(input.value.value, is_safe=True)
        input.value.value = new_v
        input.value.actual_type = self.target_type

        input.final_fields[input.value.actual_name] = copy(input.value)
        input.value = AbsentValue()

        return input

class DefaultCast(Action):
    def __init__(self, args) -> None:
        super().__init__()

        self.target_type = str_to_final_type[args[0]]
        self.default_value = None 
        if len(args) > 1:
            self.default_value = args[1]

    def run(self, input: MorphState) -> MorphState:
        new_v = self.target_type.cast(input.value.value, is_safe=True, with_default=True, default_value=self.default_value)
        input.value.value = new_v
        input.value.actual_type = self.target_type

        input.final_fields[input.value.actual_name] = copy(input.value)
        input.value = AbsentValue()

        return input