import pytest
from config_manager.coercers import CoercerRegistry

def test_semver_coercer():
    cr = CoercerRegistry()
    assert cr.coerce('semver', '1.2.3') == (1,2,3)
    with pytest.raises(ValueError):
        cr.coerce('semver', '1.two.3')

def test_date_coercer():
    cr = CoercerRegistry()
    date = cr.coerce('date', '2020-05-17')
    assert hasattr(date, 'year') and date.year == 2020
    with pytest.raises(ValueError):
        cr.coerce('date', '17-05-2020')
