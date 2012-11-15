from difflib import SequenceMatcher
from HAL.string import strip_clean
from HAL.lang.keywords import keywords

try:
    from HAL.engine.general import GeneralEngine
except ImportError:
    # Try to find GeneralEngine when ran as a script
    from general import GeneralEngine

class MatrixEngine(GeneralEngine):
    def __init__(self, *args):
        GeneralEngine.__init__(self, *args)
        self.state = set()
    
    """Matrix Engine: exactly same as GeneralEngine,
       except order and position doesn't matter"""
    def search(self, input):
        """Returns tuple(index:str, resp:list, priority:float)
        
        Note that this method doesn't conform the ABC, you should only use
        it for debugging purpose or you are ONLY using this engine"""
        data = {}
        for index, resp in self._search_db(input):
            key = frozenset(index.split())
            resp = resp.split('\f')
            if key in data:
                data[key].extend(resp)
            else:
                data[key] = resp
        diff = SequenceMatcher(lambda x: x in '?,./<>`~!@#$%&*()_+-={}[];:\'"|\\', input + ' '.join(self.state))
        cleaned = strip_clean(input.lower())
        cleaned_words = cleaned.split()
        words = self.state.union(cleaned_words)
        #print words
        def matches(entry):
            for key in entry[0]:
                if not any(x.startswith(key) for x in words):
                    return False
            return True
        def getdiff(text):
            diff.set_seq2(text)
            return diff.ratio()
        def sortset(text):
            return cleaned.find(text)
        data = filter(matches, data.iteritems())
        data = [(index, resp, getdiff(' '.join(sorted(index, key=sortset))))
                for index, resp in data]
        data.sort(key=lambda x: x[2], reverse=True)
        self.state = keywords(input)
        return data

if __name__ == '__main__':
    from pprint import pprint
    from glob import glob
    engine = MatrixEngine()
    engine.load("""\
#This file is based on Jon Skeet facts

#HELLO WORLD
Said Hello to World.

#FIRST JON SKEET
Jon Skeet's first words are "Let there be light" apparently.

#NAME ANONYMOUS METHOD
Anonymous methods and anonymous types are really all called Jon Skeet. They just don't like to boast.

#JON SKEET CODING CONVENTION
Jon Skeet's code doesn't follow a coding convention. It is the coding convention.

#BOTTLENECK PERFORMANCE
Jon Skeet doesn't have performance bottlenecks. He just makes the universe wait its turn.

#ACCEPT JON SKEET
Users don't mark Jon Skeet's answers as accepted. The universe accepts them out of a sense of truth and justice.

#DIVIDE ZERO
Jon Skeet and only Jon Skeet can divide by zero.

#JON SKEET FAIL COMPILE
When Jon Skeet's code fails to compile the compiler apologises.

#JON SKEET NULL
When Jon Skeet points to null, null quakes in fear.
""")
    while True:
        input = unicode(raw_input('>>> '), 'mbcs', 'ignore')
        for index, resps, diff in engine.search(input):
            print 'Index:', index
            print 'Diff:', diff
            print 'Responses:'
            for resp in resps:
                print '  - ', resp
            print
