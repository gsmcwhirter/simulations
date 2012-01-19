""" A port of the node.js EventEmitter functionality

Classes:
    EventEmitter

"""

import collections
import sys

class EventEmitter(object):
    """ Handles event emitting and listening
    
    Public Methods:
        addListener -- add a listener for an event
        on -- alias for addListener
        emit -- trigger the listeners for an event
        removeListener -- remove a listener from an event
        removeAllListeners -- remove all listeners from an event
        listeners -- get a copy of the listeners on an event
        setMaxListeners -- set the maximum number of listeners for an event before warnings are issued (default: 10, None for no limit)
    
    """
    
    def __init__(self):
        """ Initialize the EventEmitter
        
        """
        
        self._map = collections.defaultdict(list)
        self._maxListeners = 10
        
    def setMaxListeners(self, maxListeners):
        """ Set the maximum number of listeners for each event.
        
        Parameters:
            maxListeners -- the maximum number of listeners allowed (None for no limit)
        
        """
        
        self._maxListeners = maxListeners
        
        return self

    def addListener(self, event, f=None):
        """ Adds a listener to an event
        
        Parameters:
            event -- the event to listen for
            f -- the handler for the event (should be a function / callable)
        
        """
        
        if f is not None:
            listeners = len(self._map[event])
            if self._maxListeners is not None and listeners >= self._maxListeners: 
                print >>sys.stderr, "WARNING: Possible EventEmitter memory leak: {0} listeners added for {1}. Use setMaxListeners to increase the limit.".format(listeners + 1, event)
                
            self._map[event].append(f)
        
        return self
        
    def on(self, *args):
        """ Alias for addListener
        
        """
        
        return self.addListener(*args)
    
    def once(self, event, f=None):
        """ Add a listener, but only execute it the first time the event occurs, then remove it
        
        Parameters:
            event -- the event to listen for
            f -- the listener function / callable
        
        """
        
        def handler(*args, **kwargs):
            f(*args, **kwargs)
            self.removeListener(event, handler)
            
        return self.addListener(event, handler)
        
    def removeListener(self, event, f=None):
        """ Remove a listener from an event
        
        Parameters:
            event -- the event from which to remove it
            f -- the handler to remove
        
        """
        
        try:
            self._map[event].remove(f)
        except ValueError:
            pass
    
        return self
    
    def removeAllListeners(self, event):
        """ Clears all listeners from an event
        
        Parameters:
            event -- the event to clear listeners from
        
        
        """
        self._map[event] = []
        
        return self
    
    def listeners(self, event):
        """ Gets a COPY of the list of listeners on an event
        
        Parameters:
            event -- the event for which to lookup the listeners
        
        """
        return self._map[event][:]

    def emit(self, event, *args, **kwargs):
        """ Emit an event, triggering the handlers on it with certain arguments
        
        Parameters:
            event -- the event to trigger
            *args -- arguments to pass to the triggered listeners
            **kwargs -- keyword arguments to pass to the triggered listeners
        
        """
        
        for subscriber in self._map[event][:]:
            subscriber(*args, **kwargs)
            
        return self
