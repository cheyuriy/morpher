from dataclasses import dataclass, field
from .values import Value

@dataclass
class MorphState:
    """Class to represent state of the process during morphing

    Available fields described below.

    `source_fields` is a dictionary with all fields which were present in the original structure
    `temp_fields` is a dictionary with all fields created during processing (especially from Naming operations)
    `final_fields` is a dictionary with all fields which will be included into the result structure
    `dropped_fields` is a dictionary of all dropped fields from the original structure
    `value` is a current processing value
    """
    source_fields: dict[str, Value] = field(default_factory=dict)
    temp_fields: dict[str, Value] = field(default_factory=dict)
    final_fields: dict[str, Value] = field(default_factory=dict)
    dropped_fields: dict[str, Value] = field(default_factory=dict)
    value: Value = None