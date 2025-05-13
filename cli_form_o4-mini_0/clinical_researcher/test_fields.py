import pytest
from form_system.fields import TextField, DateTimePicker

def test_textfield_valid():
    tf = TextField('test', regex=r'^\d{3}$', max_length=3, placeholder='123')
    assert tf.validate('123') == True

def test_textfield_too_long():
    tf = TextField('test', max_length=2)
    with pytest.raises(ValueError):
        tf.validate('abc')

def test_textfield_bad_pattern():
    tf = TextField('test', regex=r'^[A-Z]+$')
    with pytest.raises(ValueError):
        tf.validate('abc')

def test_datetimepicker_valid_date_time():
    dt = DateTimePicker()
    d = dt.pick_date('2020-01-31')
    t = dt.pick_time('23:59')
    assert str(d) == '2020-01-31'
    assert t.hour == 23 and t.minute == 59

def test_datetimepicker_invalid_date():
    dt = DateTimePicker()
    with pytest.raises(ValueError):
        dt.pick_date('2020-02-30')

def test_datetimepicker_invalid_time():
    dt = DateTimePicker()
    with pytest.raises(ValueError):
        dt.pick_time('24:00')
