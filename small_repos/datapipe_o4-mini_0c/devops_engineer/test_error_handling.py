import logging
from pipeline.error_handling import skip_on_error

def test_skip_on_error_logs_and_skips(caplog):
    caplog.set_level(logging.ERROR)
    @skip_on_error
    def process(r):
        if r == 'bad':
            raise ValueError('bad record')
        return r.upper()
    assert process('good') == 'GOOD'
    assert process('bad') is None
    assert 'Error processing record bad: bad record' in caplog.text
