from __future__ import print_function
import codecs
from getpass import getuser
from glob import glob
import logging
import sys, os
import io

from HAL import HAL

# Windows doesn't have readline, but it's usefule on linux,
# as the console doesn't do editing like windows
try:
    import readline
except ImportError:
    pass

logger = logging.getLogger('HAL')

def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    # Using the correct encoding when printing
    sys.stdout = codecs.getwriter('mbcs' if os.name == 'nt' else 'utf-8')(sys.stdout, 'replace')
    
    try:
        dir = sys.argv[1]
    except IndexError:
        dir = '.'
    
    hal = HAL()
    def loadengine(pattern, name):
        engine = getattr(hal, name)
        for file in glob(os.path.join(dir, pattern)):
            logger.info('%s Engine: Loading %s', name, file)
            engine.load(io.open(file, encoding='utf-8'))
    loadengine('*.gen', 'general')
    loadengine('*.mtx', 'matrix')
    loadengine('*.rgx', 'regex')
    loadengine('*.ow',  'oneword')
    user = getuser()
    prompt = '-%s:' % user
    halpro = '-HAL:'
    length = max(len(prompt), len(halpro))
    prompt.ljust(length)
    halpro.ljust(length)
    prompt += ' '
    context = {'USERNAME': user}
    print(halpro, 'Hello %s. I am HAL %s.'%(user, hal.version))
    print()
    try:
        while True:
            line = raw_input(prompt)
            print(halpro, hal.answer(line, context))
            print()
    finally:
        print(halpro, 'Goodbye.')

if __name__ == '__main__':
    main()
