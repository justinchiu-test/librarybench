import threading
import asyncio
import urllib.parse
import json
import re
import yaml  # will pick up the local yaml.py above

class TemplateEngine:
    def __init__(self):
        self.auto_reload = False
        self.output_mode = 'escape'
        self.locale = 'en_US'
        self.macros = {}
        self.templates = {}
        self._precompiled = {}
        self.translations = {}

    def set_auto_reload(self, value=True):
        self.auto_reload = bool(value)

    def define_macro(self, name, args, content):
        self.macros[name] = {'args': args, 'content': content}

    def precompile_templates(self):
        for name, tpl in self.templates.items():
            # Naive "precompile": store the code object of the template string
            self._precompiled[name] = compile(repr(tpl), f'<template:{name}>', 'eval')

    def set_output_mode(self, mode):
        if mode not in ('escape', 'raw'):
            raise ValueError(f"Invalid mode: {mode}")
        self.output_mode = mode

    def url_encode(self, s):
        return urllib.parse.quote(s)

    def url_decode(self, s):
        return urllib.parse.unquote(s)

    def querystring(self, base, params):
        qs = urllib.parse.urlencode(params)
        sep = '&' if '?' in base else '?'
        return f"{base}{sep}{qs}" if qs else base

    def to_json(self, obj):
        return json.dumps(obj)

    def from_json(self, s):
        return json.loads(s)

    def to_yaml(self, obj):
        return yaml.safe_dump(obj)

    def from_yaml(self, s):
        return yaml.safe_load(s)

    def trim_whitespace(self, s):
        # Only trim around dash‐style tags, leave plain {{ var }} alone
        # variable dash‐tags
        s = re.sub(r'\s*(\{\{-[\s\S]+?-\}\})\s*',
                   lambda m: m.group(1), s)
        # control dash‐tags
        s = re.sub(r'\s*(\{%-[\s\S]+?-%\})\s*',
                   lambda m: m.group(1), s)
        return s

    def set_locale(self, locale):
        self.locale = locale

    def add_translations(self, locale, mapping):
        self.translations[locale] = mapping

    def render_to_string(self, name, context=None):
        tpl = self.templates.get(name, '')
        result = tpl
        # Apply dash‐only whitespace trimming
        if isinstance(result, str):
            result = self.trim_whitespace(result)

        # First do the standard tags (no dashes) => strip braces and insert value
        if context:
            for k, v in context.items():
                pattern = re.compile(r'\{\{\s*' + re.escape(str(k)) + r'\s*\}\}')
                result = pattern.sub(str(v), result)

            # Then handle any leftover dash‐style tags: only replace the var inside
            def _dash_replace(m):
                inner = m.group(1).strip()
                for kk, vv in context.items():
                    # word‐boundary replace inside the tag
                    inner = re.sub(r'\b' + re.escape(str(kk)) + r'\b',
                                   str(vv), inner)
                # rebuild a normalized dash‐tag
                return '{{- ' + inner + ' -}}'

            result = re.sub(r'\{\{-\s*(.+?)\s*-\}\}', _dash_replace, result)

        # Translations
        def _trans(m):
            text = m.group(1)
            return self.translations.get(self.locale, {}).get(text, text)

        result = re.sub(r'\{% trans "(.*?)" %\}', _trans, result)
        return result

    def render_to_file(self, name, context, f):
        out = self.render_to_string(name, context)
        if isinstance(f, str):
            with open(f, 'w', encoding='utf-8') as fp:
                fp.write(out)
        else:
            f.write(out)

    def render_threadsafe(self, name, context):
        # Simple thread‐safe: just call render_to_string
        return self.render_to_string(name, context)

    async def render_async(self, name, context):
        # Async wrapper
        return self.render_to_string(name, context)
