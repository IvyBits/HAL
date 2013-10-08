from abc import ABCMeta


class Middleware(object):
    __metaclass__ = ABCMeta

    def input(self, input):
        """Return something true and it's the response"""
        return None
    
    def filter(self, input):
        """Called after input, allows modification of the input"""
        return input
    
    def output(self, result):
        """Post process the result"""
        return result

    def get_macros(self):
        return {}
