import os
import ujson

class Config:

    def __init__(self, filename):
        self.filename = filename
        self.values = {}
        self.load()

    def get(self, name):
        if name in self.values:
            return self.values[name]
        return ''

    def set(self, name, value):
        self.values[name] = value

    def store(self):
        f = open(self.filename, 'w')
        f.write(ujson.dump(self.values))
        f.close()

    def load(self):
        if not self.filename in os.listdir():
            print('cannot find ' + self.filename)
            return
        f = open(self.filename)
        self.values = ujson.load(f)
        f.close()
