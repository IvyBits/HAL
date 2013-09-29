import string
import itertools

from HAL.stringutils import strip_clean

alpha = set(string.ascii_letters)
alpha.add(' ')
junkword = {'the', 'of', 'to', 'and', 'a', 'in', 'is', 'it', 'you',
            'that', 'he', 'was', 'for', 'on', 'are', 'with', 'as',
            'I', 'his', 'they', 'be', 'at', 'one', 'have', 'this',
            'from', 'or', 'had', 'by', 'hot', 'but', 'some', 'what',
            'there', 'we', 'can', 'out', 'other', 'were', 'all',
            'your', 'when', 'up', 'use', 'how', 'said', 'an', 'each',
            'she', 'which', 'do', 'their', 'time', 'if', 'will',
            'way', 'about', 'many', 'then', 'them', 'would', 'so',
            'these', 'her'}

def tokens(text):
    """Returns text as a list of words(tokens) in lowercase"""
    return strip_clean(text.lower(), alpha).split()

def filterjunk(words, junk=None, filter=filter):
    """Filter words that are listed as junk, either in the global variable or
    the junk argument"""
    if junk is None:
        junk = junkword
    return filter(lambda x: x not in junk, words)

def ifilterjunk(*args, **kwargs):
    return filterjunk(*args, filter=itertools.ifilter, **kwargs)

def keywords(text):
    return set(ifilterjunk(set(tokens(text))))

if __name__ == '__main__':
    while True:
        print keywords(raw_input('>>> '))
