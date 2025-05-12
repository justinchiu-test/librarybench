import sys
from pipeline.cli import main
from pipeline.metrics import metrics_manager, increment_counter

def test_cli_batch(monkeypatch, capsys):
    metrics_manager.reset()
    monkeypatch.setattr(sys, 'argv', ['prog', 'batch', '--input', 'a', 'b'])
    main()
    captured = capsys.readouterr()
    assert "Processing a" in captured.out
    assert "{'processed': 2" in captured.out

def test_cli_metrics(monkeypatch, capsys):
    metrics_manager.reset()
    increment_counter('x', 'processed', 4)
    monkeypatch.setattr(sys, 'argv', ['prog', 'metrics'])
    main()
    captured = capsys.readouterr()
    assert 'pipeline_processed_total{stage="x"} 4' in captured.out
