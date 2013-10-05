import re
from xail.stringutils import strip_clean
from functools import partial
from operator import contains

vowels = 'aeiouy'
consonants = 'bcdfghjklmnpqrstvwxz'
proper_letters = 'abcdefghijklmnopqrstuvwxyz '
rerepeat = re.compile(r'(.)\1\1')
rerepeatl = re.compile(r'\b(..+)\s*\1\b')

long_exception = ('pneumonoultramicroscopicsilicovolcanoconiosis',
                  'supercalifragilisticexpialidocious',
                  'pseudopseudohypoparathyroidism',
                  'floccinaucinihilipilification',
                  'antidisestablishmentarianism',
                  'honorificabilitudinitatibus',
                  'hippopotomontrosesquipedaliophobia')
impossibles = 'df bf kf gf jk kj sj fj gj hj lj sl'.split()
digraphs = {'th': 't', 'ng': 'n', 'sh': 's', 'ch': 'c', 'dj': 'j',
            'sch': 's', 'tsch': 'c'} # some common digraphs
acronyms = '''adsl bc bcc blt bmp btw cc cc ccd cd cdfs cdn cdr cdrw cms cpc cpl cpm
              cps crm crt css cst ctp ctr dbms ddl ddr ddr ddr dfs dhcp dlc dll dns
              drm dsl dslam dst dtd dv dvd dvdr dvdram dvdrw dvr fdr fm fsb ftp gbps gps
              hdd hdtv hdv hfs hsf html http https ieee jfk jfs jsf jsp jv kbps kvm lcd
              lcd mbps mbr mc mlk mms mp ms mst mtd mtg nntp ntfs pbj pc pc pcb pcmcia
              pdf php pm png pp ppc ppl ppm ppp pppoe pps pptp ps ps rdf rgb rpc rpm rss
              rtf sd sdk sdsl sla sli smb smm sms smtp snmp sql srgb ssd ssh ssl tft ttl
              vdsl vlb vpn vrml wc wddm www xhtml xml xmp xslt'''.split()

class SpamCheck(object):
    def __init__(self, text):
        self.text = text
        self.lower = text.lower()
        self.words = strip_clean(self.lower, proper_letters).split()
        self.error = 0
        self.reasons = set()

    def acronyms(self):
        for word in self.words[:]:
            if word in acronyms:
                self.text = re.sub(re.escape(word), '', self.text, flags=re.I)
                self.words.remove(word)
        self.lower = self.text.lower()

    def length_check(self):
        """\
        Length check: No sane sentence will use many long words.
        The longest common word is probably internationalization, or i18n,
        which has 20 letters. Just in case, exceptions are checked.
        """
        for word in self.words:
            if len(word) > 20 and word not in long_exception:
                self.reasons.add('too long')
                self.error += 1
            count = len(filter(partial(contains, vowels), word))
            if not count:
                self.reasons.add('has no vowel')
                self.error += 1

    def consonant_cluster(self):
        """\
        In English, no more than 3 written consonants (where digraphs count as one)
        ever occur together. However, in some dialects, schwas were dropped, and
        consonants become syllabic. This however doesn't occur in spelling.
        """
        consonant = 0
        text = self.lower
        for digraph, replacement in digraphs.iteritems():
            text = text.replace(digraph, replacement)
        for letter in text:
            if letter in consonants:
                consonant += 1
            else:
                consonant = 0
            if consonant > 3:
                self.reasons.add('more than 3 consonants appear in a row')
                self.error += 1

    def digraph_check(self):
        """\
        In English, many digraphs never occur. However, they frequently occur when
        spamming the keyboard, especially the QWERTY.
        """
        errors = len([None for digraph in impossibles if digraph in self.text])
        if errors:
            self.reasons.add('invalid digraphs detected')
            self.error += errors

    def repetition(self):
        count = len(rerepeat.findall(self.lower))
        if count:
            self.reasons.add('too many repeated letters')
            self.error += count
        count = len(rerepeatl.findall(self.lower))
        if count:
            self.reasons.add('too many repeated words')
            self.error += count

    def check(self):
        self.acronyms()
        self.length_check()
        self.consonant_cluster()
        self.digraph_check()
        self.repetition()
        return self.error > len(self.words) / 3

if __name__ == '__main__':
    while True:
        input = raw_input('>>> ')
        status = SpamCheck(input)
        if status.check():
            print input, 'is spam:'
            for reason in status.reasons:
                print ' - ', reason
        else:
            print input, 'is not spam'
