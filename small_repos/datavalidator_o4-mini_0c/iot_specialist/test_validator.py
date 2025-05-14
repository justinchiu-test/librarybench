import pytest
from telemetry.errors import ValidationError
from telemetry.registry import AsyncRegistryClient
from telemetry.validator import TelemetryValidator

class DummyPlugin:
    def process(self, record):
        record['processed'] = True
        return record

@pytest.mark.asyncio
async def test_valid_payload():
    registry = AsyncRegistryClient({'dev1'})
    validator = TelemetryValidator(registry_client=registry, plugins=[DummyPlugin()], strict=True)
    record = {
        'device_id': 'dev1',
        'device_mode': 'active',
        'power_source': 'battery',
        'battery_voltage': 50,
        'temperature': 20,
        'humidity': 50,
        'gps': (10.0, 20.0)
    }
    res = await validator.validate(record)
    assert res['firmware_version'] == '1.0.0'
    assert res['processed'] is True

@pytest.mark.asyncio
async def test_missing_battery_voltage():
    registry = AsyncRegistryClient({'dev1'})
    validator = TelemetryValidator(registry_client=registry)
    record = {
        'device_id': 'dev1',
        'device_mode': 'active',
        'power_source': 'battery',
        'temperature': 20,
        'humidity': 50
    }
    with pytest.raises(ValidationError):
        await validator.validate(record)

@pytest.mark.asyncio
async def test_enum_invalid():
    registry = AsyncRegistryClient({'dev1'})
    validator = TelemetryValidator(registry_client=registry)
    record = {
        'device_id': 'dev1',
        'device_mode': 'running',
        'power_source': 'ac',
        'temperature': 0,
        'humidity': 0
    }
    with pytest.raises(ValidationError):
        await validator.validate(record)

@pytest.mark.asyncio
async def test_temperature_range():
    registry = AsyncRegistryClient({'dev1'})
    validator = TelemetryValidator(registry_client=registry)
    rec = {'device_id': 'dev1', 'device_mode': 'sleep', 'power_source': 'ac', 'temperature': -50, 'humidity': 10}
    with pytest.raises(ValidationError):
        await validator.validate(rec)

@pytest.mark.asyncio
async def test_humidity_range():
    registry = AsyncRegistryClient({'dev1'})
    validator = TelemetryValidator(registry_client=registry)
    rec = {'device_id': 'dev1', 'device_mode': 'sleep', 'power_source': 'ac', 'temperature': 10, 'humidity': 200}
    with pytest.raises(ValidationError):
        await validator.validate(rec)

@pytest.mark.asyncio
async def test_invalid_certificate():
    registry = AsyncRegistryClient({'other'})
    validator = TelemetryValidator(registry_client=registry)
    rec = {'device_id': 'dev1', 'device_mode': 'sleep', 'power_source': 'ac', 'temperature': 10, 'humidity': 10}
    with pytest.raises(ValidationError):
        await validator.validate(rec)

@pytest.mark.asyncio
async def test_optional_gps_invalid():
    registry = AsyncRegistryClient({'dev1'})
    validator = TelemetryValidator(registry_client=registry)
    rec = {
        'device_id': 'dev1',
        'device_mode': 'sleep',
        'power_source': 'ac',
        'temperature': 10,
        'humidity': 10,
        'gps': (91, 0)
    }
    with pytest.raises(ValidationError):
        await validator.validate(rec)

@pytest.mark.asyncio
async def test_existing_firmware():
    registry = AsyncRegistryClient({'dev1'})
    validator = TelemetryValidator(registry_client=registry)
    rec = {
        'device_id': 'dev1',
        'device_mode': 'active',
        'power_source': 'ac',
        'temperature': 10,
        'humidity': 10,
        'firmware_version': '2.0.0'
    }
    res = await validator.validate(rec)
    assert res['firmware_version'] == '2.0.0'
