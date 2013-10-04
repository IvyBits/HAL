from contextlib import closing
from io import StringIO
import logging
import random
import re
from operator import itemgetter

from HAL.engine import *
from HAL.context import default as default_context
from HAL.middlewares import SpamFilter, WikiWare
from HAL.version import version as HALversion

try:
    from itertools import imap as map
except ImportError:
    pass

logger = logging.getLogger('HAL')
DEBUG_MODE = False


class ComboEngine(object):
    """Engine to merge outputs of others"""
    
    def __init__(self, *args):
        self.engines = args

    def output(self, input):
        out = []
        for engine in self.engines:
            o = engine.output(input)
            if o is not None:
                out.extend(o)
        out.sort(key=itemgetter(1), reverse=True)
        return out

    def final(self, input):
        data = self.output(input)
        if not data:
            return None
        if DEBUG_MODE:
            for content, probility in data:
                print '%.6f: %s' % (probility, content)
        kazi = max(map(itemgetter(1), data))
        data = [x for x in data if x[1] == kazi]
        return random.choice(data)[0]


class HAL(object):
    version = HALversion
    def __init__(self):
        self.regex   = RegexEngine()
        self.general = GeneralEngine()
        self.matrix  = MatrixEngine()
        self.generic = GenericEngine()
        self.enginemap = {'#': self.matrix.add_entry,
                          '@': self.general.add_entry,
                          '!': self.regex.add_entry}
        
        self.middleware = [WikiWare(), SpamFilter()]
        self.globals = default_context.copy()

    def feed(self, file):
        if isinstance(file, basestring):
            file = closing(StringIO(file))
        engine_map = self.enginemap
        engine_chars = tuple(engine_map.keys())
        resp = []
        last = ''
        add_entry = None
        multiline = False
        add_resp = resp.append

        with file as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                elif line[0] == ';':
                    continue
                elif line.startswith(engine_chars):
                    if resp and add_entry is not None:
                        add_entry(last, resp)
                        del resp[:]
                    last = line[1:].strip()
                    add_entry = engine_map[line[0]]
                else:
                    if not line[-1] == '\\':
                        new_multiline = False
                    else:
                        stripped = line.rstrip('\\')
                        count = len(line) - len(stripped)
                        new_multiline = count & 1
                        line = stripped + '\\' * (count // 2)
                    if multiline:
                        resp[-1] += line
                    else:
                        add_resp(line)
                    multiline = new_multiline
            if resp and add_entry is not None:
                add_entry(last, resp)

    remacro = re.compile(r'{([^{}]+)}')
    refunc  = re.compile(r'(.*?)\((.*?)\)')
    
    def _subst(self, input, context=None):
        if context is None:
            context = {}
        remacro = self.remacro
        refunc = self.refunc
        
        def get(key):
            try:
                return context[key]
            except KeyError:
                return self.globals[key]
        
        while True:
            m = remacro.search(input)
            if m is None:
                break
            action = m.group(1)
            saveto = None
            if action.count('=') > 1:
                raise ValueError('Too many equal signs')
            if '=' in action:
                saveto, action = action.split('=')
            if '(' in action:
                try:
                    name, arg = refunc.match(action).groups()
                except AttributeError:
                    raise ValueError('Invalid function call syntax')
                args = [x.strip() for x in arg.split(',')]
                try:
                    func = get(name)
                except KeyError:
                    raise ValueError('Function not found')
                try:
                    out = func(*args)
                except Exception as e:
                    raise ValueError('Function {0} returned: {1}'.format(name, e))
            else:
                try:
                    data = get(action)
                except KeyError:
                    raise ValueError('Key "{0}" not found'.format(action))
                out = str(data()) if callable(data) else str(data)
            if saveto is None:
                input = '%s%s%s' % (input[:m.start()], out, input[m.end():])
            else:
                context[saveto] = out
                input = input[:m.start()] + input[m.end():]
        return input
    
    def answer(self, question, context=None, recurse=0):
        if recurse > 3:
            return 'Recursion Error'
        
        for middleware in self.middleware:
            response = middleware.input(question)
            if response:
                return response
            response = middleware.filter(question)
            if response: # Sanity checks here
                question = response
        
        combo = ComboEngine(self.regex, self.general, self.matrix, self.generic)
        response = combo.final(question)
        
        try:
            response = self._subst(response, context=context)
        except ValueError as e:
            logger.error('Fail to substitute: %s in string %s', e, response)

        for middleware in reversed(self.middleware):
            result = middleware.output(response)
            if result: # Prevent a bad middleware from eating everything
                response = result
        
        if response.startswith('>'):
            # Only exists for compatibility with old files
            # Will be removed when the main db is cleaned up
            return self.answer(response[1:], context, recurse+1)
        return response
