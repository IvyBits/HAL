import os
import re
import random
from difflib import SequenceMatcher
from threading import Lock
from contextlib import closing

from pysqlite2 import dbapi2 as sqlite3
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from HAL.string import strip_clean, normalize, rewhite
# Inherit from Abstract Base Class if possible
try:
    from HAL.engine.base import BaseEngine
except ImportError:
    BaseEngine = object

class GeneralEngine(BaseEngine):
    """The substring engine, respond with all entries that is a substring of the input"""
    def __init__(self, file=':memory:'):
        self.db = sqlite3.connect(file, check_same_thread=False)
        try:
            self.db.execute('SELECT * FROM halindex LIMIT 1')
            self.db.execute('SELECT * FROM haldata LIMIT 1')
        except sqlite3.OperationalError:
            self.db.execute('CREATE VIRTUAL TABLE halindex USING fts4(data)')
            self.db.execute('''CREATE TABLE IF NOT EXISTS haldata (
                                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                                   data TEXT UNIQUE, resp TEXT)''')
        self.db_lock = Lock()

    def close(self):
        self.db.close()
    
    def __del__(self):
        self.close()

    def load(self, file):
        if isinstance(file, basestring):
            file = closing(StringIO(file)) # StringIO doesn't support context management protocol
        resp = []
        last = ''
        with self.db_lock, file as file, self.db:
            c = self.db.cursor()
            def add_entry(last, resp):
                index = strip_clean(last).lower()
                try:
                    c.execute('INSERT INTO haldata (resp, data) VALUES (?, ?)', ('\f'.join(resp), index))
                except sqlite3.IntegrityError:
                    # Duplicate index
                    id, resp_ = c.execute('SELECT id, resp FROM haldata WHERE data = ?', (index,)).fetchall()[0]
                    resp = resp_ + '\f' + '\f'.join(resp)
                    c.execute('UPDATE haldata SET resp = ? WHERE id = ?', (resp, id))
                else:
                    c.execute('INSERT INTO halindex(docid, data) VALUES (?, ?)', (c.lastrowid, index))
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
    
    def _search_db(self, text):
        """Format: list of (index text, resp \f separated text)"""
        text = ' OR '.join(strip_clean(text).split())
        with self.db_lock:
            c = self.db.execute('''SELECT idx.data, data.resp
                                   FROM haldata data, halindex idx
                                   WHERE idx.data MATCH ?
                                   AND data.id == idx.docid''', (text,))
            return c.fetchall()

    def search(self, input):
        """Returns tuple(index:str, resp:list, priority:float)
        
        Note that this method doesn't conform the ABC, you should only use
        it for debugging purpose or you are ONLY using this engine"""
        data = self._search_db(input)
        diff = SequenceMatcher(lambda x: x in '?,./<>`~!@#$%&*()_+-={}[];:\'"|\\', input)
        cleaned = rewhite.sub(' ', strip_clean(input))
        def matches(entry):
            return entry[0] in cleaned
        def getdiff(text):
            diff.set_seq2(text)
            return diff.ratio()
        data = filter(matches, data)
        data = [(index, resp.split('\f'), getdiff(index)) for index, resp in data]
        data.sort(key=lambda x: x[2], reverse=True)
        return data
    
    def output(self, text):
        data = self.search(text)
        out = []
        for index, resps, priority in data:
            for resp in resps:
                out.append((resp, priority))
        return out
    
    def final(self, text):
        try:
            return random.choice(self.search(text)[0])
        except IndexError:
            # When there is no response
            return None

if __name__ == '__main__':
    from pprint import pprint
    from glob import glob
    engine = GeneralEngine()
    engine.load("""
#SIMPLE
It is simple.

#VERY SIMPLE
Indeed very simple.

#SIMPLE X
X is not simple.

#MORE SIMPLE
Invalid grammar: simpler!

#extremely simple
Too extreme.

#SIMPLE VERY
Please swap...
""")
    while True:
        input = normalize(raw_input('>>> '))
        for index, resps, diff in engine.search(input):
            print 'Index:', index
            print 'Diff:', diff
            print 'Responses:'
            for resp in resps:
                print '  - ', resp
            print
