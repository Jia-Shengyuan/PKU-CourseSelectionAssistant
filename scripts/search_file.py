import os

def search_by_suffix(path, suffix):
    files = os.listdir(path)
    result = []
    for f in files:
        if f.endswith(suffix):
            result.append(f)
    return result

def search_by_name(path, name):
    files = os.listdir(path)
    result = []
    for f in files:
        if f == name:
            result.append(f)
    return result