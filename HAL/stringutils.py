import os, re

__all__ = ['rewhite', 'strip_clean', 'normalize']

_encoding = 'mbcs' if os.name == 'nt' else 'utf-8'
rewhite = re.compile(r'\s+')


def strip_clean(text, allow=set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz +')):
    return ''.join(c for c in text if c in allow)


def normalize(text):
    if type(text) is not unicode:
        text = unicode(text, _encoding, 'ignore')
    return text
