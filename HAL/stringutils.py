import os
import re
from itertools import ifilter
from operator import contains
from functools import partial

__all__ = ['rewhite', 'strip_clean', 'normalize']

_encoding = 'mbcs' if os.name == 'nt' else 'utf-8'
rewhite = re.compile(r'\s+')


def strip_clean(text, allow=frozenset('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz +\'')):
    return ''.join(ifilter(partial(contains, allow), text))


def normalize(text):
    if type(text) is not unicode:
        text = unicode(text, _encoding, 'ignore')
    return text
