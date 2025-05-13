"""
Publish package for data_scientist datapipeline CLI.
Creates a gzipped tar of the project directory.
"""
import os
import tarfile

def publish_package(path):
    base = os.path.basename(path.rstrip(os.sep))
    out = f"{base}.tar.gz"
    with tarfile.open(out, 'w:gz') as tf:
        tf.add(path, arcname=base)
    return out