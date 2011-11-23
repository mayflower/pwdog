import os
import os.path

class FilesystemStore(object):
    def __init__(self, cache_path):
        self.cache_path = cache_path

    def __str__(self):
        return 'Cache(%s)' % self.cache_path

    def set(self, name, type, content):
        path = os.path.join(self.cache_path, name)
        try:
            os.makedirs(path)
        except:
            pass # meh

        file(os.path.join(path, type), 'w').write(content)

    def get(self, name=None, type=None):
        path = self.cache_path
        if name is not None:
            path = os.path.join(path, name)

        try:
            if type is None:
                return os.listdir(path)

            return file(os.path.join(path, type), 'r').read()
        except (OSError, IOError):
            return None

    def delete(self, name, type):
        os.unlink(os.path.join(self.cache_path, path, type))
