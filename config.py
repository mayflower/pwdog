import ConfigParser

class Config(object):
    def __init__(self, filename, context):
        self.context = context
        self.parser = ConfigParser.SafeConfigParser()
        self.parser.read(filename)

    def get(self, key):
        try:
            return self.parser.get(self.context, key)
        except ConfigParser.NoOptionError:
            return None
