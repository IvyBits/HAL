from abc import ABCMeta, abstractmethod, abstractproperty

class BaseEngine(object):
    """Template of an engine"""
    
    __metaclass__ = ABCMeta
    @abstractmethod
    def __init__(self, file=None):
        """May construct from file if needed, file should be string,
           or None if default is desired"""
        pass
    
    @abstractproperty
    def loaded_from_file(self):
        return False
    
    @abstractmethod
    def close(self):
        """dumps the current internal data structure back to the file"""
        pass
    
    @abstractmethod
    def __del__(self):
        self.close()
    
    @abstractmethod
    def load(self, file):
        """loads file as a string or a file like object into the engine"""
        pass
    
    @abstractmethod
    def output(self, input, context=None):
        """Given input, return output in a list of
        tuple(output:str, priority:float(range(1)))"""
        pass
    
    @abstractmethod
    def final(self, input, context=None):
        """Selects the highest ranked output from `output()`
        
        Implementation is allowed to randomly select from
        equally ranked outputs"""
        try:
            return self.output[0]
        except IndexError:
            return
