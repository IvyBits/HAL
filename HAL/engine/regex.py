import re
import sys
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from difflib import SequenceMatcher
from threading import Lock
from contextlib import closing

from pysqlite2 import dbapi2 as sqlite3

from HAL.string import strip_clean, normalize, rewhite
renotword = re.compile(r'\W+')
# Inherit from Abstract Base Class if possible
try:
    from HAL.engine.base import BaseEngine
except ImportError:
    BaseEngine = object

class RegexEngine(BaseEngine):
    def __init__(self, file=':memory:'):
        self.db = sqlite3.connect(file, check_same_thread=False)
        # int id => regex
        self.regex = {}
        try:
            self.db.execute('SELECT * FROM halindex LIMIT 1')
        except sqlite3.OperationalError:
            self.db.execute('CREATE VIRTUAL TABLE halindex USING fts4(data)')
            self.db.execute('''CREATE TABLE IF NOT EXISTS haldata (
                                   regex TEXT UNIQUE, resp TEXT)''')
        self.db_lock = Lock()
        self._gen_regex()

    def _gen_regex(self):
        with self.db_lock:
            sql = 'SELECT rowid, regex FROM haldata'
            for id, pattern in self.db.execute(sql):
                self.regex[id] = re.compile(pattern, re.I)
    
    def close(self):
        self.db.close()
    
    def __del__(self):
        self.close()
    
    def load(self, file):
        if isinstance(file, basestring):
            file = closing(StringIO(file))
        resp = []
        last = ''
        with self.db_lock, self.db, file as file:
            c = self.db.cursor()
            def add_entry(last, resp):
                try:
                    regex = re.compile(last, re.I)
                except re.error:
                    print >>sys.stderr, 'Error on:', last
                except OverflowError:
                    print >>sys.stderr, 'Overflow on:', last
                else:
                    try:
                        c.execute('INSERT INTO haldata (resp, regex) VALUES (?, ?)', ('\f'.join(resp), last))
                    except sqlite3.IntegrityError:
                        rowid, resp_ = c.execute('SELECT rowid, resp FROM haldata WHERE regex = ?', (last,)).fetchall()[0]
                        resp = resp_ + '\f' + '\f'.join(resp)
                        c.execute('UPDATE haldata SET resp = ? WHERE rowid = ?', (resp, rowid))
                    else:
                        rowid = c.lastrowid
                        index = renotword.sub(' ', last)
                        c.execute('INSERT INTO halindex(docid, data) VALUES (?, ?)', (rowid, index))
                        self.regex[rowid] = regex
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
        text = ' OR '.join(strip_clean(text).split())
        with self.db_lock:
            c = self.db.execute('''SELECT data.rowid, data.resp
                                   FROM haldata data, halindex idx
                                   WHERE idx.data MATCH ?
                                   AND data.rowid == idx.docid''', (text,))
            return c.fetchall()
    
    def search(self, input):
        input = rewhite.sub(' ', strip_clean(input))
        out = []
        regexes = []
        diff_ = SequenceMatcher(lambda x: x in '?,./<>`~!@#$%&*()_+-={}[];:\'"|\\', input)
        def diff(text):
            diff_.set_seq2(text)
            return diff_.ratio()
        for id, resp in self._search_db(input):
            regexes.append((self.regex[id], resp.split('\f')))

        for regex, resp in regexes:
            match = regex.search(input)
            if match is not None:
                # Strip all backreference groups off
                if match.lastindex is not None:
                    base = StringIO()
                    last = match.start()
                    for i in xrange(1, match.lastindex+1):
                        base.write(input[last:match.start(i)])
                        last = match.end(i)
                    base.write(input[last:match.end()])
                    priority = diff(base.getvalue())
                else:
                    priority = diff(match.group(0))
                
                g0 = match.group(0)
                def expand(resp):
                    return match.expand(resp.replace(r'\0', g0).replace('\g<0>', g0))
                
                resp = map(expand, resp) # expand \1, \g<1>, \g<name>
                out.append((match, resp, priority))
        
        out.sort(key=lambda x: x[2], reverse=True)
        return out
    
    def output(self, input):
        out = []
        for match, resps, diff in self.search(input):
            for resp in resps:
                out.append((resp, diff))
    
    def final(self, input):
        return random.choice(self.search(input)[0][2])

if __name__ == '__main__':
    from pprint import pprint
    from glob import glob
    import time
    engine = RegexEngine()
    engine.load("""\
#JON SKEET IS (GOOD|SMART|INTELLIGENT)
Of course Jon Skeet is \g<1>, and very \1.

#WHAT I JUST SAID
\0.

#JON SKEET IS (?:SMART|INTELLIGENT)
Of course Jon Skeet is smart, because you said \g<0>.

#(.*) POINTS TO NULL
\g<1> can't point to null!!!

#JON SKEET POINTS TO NULL
Yes, Jon Skeet can point to null, and null will quake in fear.

#SEARCH (.*) ON GOOGLE
I will.

#SEARCH GURU ON GOOGLE
Did you mean Jon Skeet?

#(?:IS JON SKEET SMART|JON SKEET IS SMART|JON SKEET IS PRO|JON SKEET IS A GURU|JON SKEET)
Jon Skeet is obviously smart.
""")
    while True:
        try:
            input = unicode(raw_input('>>> '), 'mbcs', 'ignore')
        except (KeyboardInterrupt, EOFError):
            raise SystemExit
        if input == 'exit':
            raise SystemExit
        for match, resps, diff in engine.search(input):
            print 'Index:'
            print '   ', match.re.pattern
            print '   ', match.group(0)
            print '   ', match.groups()
            print 'Diff:', diff
            print 'Responses:'
            for resp in resps:
                print '  -', resp
            print
