import asyncio
import inspect
import hashlib
from datetime import datetime
import zoneinfo

# Asynchronous validation rule
class AsyncRule:
    def __init__(self, func):
        if not callable(func):
            raise ValueError("func must be callable")
        self.func = func

    def validate(self, *args, **kwargs):
        if inspect.iscoroutinefunction(self.func):
            loop = asyncio.get_event_loop()
            if loop.is_running():
                new_loop = asyncio.new_event_loop()
                try:
                    return new_loop.run_until_complete(self.func(*args, **kwargs))
                finally:
                    new_loop.close()
            else:
                return loop.run_until_complete(self.func(*args, **kwargs))
        else:
            return self.func(*args, **kwargs)

    async def validate_async(self, *args, **kwargs):
        if inspect.iscoroutinefunction(self.func):
            return await self.func(*args, **kwargs)
        # run sync function directly
        return self.func(*args, **kwargs)

# ZoneInfo with .zone property
class ZoneInfo(zoneinfo.ZoneInfo):
    @property
    def zone(self):
        return self.key

# DateTime handling utilities
class DateTimeValidator:
    @staticmethod
    def parse(date_str: str, fmt: str = None, tz: str = None) -> datetime:
        if fmt:
            dt = datetime.strptime(date_str, fmt)
        else:
            dt = datetime.fromisoformat(date_str)
        if tz:
            tzinfo = ZoneInfo(tz)
            dt = dt.replace(tzinfo=tzinfo)
        return dt

    @staticmethod
    def normalize(dt: datetime, tz: str) -> datetime:
        target = ZoneInfo(tz)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        return dt.astimezone(target)

    @staticmethod
    def check_min_max(dt: datetime, min_dt: datetime = None, max_dt: datetime = None) -> bool:
        if min_dt is not None and dt < min_dt:
            return False
        if max_dt is not None and dt > max_dt:
            return False
        return True

# Schema difference tool
class SchemaDiffTool:
    @staticmethod
    def diff(old_schema: dict, new_schema: dict) -> dict:
        old_fields = set(old_schema.keys())
        new_fields = set(new_schema.keys())
        added = new_fields - old_fields
        removed = old_fields - new_fields
        changed = {
            field for field in old_fields & new_fields
            if old_schema[field] != new_schema[field]
        }
        return {
            'added': sorted(list(added)),
            'removed': sorted(list(removed)),
            'changed': sorted(list(changed)),
        }

# Error localization
class ErrorLocalization:
    def __init__(self):
        self._translations = {}

    def register(self, code: str, lang: str, template: str):
        self._translations.setdefault(code, {})[lang] = template

    def translate(self, code: str, lang: str, **kwargs) -> str:
        templates = self._translations.get(code, {})
        template = templates.get(lang) or templates.get('en')
        if not template:
            return code
        return template.format(**kwargs)

# Schema inheritance
class Schema:
    def __init__(self, fields: dict, parent: 'Schema' = None):
        self.parent = parent
        self.fields = fields or {}

    def resolved_fields(self) -> dict:
        if self.parent:
            resolved = self.parent.resolved_fields().copy()
            resolved.update(self.fields)
            return resolved
        return self.fields.copy()

# Plugin management
class PluginManager:
    def __init__(self):
        self._plugins = {}

    def register(self, name: str, plugin):
        self._plugins[name] = plugin

    def get(self, name: str):
        return self._plugins.get(name)

    def list(self):
        return list(self._plugins.keys())

# Profile-based rules
class ProfileRuleSet:
    def __init__(self):
        self._profiles = {}

    def add_rule(self, profile: str, name: str, rule):
        self._profiles.setdefault(profile, {})[name] = rule

    def get_rules(self, profile: str):
        return self._profiles.get(profile, {}).copy()

    def validate(self, profile: str, data):
        rules = self.get_rules(profile)
        results = {}
        for name, rule in rules.items():
            results[name] = rule(data)
        return results

# Secure field masking
class SecureFieldMasking:
    def __init__(self, fields, mask='****', hash_fields=None):
        self.fields = set(fields)
        self.mask = mask
        self.hash_fields = set(hash_fields or [])

    def mask_data(self, data: dict) -> dict:
        result = data.copy()
        for field in self.fields:
            if field in result:
                if field in self.hash_fields:
                    result[field] = hashlib.sha256(str(result[field]).encode()).hexdigest()
                else:
                    result[field] = self.mask
        return result

# Transformation pipeline
class TransformationPipeline:
    def __init__(self):
        self._transforms = []

    def add(self, func):
        if not callable(func):
            raise ValueError("Transform must be callable")
        self._transforms.append(func)

    def run(self, value):
        v = value
        for fn in self._transforms:
            v = fn(v)
        return v

# Schema versioning
class SchemaVersioning:
    def __init__(self):
        self._schemas = {}
        self._migrations = {}

    def register(self, version: str, schema_fields: dict):
        self._schemas[version] = schema_fields

    def add_migration(self, from_v: str, to_v: str, func):
        self._migrations[(from_v, to_v)] = func

    def validate(self, version: str, data: dict) -> bool:
        schema = self._schemas.get(version)
        if schema is None:
            raise ValueError("Unknown version")
        for key in schema:
            if key not in data:
                return False
        return True

    def migrate(self, data: dict, from_v: str, to_v: str) -> dict:
        if from_v == to_v:
            return data.copy()
        func = self._migrations.get((from_v, to_v))
        if not func:
            raise ValueError("Migration path not found")
        return func(data.copy())