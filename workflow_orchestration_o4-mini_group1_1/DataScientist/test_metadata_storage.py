import pytest
from DataScientist.pipeline.task import Task
from DataScientist.pipeline.pipeline import Pipeline
import datetime

class QuickTask(Task):
    def run(self, context):
        return 123

def test_metadata_records():
    p = Pipeline()
    p.add_task(QuickTask("qt"))
    start_count = len(p.metadata.records)
    ctx = p.run()
    end_count = len(p.metadata.records)
    assert end_count == start_count + 1
    rec = p.metadata.records[-1]
    assert rec['task_id'] == "qt"
    assert rec['status'] == 'success'
    assert isinstance(rec['start_time'], datetime.datetime)
    assert isinstance(rec['end_time'], datetime.datetime)
