import logging
import random
from typing import Any, Callable, Dict, List, Optional, Type

logger = logging.getLogger('schema_validator')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

class ValidationError(Exception):
    def __init__(self, field: str, message: str, value: Any = None):
        super().__init__(f"Field '{field}': {message} (value: {value})")
        self.field = field
        self.message = message
        self.value = value

class Field:
    def __init__(
        self,
        name: str,
        type_: Type,
        optional: bool = False,
        aliases: List[str] = None,
        custom_validator: Callable[[Any], Optional[str]] = None
    ):
        self.name = name
        self.type = type_
        self.optional = optional
        self.aliases = aliases.copy() if aliases else []
        camel = self._to_camel(name)
        if camel not in self.aliases and camel != name:
            self.aliases.append(camel)
        self.custom_validator = custom_validator

    def _to_camel(self, snake: str) -> str:
        parts = snake.split('_')
        return parts[0] + ''.join(p.title() for p in parts[1:])

    def parse(self, data: Dict[str, Any], strict: bool) -> Any:
        keys = [self.name] + self.aliases
        found_key = None
        for key in keys:
            if key in data:
                found_key = key
                break
        if found_key is None:
            if self.optional:
                return None
            raise ValidationError(self.name, "Missing required field")
        value = data[found_key]
        coerced = self._coerce(value)
        if not isinstance(coerced, self.type):
            msg = f"Expected type {self.type.__name__}"
            raise ValidationError(self.name, msg, value)
        if self.custom_validator:
            err = self.custom_validator(coerced)
            if err:
                raise ValidationError(self.name, err, coerced)
        return coerced

    def _coerce(self, value: Any) -> Any:
        if isinstance(value, self.type):
            return value
        if self.type is int:
            if isinstance(value, str) and value.isdigit():
                return int(value)
            if isinstance(value, bool):
                return int(value)
            if isinstance(value, float):
                return int(value)
        if self.type is float:
            if isinstance(value, str):
                try:
                    return float(value)
                except:
                    pass
            if isinstance(value, bool):
                return float(value)
            if isinstance(value, int):
                return float(value)
        if self.type is bool:
            if isinstance(value, str):
                val = value.lower()
                if val in ('true', '1'):
                    return True
                if val in ('false', '0'):
                    return False
            if isinstance(value, (int, float)):
                return bool(value)
        if self.type is str:
            return str(value)
        return value

class Schema:
    def __init__(self, strict: bool = False):
        self.fields: Dict[str, Field] = {}
        self.strict = strict
        self._plugins: List[Callable[['Schema'], None]] = []

    def add_field(self, field: Field):
        self.fields[field.name] = field

    def register_plugin(self, plugin: Callable[['Schema'], None]):
        self._plugins.append(plugin)
        plugin(self)

    def parse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[ValidationError] = []
        result: Dict[str, Any] = {}
        for name, field in self.fields.items():
            try:
                val = field.parse(data, self.strict)
                if val is not None or not field.optional:
                    result[name] = val
            except ValidationError as e:
                errors.append(e)
        if errors:
            for e in errors:
                logger.error({'field': e.field, 'message': e.message, 'value': e.value})
            if self.strict:
                raise Exception("Validation failed")
        return result

    def generate_mock(self) -> Dict[str, Any]:
        mock: Dict[str, Any] = {}
        for name, field in self.fields.items():
            if field.optional and random.choice([True, False]):
                continue
            t = field.type
            if t is int:
                mock[name] = 1
            elif t is float:
                mock[name] = 1.0
            elif t is bool:
                mock[name] = True
            elif t is str:
                mock[name] = f"mock_{name}"
            elif t is dict:
                mock[name] = {}
            elif t is list:
                mock[name] = []
            else:
                mock[name] = None
        return mock

    def to_json_schema(self) -> Dict[str, Any]:
        props: Dict[str, Any] = {}
        required: List[str] = []
        for name, field in self.fields.items():
            t = field.type
            js_type = 'string'
            if t is int:
                js_type = 'integer'
            elif t is float:
                js_type = 'number'
            elif t is bool:
                js_type = 'boolean'
            elif t is dict:
                js_type = 'object'
            elif t is list:
                js_type = 'array'
            props[name] = {'type': js_type}
            if not field.optional:
                required.append(name)
        schema: Dict[str, Any] = {'type': 'object', 'properties': props}
        if required:
            schema['required'] = required
        return schema
