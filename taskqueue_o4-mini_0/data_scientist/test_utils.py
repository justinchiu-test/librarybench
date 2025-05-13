from ml_pipeline.utils import generate_unique_task_id

def test_unique_task_id():
    id1 = generate_unique_task_id()
    id2 = generate_unique_task_id()
    assert isinstance(id1, str)
    assert isinstance(id2, str)
    assert id1 != id2
