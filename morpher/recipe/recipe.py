from copy import copy
from enum import Enum 
from typing import List, Any
from .state import MorphState
from .values import Value
from .value_types import TempType, FinalType
from .actions import *
from ..morpher_parser import Instruction, Input, Pointer, Transformation, Naming, Casting
from ..morpher_parser import InputOperation, PointerOperation, TransformationOperation, NamingOperation, CastingOperation

SourceFieldStrategy = Enum("SourceFieldStrategy", ["AUTO_FINALIZE", "AUTO_DROP"])

class Recipe:
    _op_to_action = {
        Input.TAKE: Take,
        Input.DROP: Drop,
        Pointer.FULL: Full,
        Pointer.PARTIAL: Partial,
        Pointer.FIRST: First,
        Pointer.LAST: Last,
        Pointer.NTH: Nth,
        Transformation.ID: ID,
        Transformation.EXTRACT: Extract,
        Transformation.FLATTEN: Flatten,
        Transformation.APPLY: Apply,
        Transformation.LOWER: Lower,
        Transformation.UPPER: Upper,
        Naming.ALIAS: Alias,
        Naming.PREFIX: Prefix,
        Naming.SUFFIX: Suffix,
        Naming.SPLIT: Split,
        Casting.CAST: Cast,
        Casting.SAFE_CAST: SafeCast,
        Casting.DEFAULT_CAST: DefaultCast
    }

    _initial_type_to_final_type = {
        TempType.STRING: "string",
        TempType.BOOL: "bool",
        TempType.FLOAT: "float",
        TempType.INTEGER: "integer",
        TempType.LIST: "json",
        TempType.OBJECT: "json"
    }

    def __init__(
        self, 
        source_fields_stategy: SourceFieldStrategy = SourceFieldStrategy.AUTO_DROP, 
        with_source_fields_timestamp_cast: bool = False
    ) -> None:
        self.source_fields_stategy = source_fields_stategy
        self.with_source_fields_timestamp_cast = with_source_fields_timestamp_cast
        self.is_set_up = False

    def _create_default_instruction(self, field_name: str, original_type: TempType, value: Any) -> Instruction:
        final_type = self._initial_type_to_final_type[original_type]
        
        if final_type == "string" and self.with_source_fields_timestamp_cast:
            try:
                FinalType.TIMESTAMP.cast(value)
                final_type = "timestamp"
            except Exception as e:
                pass
        
        ops = [
            InputOperation.new(Input.TAKE, [field_name]),
            PointerOperation.new(Pointer.FULL),
            TransformationOperation.new(Transformation.ID),
            NamingOperation.new(Naming.ALIAS),
            CastingOperation.new(Casting.CAST, [final_type])
        ]

        return Instruction(ops)

    def _process_source_fields(self, source_fields: dict[str, Value]) -> List[Action]:
        if self.source_fields_stategy == SourceFieldStrategy.AUTO_DROP:
            self.finalization_instructions = []
            return self.actions_list 
        elif self.source_fields_stategy == SourceFieldStrategy.AUTO_FINALIZE:
            instructions = []
            for k, v in source_fields.items():
                instructions.append(self._create_default_instruction(k, v.original_type, v.value))
            actions = self._translate_ops_to_actions(instructions)
            self.finalization_instructions = instructions
            self.actions_list = actions + self.actions_list
            return self.actions_list
        else:
            raise ValueError

    def _translate_ops_to_actions(self, instructions: List[Instruction]) -> List[Action]:
        actions_list = []
        for instruction in instructions:
            for op in instruction:
                action_class = self._op_to_action.get(op.operation, None)
                if action_class is None:
                    raise ValueError
                action = action_class(*op.args)
                actions_list.append(action)
        return actions_list

    def translate(self, instructions: List[Instruction]):
        self.original_instructions = instructions
        self.actions_list = self._translate_ops_to_actions(instructions)
        self.is_set_up = True
        return self

    def dict_to_state(self, s: dict) -> MorphState:
        source_fields = {}
        for k,v in s.items():
            source_fields[k] = Value.create_value(k, v)
        state = MorphState(source_fields)
        return state

    def _state_to_dict_and_metadata(self, state: MorphState) -> tuple[dict, dict, MorphState]:
        final_fields = state.final_fields
        dropped_fields = state.dropped_fields
        result = {}
        metadata = {}
        for k,v in final_fields.items():
            if v == dropped_fields.get(k, None):
                continue
            result[k] = v.value
            metadata[k] = {
                "from_field": v.original_name,
                "from_field_type": v.original_type,
                "type": v.actual_type.name
            }
        return result, metadata, state

    def morph(self, d: dict) -> tuple[dict, dict, MorphState]:
        if not self.is_set_up:
            raise ValueError
        initial_state = self.dict_to_state(d)
        actual_actions_list = self._process_source_fields(initial_state.source_fields)
        state = copy(initial_state)
        for action in actual_actions_list:
            state = action.run(state)

        return self._state_to_dict_and_metadata(state)


