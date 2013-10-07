import logging
import re

from xail import XAIL
from HAL.context import default as default_context
from HAL.middlewares import SpamFilter, WikiWare
from HAL.version import version as HALversion
from HAL.middlewares.wikipedia import set_agent

try:
    from itertools import imap as map
except ImportError:
    pass

logger = logging.getLogger('HAL')
DEBUG_MODE = False


class HAL(object):
    version = HALversion

    def __init__(self):
        self.middleware = [WikiWare(), SpamFilter()]
        self.globals = default_context.copy()
        self.xail = XAIL()

    def feed(self, *args, **kwargs):
        return self.xail.feed(*args, **kwargs)

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
            if response:  # Sanity checks here
                question = response

        response = self.xail.final(question)
        
        try:
            response = self._subst(response, context=context)
        except ValueError as e:
            logger.error('Fail to substitute: %s in string %s', e, response)

        for middleware in reversed(self.middleware):
            result = middleware.output(response)
            if result:  # Prevent a bad middleware from eating everything
                response = result
        
        if response.startswith('>'):
            # Only exists for compatibility with old files
            # Will be removed when the main db is cleaned up
            return self.answer(response[1:], context, recurse+1)
        return response
