from pipeline.source_sink import SourceHook, SinkHook

def test_source_sink_hooks():
    def importer(ctx):
        return [1, 2, 3]
    def exporter(data, ctx):
        return sum(data)
    sh = SourceHook(importer)
    sk = SinkHook(exporter)
    data = sh.import_data({})
    assert data == [1, 2, 3]
    out = sk.export_data(data, {})
    assert out == 6
