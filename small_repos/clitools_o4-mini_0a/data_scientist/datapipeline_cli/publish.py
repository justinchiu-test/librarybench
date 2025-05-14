import os
import tarfile

def publish_package(path):
    if not os.path.isdir(path):
        raise ValueError('Path must be a directory')
    dist = os.path.join(path, 'dist')
    os.makedirs(dist, exist_ok=True)
    name = os.path.basename(os.path.abspath(path))
    tar_path = os.path.join(dist, f'{name}.tar.gz')
    with tarfile.open(tar_path, 'w:gz') as tar:
        tar.add(path, arcname=name)
    return tar_path
