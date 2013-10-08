"""Date and time Middleware, called date so I can use datetime"""

from HAL.middleware import Middleware
import time


class DateTimeWare(Middleware):
    def date_macro(self):
        return time.strftime('%A, %B %d, %Y')

    def time_macro(self):
        return time.strftime('%H:%M:%S')

    def datetime_macro(self):
        return time.strftime('%H:%M:%S on %A, %B %d, %Y')

    def get_macros(self):
        return {'date': self.date_macro, 'time': self.time_macro, 'datetime': self.datetime_macro}