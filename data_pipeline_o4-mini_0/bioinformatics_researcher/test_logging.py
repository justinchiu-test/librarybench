from pipeline.logging import RealTimeLogger
import json

def test_real_time_logger():
    logger = RealTimeLogger()
    logger.log({'event': 'start'})
    logs = logger.get_logs()
    assert len(logs) == 1
    entry = json.loads(logs[0])
    assert entry['event'] == 'start'
