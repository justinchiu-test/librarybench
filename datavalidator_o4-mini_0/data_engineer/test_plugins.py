from etl_validator.schema import SchemaDefinition
from etl_validator.validator import Validator
from etl_validator.plugins import PluginManager, Plugin

class DoubleQuantityPlugin(Plugin):
    def transform(self, record):
        if 'quantity' in record and isinstance(record['quantity'], (int, float)):
            record['quantity'] = record['quantity'] * 2
        return record

def test_plugin_transform_affects_validation():
    schema = SchemaDefinition({
        'fields': {
            'order_id': {'type': 'string', 'required': True},
            'quantity': {'type': 'number', 'min': 1, 'max': 100, 'required': True}
        },
        'strict': False
    })
    pm = PluginManager()
    pm.register(DoubleQuantityPlugin())
    val = Validator(schema, plugin_manager=pm)
    rec = {'order_id': '1', 'quantity': 60}
    # After doubling, quantity = 120 -> out of range
    result = val.validate(rec)
    assert not result.success
    assert any(e['field'] == 'quantity' and e['code'] == 'RANGE' for e in result.errors)
    # Lower quantity
    rec2 = {'order_id': '2', 'quantity': 10}
    r2 = val.validate(rec2)
    assert r2.success
