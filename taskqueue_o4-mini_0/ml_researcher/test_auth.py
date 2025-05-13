from scheduler.auth import RoleBasedAccessControl

def test_role_based_access_control():
    rb = RoleBasedAccessControl()
    rb.add_role('admin', ['enqueue','cancel','status','reprioritize'])
    rb.add_role('user', ['enqueue','status'])
    rb.assign_role('alice', 'admin')
    rb.assign_role('bob', 'user')
    assert rb.check_permission('alice','cancel')
    assert not rb.check_permission('bob','cancel')
    assert rb.check_permission('bob','enqueue')
