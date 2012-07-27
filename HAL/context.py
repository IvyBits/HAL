import re
import random
import datetime

__all__ = ['Context']

age = random.randint(18, 30)
default = dict(
    BIRTHDAY='July 1, '+str(datetime.date.today().year-age),
    BIRTHPLACE='Toronto, Canada', BOTMASTER='owner',
    CONTRIBUTOR='xiaomao', LOCATION='Toronto, Ontario',
    FAVORITEACTOR='undefined', FAVORITEACTRESS='undefined',
    FAVORITEARTIST='Larry Wall', FAVORITEBAND='undefined',
    FAVORITEBOOK='2001: A Space Odyssey', AGE=age,
    FAVORITECOLOR='blue', FAVORITEMOVIE='2001: A Space Odyssey',
    FAVORITESONG='cat /dev/urandom | aplay', NAME='HAL',
    FAVORITESPORT='hacking', GENDER='male', 
    GIRLFRIEND='None', MASTER='xiaomao', RELIGION='atheist',
    GENUS='robot', SPECIES='chatterbot', TALKABOUT='programming',
    USERNAME='(WARNING: USERNAME IS NOT SET!)',
    WEBSITE='http://www.halbot.co.cc/',
)
remacro = re.compile(r'{[^{}]+}')
refunc  = re.compile(r'(.*?)\((.*?)\)')

class Context(dict):
    __slots__ = ('engine', 'data')
    def __init__(self, engine, base=None, **kwargs):
        self.engine = engine
        dict.__init__(self, default)
        if base is not None:
            self.update(base)
        self.update(kwargs)
        self.data = {}
    
    def fork(self):
        return Context(self.engine, self)

    def subst(self, input):
        while True:
            m = remacro.search(input)
            if m is None:
                break
            action = m.group(0).strip('{}')
            saveto = None
            out = None
            if action.count('=') > 1:
                raise ValueError('Too many equal signs')
            if '=' in action:
                saveto, action = action.split('=')
            if '(' in action:
                # function calling
                try:
                    name, arg = refunc.match(action).groups()
                except AttributeError:
                    raise ValueError('Invalid function call syntax')
                args = [x.strip() for x in arg.split(',')]
                try:
                    func = self[name]
                except KeyError:
                    raise ValueError('Function not found')
                try:
                    out = func(*args)
                except Exception as e:
                    raise ValueError('Function {0} returned: {1}'.format(name, e))
            else:
                try:
                    data = self[action]
                except KeyError:
                    raise ValueError('Key "{0}" not found'.format(action))
                try:
                    out = data()
                except:
                    out = str(data)
            if saveto is None:
                # out is what we want to substitute
                input = input[:m.start()] + out + input[m.end():]
            else:
                self[saveto] = out
                input = input[:m.start()] + input[m.end():]
        return input
    
    def answer(self, ques):
        self.engine.answer(ques, self)
