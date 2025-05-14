import pickle

def snapshot(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)

def restore(path):
    with open(path, 'rb') as f:
        return pickle.load(f)
