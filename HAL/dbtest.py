"""Detects various sqlite configurations,
   meant to be imported interactively"""

try:
    from pysqlite2 import dbapi2 as sqlite3
except ImportError:
    import sqlite3
    print 'Using the bundled sqlite module'
else:
    print 'Using the separate pysqlite2 package'

db = sqlite3.connect(':memory:')

try:
    db.execute('CREATE VIRTUAL TABLE test USING fts4(data)')
except sqlite3.OperationalError as e:
    if 'no such module' not in e.args[0]:
        raise
    # try fts3 instead
    try:
        db.execute('CREATE VIRTUAL TABLE test USING fts3(data)')
    except sqlite3.OperationalError as e:
        if 'no such module' in e.args[0]:
            print 'No fts, performance penalty expected'
        else:
            raise
    else:
        print 'fts3 is still ok'
else:
    print 'Nice, you have fts4'
