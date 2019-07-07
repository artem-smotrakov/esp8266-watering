import os
import ujson

# this class holds a configuration for the device
# the configuraion is stored to a file
class Config:

    # loads a configuraion from the specified file,
    # and initializes an instance of Config
    def __init__(self, filename):
        self.filename = filename
        self.values = {}
        self.load()

    # returns a value of the specified parameter if the parameter exists
    # otherwise, returns an empty string
    def get(self, name):
        if name in self.values:
            return self.values[name]
        return ''

    # updates the specified parameter
    def set(self, name, value):
        self.values[name] = value

    # stores the configuraion to the specified file
    def store(self):
        f = open(self.filename, 'w')
        f.write(ujson.dumps(self.values))
        f.close()

    # loads a configration from the specified file
    def load(self):
        if not self.filename in os.listdir():
            print('cannot find ' + self.filename)
            return
        f = open(self.filename)
        self.values = ujson.load(f)
        f.close()
