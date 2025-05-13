import tempfile
from watcher.hash_utils import hash_file

def test_md5_sha256(tmp_path):
    f = tmp_path / "data.bin"
    content = b"abcdef"
    f.write_bytes(content)
    md5 = hash_file(str(f), algorithm="md5")
    sha = hash_file(str(f), algorithm="sha256")
    assert md5 == "e80b5017098950fc58aad83c8c14978e"
    assert sha == "bef575f1f8ecbd9b8fa940c6e3c8417adb07e6af5c184ca7f47f2905f8a6c1ee"
