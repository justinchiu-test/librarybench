"""
Publish data scientist pipeline as tar.gz.
"""
import os
import tarfile

def publish_package(path):
    # create tar.gz of the given project directory
    base = os.path.basename(path.rstrip(os.sep))
    tar_path = path.rstrip(os.sep) + '.tar.gz'
    with tarfile.open(tar_path, 'w:gz') as tar:
        tar.add(path, arcname=base)
    return tar_path