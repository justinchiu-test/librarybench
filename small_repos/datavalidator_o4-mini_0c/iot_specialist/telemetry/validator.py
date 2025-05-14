import asyncio
from .errors import ValidationError
from .registry import AsyncRegistryClient
from .plugins import Plugin

class TelemetryValidator:
    def __init__(self, registry_client=None, plugins=None, strict=False, last_known_firmware='1.0.0'):
        self.registry = registry_client or AsyncRegistryClient()
        self.plugins = plugins or []
        self.strict = strict
        self.last_known_firmware = last_known_firmware

    async def validate(self, record):
        # Strict mode: no extra fields
        if self.strict:
            allowed = {
                'device_id', 'device_mode', 'power_source',
                'battery_voltage', 'temperature', 'humidity',
                'firmware_version', 'gps'
            }
            extra = set(record) - allowed
            if extra:
                raise ValidationError(f'Unknown fields: {extra}')

        # EnumConstraints
        mode = record.get('device_mode')
        if mode not in ('sleep', 'active', 'maintenance'):
            raise ValidationError('Invalid device_mode')

        # ConditionalValidation: battery_voltage only if power_source is battery
        ps = record.get('power_source')
        if ps == 'battery':
            if 'battery_voltage' not in record:
                raise ValidationError('Missing battery_voltage for battery power_source')
            bv = record['battery_voltage']
            if not isinstance(bv, (int, float)) or bv < 0 or bv > 100:
                raise ValidationError('battery_voltage out of range')

        # RangeChecks: temperature and humidity
        temp = record.get('temperature')
        if not isinstance(temp, (int, float)) or temp < -40 or temp > 85:
            raise ValidationError('temperature out of range')
        hum = record.get('humidity')
        if not isinstance(hum, (int, float)) or hum < 0 or hum > 100:
            raise ValidationError('humidity out of range')

        # DefaultValues: firmware_version
        if 'firmware_version' not in record or record.get('firmware_version') is None:
            record['firmware_version'] = self.last_known_firmware

        # OptionalFields: gps
        if 'gps' in record and record['gps'] is not None:
            gps = record['gps']
            if not isinstance(gps, (list, tuple)) or len(gps) != 2:
                raise ValidationError('gps must be (lat, lon)')
            lat, lon = gps
            if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                raise ValidationError('gps coords must be numbers')
            if lat < -90 or lat > 90 or lon < -180 or lon > 180:
                raise ValidationError('gps coords out of range')

        # AsyncValidation: device certificate
        valid = await self.registry.validate_certificate(record.get('device_id'))
        if not valid:
            raise ValidationError('Invalid device certificate')

        # PluginSystem: apply plugins
        for p in self.plugins:
            if hasattr(p, 'process'):
                record = p.process(record)

        return record
