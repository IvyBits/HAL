import re
import random
import shelve
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from contextlib import closing

from stemming.porter2 import stem

# Inherit from Abstract Base Class if possible
try:
    from HAL.engine.base import BaseEngine
except ImportError:
    BaseEngine = object
from HAL.string import strip_clean, normalize, rewhite

rewb = re.compile(r'\W+')

class OneWordEngine(BaseEngine):
    """Fall back engine that checks every word in the sentence,
       once without modification, and once stemmed"""
    def __init__(self, file=None):
        if file is None:
            self.data = {}
        else:
            self.data = shelve.open(file)
        self.dbfile = file
        self._loaded_from_file = bool(self.data)
    
    @property
    def loaded_from_file(self):
        return self._loaded_from_file

    def __del__(self):
        self.close()
    
    def close(self):
        if self.dbfile is not None:
            self.data.close()
    
    def load(self, file):
        if isinstance(file, basestring):
            file = closing(StringIO(file))
        resp = []
        last = ''
        def add_entry(last, resp):
            name = strip_clean(last).lower().encode('utf-8')
            if name in self.data:
                # Require to workaround the shelve case
                tmp = self.data[name]
                tmp.extend(resp)
                self.data[name] = tmp
            else:
                self.data[name] = resp
        with file as file:
            for line in file:
                line = normalize(line.strip())
                if not line:
                    continue
                if line[0] == '#':
                    if resp:
                        add_entry(last, resp)
                    resp = []
                    last = line[1:]
                else:
                    resp.append(line)
            if resp:
                add_entry(last, resp)
    
    def search(self, input):
        words = set(rewb.split(input.encode('utf-8')))
        words.update(map(stem, words))
        out = []
        for word in words:
            try:
                out.append((word, self.data[word]))
            except KeyError:
                pass
        return out
    
    def output(self, input, context=None):
        return [(out, 0.001) for word, out in self.search(input)]
    
    def final(self, input, context=None):
        try:
            return random.choice(self.search(input))[1]
        except IndexError:
            return

if __name__ == '__main__':
    from pprint import pprint
    from glob import glob
    engine = OneWordEngine()
    engine.load("""\
#GURU
Did you mean Jon Skeet?

#NULL
When Jon Skeet points to null, null quakes in fear.

#ROOT
Jon Skeet has root access to your system.

#badge
Jon Skeet has more "Nice Answer" badges than you have badges.

#lizard
"Bill the Lizard" you mean?

#REPUTATION
Jon Skeet's SO reputation is only as modest as it is because of integer overflow (SQL Server does not have a datatype large enough)

#immutable
Jon Skeet is immutable. If something's going to change, it's going to have to be the rest of the universe.

#accept
Users don't mark Jon Skeet's answers as accepted. The universe accepts them out of a sense of truth and justice.

#bottleneck
Jon Skeet doesn't have performance bottlenecks. He just makes the universe wait its turn.

#Skeet
Jon Skeet!
""")
    while True:
        input = unicode(raw_input('>>> '), 'mbcs', 'ignore')
        for word, resps in engine.search(input):
            print 'Index:', word
            print 'Responses:'
            for resp in resps:
                print '  - ', resp
            print
