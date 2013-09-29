from collections import namedtuple, Sequence
import logging

from HAL.engine import *
from HAL.context import default as default_context
from HAL.middleware import Middleware
from HAL import spam
import random
import re

from operator import itemgetter
try:
    from itertools import imap as map
except ImportError:
    pass

logger = logging.getLogger('HAL')

class SpamFilter(Middleware):
    """Duck-typed engine for spam procesing"""
    resp = ['Please stop spamming me.',
            'Why are you spamming me?',
            'What was that?',
            'Do you enjoy spam?',
            'Stop spamming please.',
            'Are you spamming me?',
            'Can you please speak normally?',
            'What language is that?',
            "I don't understand spam.",
            'Seems like you have nothing good to say.']
    def input(self, input):
        if spam.check(input):
            return random.choice(self.resp)

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
        kazi = max(map(itemgetter(1), data))
        data = [x for x in data if x[1] == kazi]
        return random.choice(data)[0]

class HAL(object):
    version = 'git'
    def __init__(self):
        self.regex   = RegexEngine()
        self.general = GeneralEngine()
        self.matrix  = MatrixEngine()
        self.oneword = OneWordEngine()
        self.generic = GenericEngine()
        
        self.middleware = [SpamFilter()]
        self.globals = default_context.copy()
    
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
            out = None
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
        
        if context is None:
            context = self._context
        
        for middleware in self.middleware:
            response = middleware.input(question)
            if response:
                return response
            response = middleware.filter(question)
            if response: # Sanity checks here
                question = response
        
        combo = ComboEngine(self.regex, self.general, self.matrix, self.oneword, self.generic)
        response = combo.final(question)
        
        try:
            response = self._subst(response, context=context)
        except ValueError as e:
            logger.error('Fail to substitute: %s in string %s', e, response)
        
        if response.startswith('>'):
            # Only exists for compatibility with old files
            # Will be removed when the main db is cleaned up
            return self.answer(response[1:], context, recurse+1)
        return response
