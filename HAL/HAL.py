from collections import namedtuple, Sequence
import logging

from engine import *

ENGINES = ('regex', 'general', 'matrix', 'oneword', 'generic')
class HALengineList(namedtuple('HALengineList', ENGINES)):
    'Order subjected to change for iterations purposes without notice, use attributes and keywords'
    pass

class HALengineInit(namedtuple('HALengineInit', ENGINES)):
    def __new__(_cls, regex=None, general=None, matrix=None, oneword=None, generic=None):
        'Create new instance of HALengineInit(regex, general, matrix, oneword, generic)'
        return tuple.__new__(_cls, (regex, general, matrix, oneword, generic))

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
        self.postengine = []
    
    def answer(self, question, context=None):
        engines = list(self.prengine)
        engines.extend(self.engines)
        engines.extend(self.postengine)
        for engine in engines:
            res = engine.final(question)
            if res is not None:
                break
        return res
