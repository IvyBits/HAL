import re
import os.path
from string import strip_clean

vowels = 'aeiouy'
consonants = 'bcdfghjklmnpqrstvwxz'
proper_letters = 'abcdefghijklmnopqrstuvwxyz '
rerepeat = re.compile(r'(.)\1\1')
rerepeatl = re.compile(r'(..+)\s*\1')

long_exception = ('pneumonoultramicroscopicsilicovolcanoconiosis',
                  'supercalifragilisticexpialidocious',
                  'pseudopseudohypoparathyroidism',
                  'floccinaucinihilipilification',
                  'antidisestablishmentarianism',
                  'honorificabilitudinitatibus',
                  'hippopotomontrosesquipedaliophobia')
impossibles = 'df bf kf gf jk kj sj fj gj hj lj sl'.split()

def check(text):
    """"""
    # Strip to leave only words
    letters = []
    words = strip_clean(text.lower(), proper_letters).split()

    # See if each word has a vowel, also checks length
    for word in words:
        # If word longer than 20 and not in exception list, it's spam
        if len(word) > 20 and word not in long_exception:
            return 'too long'
        count = 0
        for vowel in vowels:
            if vowel in word:
                count += 1
        if not count:
            return 'has no vowel'
    
    # Only 3 consonant can appear in a row
    consonant = 0
    for letter in text.replace('th', 't'):
        if letter in consonants:
            consonant += 1
        else:
            consonant = 0
        if consonant > 3:
            return 'more than 3 consonants appear in a row'
    
    # Inavid Sequences
    for seq in impossibles:
        if seq in text:
            return 'invalid sequences detected'
    
    # Repitition
    for regex in (rerepeat, rerepeatl):
        if regex.search(text):
            return 'too many repeated letters'
    
    # Passed all test, not a spam
    return False

if __name__ == '__main__':
    while True:
        input = raw_input('>>> ')
        status = check(input)
        if status:
            print input, 'is spam:', status
        else:
            print input, 'is not spam'
