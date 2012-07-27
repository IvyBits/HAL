from collections import namedtuple, Sequence
import logging

from engine import *
from context import Context
import spam
import random

ENGINES = ('regex', 'general', 'matrix', 'oneword', 'generic')
class HALengineList(namedtuple('HALengineList', ENGINES)):
    'Order subjected to change for iterations purposes without notice, use attributes and keywords'
    pass

class HALengineInit(namedtuple('HALengineInit', ENGINES)):
    def __new__(_cls, regex=None, general=None, matrix=None, oneword=None, generic=None):
        'Create new instance of HALengineInit(regex, general, matrix, oneword, generic)'
        return tuple.__new__(_cls, (regex, general, matrix, oneword, generic))

class SpamEngine:
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
    def final(self, input):
        if spam.check(input):
            return random.choice(self.resp)

class ComboEngine:
    """Engine to merge outputs of others"""
    def __init__(self, *args):
        self.engines = args
    def output(self, input):
        out = []
        for engine in self.engines:
            o = engine.output(input)
            if o is not None:
                out.extend(o)
        out.sort(key=lambda x: x[1], reverse=True)
        return out
    def final(self, input):
        data = self.output(input)
        if not data:
            return None
        kazi = max(a[1] for a in data)
        data = filter(lambda x: x[1] == kazi, data)
        return random.choice(data)[0]

class HAL(object):
    version = 'git'
    def __init__(self, init=HALengineInit(), load=HALengineInit()):
        logger = logging.getLogger('HAL')
        # Initialize Engines
        if not isinstance(init, HALengineInit):
            init = HALengineInit(*init)
        if not isinstance(load, HALengineInit):
            load = HALengineInit(*load)
        self.engines = HALengineList(regex=  RegexEngine(init.regex),
                                     general=GeneralEngine(init.general),
                                     matrix= MatrixEngine(init.matrix),
                                     oneword=OneWordEngine(init.oneword),
                                     generic=GenericEngine(init.generic))
        def load_data(toload, load, engine):
            if isinstance(toload, basestring):
                try:
                    load(open(toload))
                except IOError:
                    load(toload)
                    logger.info('%s engine: Loaded string into', engine)
                else:
                    logger.info('%s engine: Loading file %s',
                                engine, toload)
            elif isinstance(toload, Sequence):
                for elem in toload:
                    load_data(elem, load, engine)
            elif isinstance(toload, file):
                load(file)
                logger.info('%s engine: Loading file object %s into',
                            engine, toload)
        
        for engine in ENGINES:
            if getattr(load, engine) is not None:
                toload = getattr(load, engine)
                load_data(toload, getattr(self.engines, engine).load, engine)
        
        self.prengine = []
        self.postengine = [SpamEngine()]
        self._context = Context(self)
    
    def context(self):
        return self._context.fork()
    
    def answer(self, question, context=None, recurse=0):
        if recurse > 3:
            return 'Recursion Error'
        if context is None:
            context = self._context
        engines = list(self.prengine)
        engines.append(ComboEngine(*self.engines[:3]))
        engines.append(self.engines.oneword)
        engines.extend(self.postengine)
        engines.append(self.engines.generic)
        for engine in engines:
            res = engine.final(question)
            if res is not None:
                break
        try:
            res = context.subst(res)
        except ValueError as e:
            logging.getLogger('HAL').error('Fail to substitute: '
                                           '%s in string %s',
                                           e.args[0], res)
        if res.startswith('>'):
            # Only exists for compatibility with old files
            # Will be removed when the main db is cleaned up
            return self.answer(res[1:], context, recurse+1)
        return res
