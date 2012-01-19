""" An extension of optparse.OptionParser that has custom error and exit handling

Classes:
    OptionParser -- the extension class

"""

import optparse

class OptionParser(optparse.OptionParser):
    """ Overrides the error() and exit() methods to allow prevention of auto-exit
        
    New Methods:
        set_error_handler -- sets an error handler instead of the default
        set_exit_handler -- sets an exit handler instead of the default
        
    """
    
    def __init__(self, *args, **kwdargs):
        optparse.OptionParser.__init__(self, *args, **kwdargs)
        
        self._errorhandler = None
        self._exithandler = None
    
    def set_error_handler(self, handler):
        """ Sets an error handling function
        
        Parameters:
            handler -- A function that takes an error message and does something with it.
        
        """
        
        self._errorhandler = handler
        
    def set_exit_handler(self, handler):
        """ Sets an exit handling function
        
        Parameters:
            handler -- A function that takes an exit code and error message and does something with it.
        
        """
        
        self._exithandler = handler
        
    def error(self, msg):
        """ Declares a user-defined error has occurred.
        
        Parameters:
            msg -- The error message string
            
        """
        
        if self._errorhandler is not None:
            return self._errorhandler(msg)
        else:
            return optparse.OptionParser.error(self, msg)    
            
            
    def exit(self, code=0, msg=None):
        """ Exits the parser/program (the default calls sys.exit). Often called by OptionParser.error().
        
        Parameters:
            code -- The exit code
            msg -- The error message
        
        """
        
        if self._exithandler is not None:
            return self._exithandler(code, msg)
        else:
            return optparse.OptionParser.exit(self, code, msg)    
            
