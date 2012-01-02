import pwdog.store as store
import os

def test_filesystem_store():
    path = 'tests/credentials'
    s = store.FilesystemStore(path)

    data = [('foo', 'bar', 'omgwtf'), ('fu', 'baz', '')]

    for d in data:
        s.set(*d)
        assert s.get(*d[:2]) == d[2]

        s.delete(*d[:2])
        assert s.get(*d[:2]) is None

        assert d[0] not in os.listdir(path)
