import pytest
from background_dispatcher import Dispatcher

def test_rbac_permissions():
    dsp = Dispatcher()
    dsp.set_role('admin_user', 'admin')
    dsp.set_role('normal_user', 'user')
    dsp.set_role('guest_user', 'guest')
    # admin can enqueue
    dsp.api_enqueue_image_task('admin_user', {})
    # user can enqueue
    dsp.api_enqueue_image_task('normal_user', {})
    # guest cannot enqueue
    with pytest.raises(PermissionError):
        dsp.api_enqueue_image_task('guest_user', {})

    # guest can query (of existing or non-existing)
    assert dsp.api_query_progress('guest_user', 999) is None
