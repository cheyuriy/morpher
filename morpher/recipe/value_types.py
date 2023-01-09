import arrow
import json
from enum import Enum, auto
from typing import Any, Optional

class ValueType(Enum):
    pass 

class TempType(ValueType):
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOL = auto()
    LIST = auto()
    OBJECT = auto()

class FinalType(ValueType):
    STRING = auto()
    INTEGER = auto()
    DECIMAL = auto()
    FLOAT = auto()
    TIMESTAMP = auto()
    UNIXTIME = auto()
    UNIXTIME_MS = auto()
    BOOL = auto()
    JSON = auto()
    DATE = auto()

    def _to_string(self, value: Any) -> tuple[str, Optional[Exception]]:
        return str(value), None

    def _to_integer(self, value: Any) -> tuple[int, Optional[Exception]]:
        try:
            return int(value), None
        except Exception as e:
            return None, e

    def _to_decimal(self, value: Any) -> tuple[float, Optional[Exception]]:
        return self._to_float(value)

    def _to_float(self, value: Any) -> tuple[float, Optional[Exception]]:
        try:
            return float(value), None 
        except Exception as e:
            return None, e

    def _to_timestamp(self, value: Any) -> tuple[str, Optional[Exception]]:
        try:
            if isinstance(value, str) or isinstance(value, int):
                return arrow.get(value).to("UTC").isoformat()[:-6], None
            else:
                raise ValueError
        except Exception as e:
            return None, e

    def _to_unixtime(self, value: Any) -> tuple[int, Optional[Exception]]:
        try:
            if isinstance(value, str):
                return int(arrow.get(value).to("UTC").timestamp()), None
            elif isinstance(value, int) or isinstance(value, float):
                return int(arrow.get(int(value)).to("UTC").timestamp()), None
            else:
                raise ValueError
        except Exception as e:
            return None, e

    def _to_unixtime_ms(self, value: Any) -> tuple[int, Optional[Exception]]:
        try:
            if isinstance(value, str):
                return int(arrow.get(value).to("UTC").timestamp() * 1000), None
            elif isinstance(value, int) or isinstance(value, float):
                return int(arrow.get(value).to("UTC").timestamp() * 1000), None
            else:
                raise ValueError
        except Exception as e:
            return None, e

    def _to_bool(self, value: Any) -> tuple[bool, Optional[Exception]]:
        try:
            if value in [True, "true", "TRUE", 1]:
                return True, None 
            elif value in [False, "false", "FALSE", 0]:
                return False, None
            else: 
                raise ValueError
        except Exception as e:
            return None, e

    def _to_json(self, value: Any) -> tuple[str, Optional[Exception]]:
        try:
            return json.dumps(value, ensure_ascii=False, allow_nan=False), None
        except Exception as e:
            return None, e

    def _to_date(self, value: Any) -> tuple[str, Optional[Exception]]:
        try:
            return arrow.get(value).date().isoformat(), None
        except Exception as e:
            return None, e

    def cast(self, value: Any, is_safe: bool=False, with_default: bool=False, default_value: Any=None) -> Any:
        if value is None:
            return None

        default_values = {
            "STRING": "",
            "INTEGER": 0,
            "DECIMAL": 0.0,
            "FLOAT": 0.0,
            "TIMESTAMP": None,
            "UNIXTIME": 0,
            "UNIXTIME_MS": 0,
            "BOOL": None,
            "JSON": "{}",
            "DATE": None
        }

        if self.name == "STRING":
            v, e = self._to_string(value)
        elif self.name == "INTEGER":
            v, e = self._to_integer(value)
        elif self.name == "DECIMAL":
            v, e = self._to_decimal(value)
        elif self.name == "FLOAT":
            v, e = self._to_float(value)
        elif self.name == "TIMESTAMP":
            v, e = self._to_timestamp(value)
        elif self.name == "UNIXTIME":
            v, e = self._to_unixtime(value)
        elif self.name == "UNIXTIME_MS":
            v, e = self._to_unixtime_ms(value)
        elif self.name == "BOOL":
            v, e = self._to_bool(value)
        elif self.name == "JSON":
            v, e = self._to_json(value)
        elif self.name == "DATE":
            v, e = self._to_date(value)
        else:
            raise ValueError

        if e is None:
            return v 
        else:
            if is_safe and with_default:
                default = default_value if default_value else default_values[self.name]
                return default
            elif is_safe and not with_default:
                return None 
            else: 
                raise e 
             



             
