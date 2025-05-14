"""
Manual test script to verify our implementation.
"""
import sys
print("Python version:", sys.version)
print("Testing clinical_researcher.form_system.fields...")

from clinical_researcher.form_system.fields import TextField, DateTimePicker

# Test TextField
tf = TextField('test', regex=r'^\d{3}$', max_length=3, placeholder='123')
print("Created TextField:", tf)
try:
    print("Validating '123':", tf.validate('123'))
    print("Success!")
except Exception as e:
    print("Error:", e)
    
try:
    print("Validating '1234':")
    tf.validate('1234')
    print("Failed!")
except Exception as e:
    print("Got expected error:", e)

# Test DateTimePicker
dt = DateTimePicker()
print("Created DateTimePicker:", dt)
try:
    d = dt.pick_date('2020-01-31')
    t = dt.pick_time('23:59')
    print("Date:", d)
    print("Time:", t)
    print("Success!")
except Exception as e:
    print("Error:", e)

print("\nTesting security_officer.incident_form.fields...")
from security_officer.incident_form.fields import TextField as SOTextField

# Test TextField
tf = SOTextField(pattern=r"^CVE-\d{4}-\d+$", max_length=20)
print("Created SOTextField:", tf)
ok, err = tf.input("CVE-2021-1234")
print("Input result:", ok, err)
print("Value:", tf.get_value())

print("\nTesting product_manager.survey...")
from product_manager.survey import TextField as PMTextField, enable_accessibility_mode, ACCESSIBILITY_MODE

# Test accessibility mode
print("Initial accessibility mode:", ACCESSIBILITY_MODE)
enable_accessibility_mode()
print("After enabling:", ACCESSIBILITY_MODE)

# Test TextField
tf = PMTextField(length_limit=5, placeholder="enter")
print("Created PMTextField:", tf)
ok, err = tf.validate("too")
print("Validation result (valid):", ok, err)
ok, err = tf.validate("toolong")
print("Validation result (invalid):", ok, err)

print("\nAll tests completed!")