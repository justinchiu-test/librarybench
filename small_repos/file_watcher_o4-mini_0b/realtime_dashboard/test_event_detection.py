from filewatcher.event_detection import HighLevelEventDetection, HighLevelEventType

def test_detect():
    det = HighLevelEventDetection()
    for raw_type, evtype in [("created", HighLevelEventType.CREATE),
                              ("modified", HighLevelEventType.MODIFY),
                              ("deleted", HighLevelEventType.DELETE),
                              ("moved", HighLevelEventType.MOVE)]:
        raw = {'event_type': raw_type, 'src_path': '/a', 'dest_path': '/b'}
        out = det.detect(raw)
        assert out['type'] == evtype
        assert out['src_path'] == '/a'
        assert out['dest_path'] == '/b'
