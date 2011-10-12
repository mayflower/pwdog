import os

class Cache():
    def __init__(self, cache_path):
        self.cache_path = cache_path

    def __str__(self):
        return 'Cache(%s)' % self.cache_path

    def write(self, name, type, content):
        try:
            try:
                os.makedirs('%s/%s' % (self.cache_path, name))
            except:
                pass # meh
            
            file('%s/%s/%s' % (self.cache_path, name, type), 'w').write(content)
            return True
        except:
            raise

    def read(self, name, type):
        try:
            content = file('%s/%s/%s' % (self.cache_path, name, type), 'r').read()
            return content
        except OSError:
            print "cache read fail"
            raise OSError