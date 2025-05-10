import pytest
import hashlib
from unified.src.data_engineer.dataschema.secure_field_masking import SecureFieldMasking

def test_mask_and_hash():
    data = {'ssn':'123-45-6789', 'cc':'1111', 'name':'Joe'}
    sm = SecureFieldMasking(fields=['ssn','cc','name'], mask='MASK', hash_fields=['cc'])
    out = sm.mask_data(data)
    assert out['ssn'] == 'MASK'
    assert out['name'] == 'MASK'
    assert out['cc'] == hashlib.sha256('1111'.encode()).hexdigest()
    # fields not listed remain
    data2 = {'other':'x'}
    sm2 = SecureFieldMasking(fields=['none'])
    assert sm2.mask_data(data2) == {'other':'x'}
