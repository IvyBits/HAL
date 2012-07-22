try:
    from HAL.engine.base import BaseEngine
except ImportError:
    BaseEngine = object
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from contextlib import closing
import random

class GenericEngine(BaseEngine):
    """The generic engine that responds with
       one-size-fit-all-but-useless answers"""
    def __init__(self, file=None):
        self.data = {"I don't understand.",
                     "I can't seem to understand.",
                     'Wait, I got a phone call.',
                     'Oh, my keyboard hung again.',
                     'Sorry, my computer lagged.',
                     'Only Jon Skeet knows the answer to that one.'}
        if file:
            with open(file) as file:
                self.data.update(i.strip() for i in file)
        self.file = file
        self.data = list(self.data)
    
    def close(self):
        if self.file is not None:
            with open(file, 'w') as file:
                for entry in self.data:
                    print >>file, entry
    
    def __del__(self):
        self.close()

    def load(self, file):
        if isinstance(file, basestring):
            file = closing(StringIO(file))
        with file as file:
            for line in file:
                self.data.append(line.strip())
    
    def output(self, input):
        return map(lambda x: (x, 0.0), self.data)
    
    def final(self, input):
        return random.choice(self.data)

if __name__ == '__main__':
    from pprint import pprint
    engine = GenericEngine()
    pprint(engine.data)
    pprint(engine.output('x'))
    print engine.final('x')
