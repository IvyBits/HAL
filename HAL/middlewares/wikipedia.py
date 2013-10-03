# encoding: utf-8
from HAL.middleware import Middleware
from HAL.utils import LimitedSizeDict
from HAL.version import version

from urllib import urlencode
from urllib2 import urlopen, Request
from contextlib import closing

from bs4 import BeautifulSoup
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
                            (?=\s|$)''', re.X|re.M)
rebracket = re.compile(r'\s*\([^()]*\)\s*')
respacepunc = re.compile(r'''\s+(?=[,.;:?!])''')
_superscript = u'⁰¹²³⁴⁵⁶⁷⁸⁹'
_normal = u'0123456789'
_subscript = u'₀₁₂₃₄₅₆₇₈₉'
headers = {'User-Agent': 'HAL/%s' % version}
blacklist = tuple('my your his our thy thine their'.split()) # these sound like smalltalk


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

    def remove(self, *args, **kwargs):
        for tag in self.soup.find_all(*args, **kwargs):
            tag.extract()

    def update(self, func, *args, **kwargs):
        for tag in self.soup.find_all(*args, **kwargs):
            if tag.string:
                tag.string = func(tag.string)

    def clean(self):
        self.remove('sup', class_='reference')
        self.remove('sup', class_='Template-Fact')
        self.update(superscript_int, 'sup')
        self.update(subscript_int, 'sub')
        self.remove('div')
        self.remove('dl')
        self.remove('table')
        self.remove('span', class_='editsection')
        self.remove('span', class_='mw-editsection')
        self.remove('span', class_=lambda x: x is not None and 'IPA' in x)
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
    query = dict(action='query', list='search', srsearch=keyword, srprop='wordcount', format='json')
    page = urlopen('%s?%s' % (api, urlencode(query)))
    with closing(page):
        results = json.load(page)
    for result in results['query']['search']:
        yield result['title'], result['wordcount']


def get_best_article(articles):
    """Gets the most suitable article. Most of the time the first one works.

    However, sometimes the first one is disambiguation, so if it's 10x shorter than
    the second or more, the second is returned."""
    if len(articles) == 0:
        return
    elif len(articles) == 1:
        return articles[0][0]
    else:
        if articles[0][1] * 10 < articles[1][1]:
            return articles[1][0]
        else:
            return articles[0][0]


def download_article(name, wiki='http://en.wikipedia.org/w/index.php'):
    query = dict(title=name, action='render')
    request = Request('%s?%s' % (wiki, urlencode(query)), headers=headers)
    page = urlopen(request)
    with closing(page):
        article = page.read()
    return article


def get_lead(article):
    parser = WikiParser(article)
    parser.parse()
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
        articles = list(find_article(keyword))
        article = get_best_article(articles)
        if article is None:
            cache[lower] = None
            return
        article = download_article(article)
        result = sentences(get_lead(article))
        match = result.lower()
        if not any(stem(word) in match for word in lower.split()):
            # none of the keyword was found in the result
            cache[lower] = None
            return
        cache[lower] = result
        return result


class WikiWare(Middleware):
    def __init__(self):
        self.cache = {}

    # Input handler was removed so better response cen be used by the engine
    # However, the [wiki:article] syntax can be used

    def output(self, result):
        return rewikisub.sub(lambda match: get_wikipedia(match.group(1)) or
                             "I don't know what that means.", result)

if __name__ == '__main__':
    try:
        while True:
            keyword = raw_input('--> ')
            articles = list(find_article(keyword))
            article = get_best_article(articles)
            print 'Chosen:', article
            article = download_article(article)
            print sentences(get_lead(article))
    except (KeyboardInterrupt, EOFError):
        pass