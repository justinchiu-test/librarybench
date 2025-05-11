import asyncio
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo

# Validation rules
class Rule:
    def __init__(self, name):
        self.name = name

    def validate(self, value):
        raise NotImplementedError()

class AsyncRule(Rule):
    async def validate_async(self, value):
        raise NotImplementedError()

# Validation engine
class ValidationEngine:
    def __init__(self):
        self.profiles = {}
        self.current = None

    def register_rule(self, profile: str, rule):
        self.profiles.setdefault(profile, []).append(rule)

    def set_profile(self, profile: str):
        self.current = profile

    def validate(self, value):
        results = []
        for rule in self.profiles.get(self.current, []):
            res = rule.validate(value)
            results.append((rule.name, res))
        return results

    async def validate_async(self, value):
        results = []
        for rule in self.profiles.get(self.current, []):
            if isinstance(rule, AsyncRule):
                res = await rule.validate_async(value)
            else:
                res = rule.validate(value)
            results.append((rule.name, res))
        return results

# DateTime validation
class DateTimeValidator:
    @staticmethod
    def parse(date_str: str, fmt: str = None):
        if fmt:
            return datetime.strptime(date_str, fmt)
        return datetime.fromisoformat(date_str)

    @staticmethod
    def normalize(dt: datetime, tz: str = 'UTC'):
        zone = ZoneInfo(tz)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=zone)
        return dt.astimezone(zone)

    @staticmethod
    def validate_range(dt: datetime, min_dt=None, max_dt=None):
        if min_dt and dt < min_dt:
            return False
        if max_dt and dt > max_dt:
            return False
        return True

# Error localization
class ErrorLocalization:
    def __init__(self, translations=None):
        self.translations = translations or {}

    def translate(self, message_key: str, lang: str = 'en') -> str:
        return self.translations.get(lang, {}).get(message_key, message_key)

    def register_translation(self, lang: str, translations: dict):
        self.translations.setdefault(lang, {}).update(translations)

# Secure field masking
class SecureFieldMasking:
    @staticmethod
    def redact(value):
        return '****'

    @staticmethod
    def hash(value):
        if not isinstance(value, str):
            value = str(value)
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

# Plugin management
class PluginManager:
    def __init__(self):
        self._plugins = {}

    def register(self, name: str, plugin):
        self._plugins.setdefault(name, []).append(plugin)

    def get(self, name: str):
        return self._plugins.get(name, [])

    def list_plugins(self):
        return dict(self._plugins)

# Schema difference tool
class SchemaDiffTool:
    @staticmethod
    def diff(old: dict, new: dict) -> dict:
        added = {k: new[k] for k in new if k not in old}
        removed = {k: old[k] for k in old if k not in new}
        changed = {
            k: {'old': old[k], 'new': new[k]}
            for k in old if k in new and old[k] != new[k]
        }
        return {'added': added, 'removed': removed, 'changed': changed}

# Transformation pipeline
class TransformationPipeline:
    def __init__(self):
        self.transforms = []

    def add(self, func):
        self.transforms.append(func)

    def process(self, value):
        for func in self.transforms:
            value = func(value)
        return value

# Schema and registry
class Schema:
    def __init__(self, name, fields, version=1, parent=None):
        self.name = name
        self.fields = dict(fields)
        self.version = version
        self.parent = parent
        if parent:
            merged = dict(parent.fields)
            merged.update(self.fields)
            self.fields = merged

    def migrate(self, new_fields, new_version):
        return Schema(self.name, new_fields, new_version, parent=self)

class SchemaRegistry:
    def __init__(self):
        self.schemas = {}

    def register(self, schema: Schema):
        self.schemas.setdefault(schema.name, {})[schema.version] = schema

    def get(self, name, version):
        return self.schemas.get(name, {}).get(version)