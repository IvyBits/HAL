import os, re

__all__ = ['rewhite', 'strip_clean', 'normalize']

_encoding = 'mbcs' if os.name == 'nt' else 'utf-8'
rewhite = re.compile(r'\s+')

def strip_clean(text, allow='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz +'):
    out = []
    for c in text:
        if c in allow:
            out.append(c)
    return ''.join(out)

def normalize(text):
    if type(text) is not unicode:
        text = unicode(text, _encoding, 'ignore')
    return text
