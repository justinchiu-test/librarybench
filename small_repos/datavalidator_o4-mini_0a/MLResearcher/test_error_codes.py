from error_codes import ErrorCodeSupport

def test_assign_error_codes():
    ecs = ErrorCodeSupport()
    errors = [{'field':'a','type':'missing'},
              {'field':'b','type':'outlier'},
              {'field':'c','type':'length'},
              {'field':'d','type':'unknown'}]
    codes = ecs.assign_error_codes(errors)
    assert codes == ['MISSING_FEATURE','OUTLIER_DETECTED','INVALID_LENGTH','INVALID_VALUE']
