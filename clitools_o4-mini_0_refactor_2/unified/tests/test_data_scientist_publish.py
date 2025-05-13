import os
import tempfile
import tarfile
from data_scientist.datapipeline_cli.publish import publish_package

def test_publish_package(tmp_path):
    proj = tmp_path / 'proj'
    proj.mkdir()
    # add dummy file
    f = proj / 'file.txt'
    f.write_text('data')
    tar_path = publish_package(str(proj))
    assert os.path.isfile(tar_path)
    # verify tar contains proj/file.txt
    with tarfile.open(tar_path, 'r:gz') as tar:
        names = tar.getnames()
    assert any('proj/file.txt' in n for n in names)
