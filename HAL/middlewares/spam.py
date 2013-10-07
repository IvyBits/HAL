import random
from HAL import spamchecker
from HAL.middleware import Middleware
from HAL.middlewares.wikipedia import requestion

__author__ = 'xiaomao'


class SpamFilter(Middleware):
    resp = ['Please stop spamming me.',
            'Why are you spamming me?',
            'What was that?',
            'Do you enjoy spam?',
            'Stop spamming please.',
            'Are you spamming me?',
            'Can you please speak normally?',
            'What language is that?',
            "I don't understand spam.",
            'Seems like you have nothing good to say.']

    def input(self, input):
        if spamchecker.SpamCheck(input).check():
            if requestion.search(input) is None:
                return random.choice(self.resp)
