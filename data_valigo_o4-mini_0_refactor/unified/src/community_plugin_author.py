import inspect
import asyncio
import hashlib
from datetime import datetime

# Plugin registration
_rules = {}
_transformers = {}

def register_rule(name: str, profile: str = None):
    def decorator(fn):
        _rules.setdefault(name, []).append((fn, profile))
        return fn
    return decorator

def get_rule(name: str, profile: str = None):
    candidates = _rules.get(name, [])
    for fn, prof in candidates:
        if prof == profile:
            return fn
    for fn, prof in candidates:
        if prof is None:
            return fn
    return None

def register_transformer(name: str):
    def decorator(fn):
        _transformers[name] = fn
        return fn
    return decorator

def get_transformer(name: str):
    return _transformers.get(name)

class AsyncValidationError(Exception):
    pass

class Validator:
    def __init__(self, profile: str = None):
        self.profile = profile

    async def _run_rule(self, rule_fn, value, context):
        if inspect.iscoroutinefunction(rule_fn):
            return await rule_fn(value, context)
        else:
            return rule_fn(value, context)

    def validate(self, name: str, value, context=None):
        context = context or {}
        context['profile'] = self.profile
        rule_fn = get_rule(name, self.profile)
        if not rule_fn:
            raise AsyncValidationError(f"No rule registered: {name}")
        result = rule_fn(value, context)
        if inspect.isawaitable(result):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(result)
        return result

    async def validate_async(self, name: str, value, context=None):
        context = context or {}
        context['profile'] = self.profile
        rule_fn = get_rule(name, self.profile)
        if not rule_fn:
            raise AsyncValidationError(f"No rule registered: {name}")
        return await self._run_rule(rule_fn, value, context)

# DateTime utilities
def parse_date(date_str: str, fmt: str = None) -> datetime:
    if fmt:
        return datetime.strptime(date_str, fmt)
    return datetime.fromisoformat(date_str)

def normalize_timezone(dt: datetime, tzinfo) -> datetime:
    if dt.tzinfo:
        return dt.astimezone(tzinfo)
    return dt.replace(tzinfo=tzinfo)

def min_date(dt: datetime, min_dt: datetime):
    if dt < min_dt:
        raise ValueError(f"Date {dt} is before minimum {min_dt}")
    return dt

def max_date(dt: datetime, max_dt: datetime):
    if dt > max_dt:
        raise ValueError(f"Date {dt} is after maximum {max_dt}")
    return dt

# Error localization
class ErrorLocalizer:
    def __init__(self, default_lang='en'):
        self.default = default_lang
        self._backends = {}

    def register(self, lang: str, fn):
        self._backends[lang] = fn

    def translate(self, msg: str, lang: str = None) -> str:
        lang = lang or self.default
        fn = self._backends.get(lang)
        if fn:
            try:
                return fn(msg)
            except Exception:
                return msg
        return msg

# Schema and migrations
class Schema:
    def __init__(self, fields: dict, parent: 'Schema' = None):
        self.parent = parent
        if parent:
            merged = dict(parent.fields)
            merged.update(fields)
            self.fields = merged
        else:
            self.fields = dict(fields)

    def validate(self, data: dict) -> bool:
        for k, t in self.fields.items():
            if k not in data:
                raise ValueError(f"Missing field {k}")
            if not isinstance(data[k], t):
                raise TypeError(f"Field {k} expected {t}, got {type(data[k])}")
        return True

class VersionedSchema(Schema):
    def __init__(self, fields: dict, version: int, parent: 'VersionedSchema' = None):
        super().__init__(fields, parent)
        self.version = version
        self._migrations = {}

    def add_migration(self, from_version: int, fn):
        self._migrations[from_version] = fn

    def migrate(self, data: dict, target_version: int) -> dict:
        vs = dict(data)
        cur = self.version
        if target_version < cur:
            raise ValueError(f"No migration from {cur} to {target_version}")
        for v in range(cur, target_version):
            fn = self._migrations.get(v)
            if not fn:
                raise ValueError(f"No migration from {v}")
            vs = fn(vs)
        return vs

# Schema diff tool
class SchemaDiffTool:
    @staticmethod
    def compute_diff(schema1: dict, schema2: dict) -> dict:
        added = {k: schema2[k] for k in schema2 if k not in schema1}
        removed = {k: schema1[k] for k in schema1 if k not in schema2}
        changed = {k: (schema1[k], schema2[k]) for k in schema1 if k in schema2 and schema1[k] != schema2[k]}
        return {"added": added, "removed": removed, "changed": changed}

# Transformation system
class TransformationPipeline:
    def __init__(self):
        self._transforms = []

    def add(self, fn):
        self._transforms.append(fn)

    def apply(self, value):
        result = value
        for fn in self._transforms:
            result = fn(result)
        return result

# Secure masking
def mask(value: str, field_type: str) -> str:
    if field_type == 'ssn':
        parts = value.split('-')
        if len(parts) == 3:
            return '***-**-' + parts[2]
    if field_type == 'cc':
        digits = ''.join(filter(str.isdigit, value))
        if len(digits) >= 4:
            return '**** **** **** ' + digits[-4:]
    return hashlib.sha256(value.encode()).hexdigest()