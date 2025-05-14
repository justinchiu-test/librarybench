import pytest
from config.coercers import coerce_date, coerce_duration, coerce_optimizer, Optimizer
from datetime import datetime, timedelta

def test_coerce_date():
    dt = coerce_date('2021-01-01')
    assert dt == datetime(2021,1,1)

def test_coerce_duration_min():
    td = coerce_duration('30min')
    assert td == timedelta(minutes=30)

def test_coerce_duration_h():
    td = coerce_duration('2h')
    assert td == timedelta(hours=2)

def test_coerce_duration_invalid():
    with pytest.raises(ValueError):
        coerce_duration('5days')

def test_coerce_optimizer():
    opt = coerce_optimizer('sgd')
    assert opt == Optimizer.SGD
    opt = coerce_optimizer('ADAM')
    assert opt == Optimizer.ADAM

def test_coerce_optimizer_invalid():
    with pytest.raises(ValueError):
        coerce_optimizer('rmsprop')
