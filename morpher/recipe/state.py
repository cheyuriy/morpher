from dataclasses import dataclass, field
from .values import Value

@dataclass
class MorphState:
    source_fields: dict = field(default_factory=dict)
    temp_fields: dict = field(default_factory=dict)
    final_fields: dict = field(default_factory=dict)
    dropped_fields: dict = field(default_factory=dict)
    value: Value = None