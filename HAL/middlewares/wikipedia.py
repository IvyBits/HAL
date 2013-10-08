# encoding: utf-8
from HAL.middleware import Middleware
from HAL.utils import LimitedSizeDict
from HAL.version import version

from urllib import urlencode
from urllib2 import urlopen, Request
from contextlib import closing

from bs4 import BeautifulSoup, Comment
from stemming.porter2 import stem

import re
import json

requestion = re.compile(r'''wh(?:o|ere|en|at|y)(?:['"](?:s|re)|\s+is|\s+are)\s+(?:(?:an?|the)\s+)?([a-zA-Z0-9 _'"]+)''', re.I)
rewikisub = re.compile(r'\[wiki:(.*?)\]')
#resentence = re.compile(r'.*?(?:[.?!](?=\s))|$', re.M)
resentence = re.compile(r'''# Match a sentence ending in punctuation or EOS.
                            [^.!?\s]    # First char is non-punct, non-ws
                            [^.!?]*      # Greedily consume up to punctuation.
                            (?<!.Mr|.Ms|Mrs)
                            (?:          # Group for unrolling the loop.
                              [.!?]      # (special) inner punctuation ok if
                              (?!['\"]?\s|$)  # not followed by ws or EOS.
                              [^.!?]*    # Greedily consume up to punctuation.
                            )*           # Zero or more (special normal*)
                            [.!?]?       # Optional ending punctuation.
                            ['"]?       # Optional closing quote.
                            (?=\s|$)''', re.X | re.M)
rebracket = re.compile(r'\s*\([^()]*\)\s*')
respacepunc = re.compile(r'''\s+(?=[,.;:?!])''')
redisambig = re.compile(r'may(?:\dalso)?\drefer')
_superscript = u'⁰¹²³⁴⁵⁶⁷⁸⁹'
_normal = u'0123456789'
_subscript = u'₀₁₂₃₄₅₆₇₈₉'
headers = {'User-Agent': 'HAL/%s' % version}


def set_agent(agent):
    headers['User-Agent'] = 'HAL/%s %s' % (version, agent)


def superscript_int(str):
    for sup, norm in zip(_superscript, _normal):
        str = str.replace(norm, sup)
    return str


def subscript_int(str):
    for sub, norm in zip(_subscript, _normal):
        str = str.replace(norm, sub)
    return str


class WikiParser(object):
    def __init__(self, text):
        self.soup = BeautifulSoup(text)
        self.disambiguation = self.soup.find('table', id='disambigbox') is not None

    def remove(self, *args, **kwargs):
        for tag in self.soup.find_all(*args, **kwargs):
            tag.extract()

    def update(self, func, *args, **kwargs):
        for tag in self.soup.find_all(*args, **kwargs):
            if tag.string:
                tag.string = func(tag.string)

    def clean(self):
        self.remove(text=lambda text: isinstance(text, Comment))
        self.remove('sup', class_='reference')
        self.remove('sup', class_='Template-Fact')
        self.update(superscript_int, 'sup')
        self.update(subscript_int, 'sub')
        self.remove('div')
        self.remove('dl')
        self.remove('table')
        self.remove('span', class_='editsection')
        self.remove('span', class_='mw-editsection')
        self.update(lambda x: '\f%s:' % x, 'span', class_='mw-headline')

    def split(self):
        self.sections = sections = []
        for section in self.soup.get_text().split('\f'):
            section = section.strip()
            if not section:
                continue
            sections.append(section)

    def parse(self):
        self.clean()
        self.split()


def find_article(keyword, api='http://en.wikipedia.org/w/api.php'):
    query = dict(action='query', list='search', srsearch=keyword, format='json', srprop='redirecttitle')
    page = urlopen('%s?%s' % (api, urlencode(query)))
    with closing(page):
        results = json.load(page)
    for result in results['query']['search']:
        redirect = result.get('redirecttitle', None)
        if redirect is not None:
            redirect = redirect['mTextform']
        yield result['title'], redirect


def download_article(name, wiki='http://en.wikipedia.org/w/index.php'):
    query = dict(title=name.encode('utf-8'), action='render')
    request = Request('%s?%s' % (wiki, urlencode(query)), headers=headers)
    page = urlopen(request)
    with closing(page):
        article = page.read()
    return article


def get_lead(parser):
    text = parser.sections[0]
    while True:
        newtext = rebracket.sub(' ', text)
        if newtext == text:
            break
        text = newtext
    text = respacepunc.sub('', text)
    return text


def sentences(text, count=2):
    return ' '.join(map(unicode.strip, resentence.findall(text)[:count]))


def get_wikipedia(keyword, cache=LimitedSizeDict(size_limit=4096)):
    lower = keyword.lower()
    try:
        return cache[lower]
    except KeyError:
        for article, redirect in find_article(keyword):
            article = download_article(article)
            parser = WikiParser(article)
            if parser.disambiguation:
                cache[article.lower()] = None
                continue
            parser.parse()
            result = sentences(get_lead(parser))
            match = result.lower()
            has_text = ((redirect is not None and lower in redirect.lower())
                        or any(stem(word) in match for word in lower.split()))
            if not has_text or redisambig.search(match) is not None:
                # none of the keyword was found in the result
                cache[article.lower()] = None
                continue
            cache[lower] = result
            cache[article.lower()] = result
            return result
        cache[lower] = None
        return


class WikiWare(Middleware):
    def __init__(self):
        self.cache = {}

    # Input handler was removed so better response cen be used by the engine
    # However, the [wiki:article] syntax can be used
    def wiki_macro(self, keyword):
        return get_wikipedia(keyword) or "I don't know what that means."

    def get_macros(self):
        return {'wiki': self.wiki_macro}

    def output(self, result):
        return rewikisub.sub(lambda match: get_wikipedia(match.group(1)) or
                             "I don't know what that means.", result)

if __name__ == '__main__':
    try:
        while True:
            keyword = raw_input('--> ')
            articles = list(find_article(keyword))
            print 'Chosen:', article
            article = download_article(article)
            print sentences(get_lead(article))
    except (KeyboardInterrupt, EOFError):
        pass