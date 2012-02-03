""" A port of the node.js EventEmitter functionality

Classes:

    EventEmitter
      implements the event emitter functionality

Functions:

    listener
      A class decorator for adding listeners

    once
      A class decorator for adding once-only listeners

"""

import collections
import sys


class EventEmitter(object):
    """ Handles event emitting and listening

    Public Methods:

        add_listener
          add a listener for an event

        on
          alias for add_listener

        once
          adds a listener, but only executes it once, then it is removed

        emit
          trigger the listeners for an event

        remove_listener
          remove a listener from an event

        remove_all_listeners
          remove all listeners from an event

        listeners
          get a copy of the listeners on an event

        set_max_listeners
          set the maximum number of listeners for an event before warnings are
          issued (default: 10, None for no limit)

    """

    max_errstr = """"
    WARNING: Possible EventEmitter memory leak:
    {0} listeners added for {1}. Use set_max_listeners to increase the limit.
    """

    def __init__(self):
        """ Initialize the EventEmitter

        """

        self._map = collections.defaultdict(list)
        self._max_listeners = 10

    def set_max_listeners(self, max_listeners):
        """ Set the maximum number of listeners for each event.

        Parameters:

            max_listeners
              the maximum number of listeners allowed (None for no limit)

        """

        self._max_listeners = max_listeners

        return self

    def add_listener(self, event, listener=None):
        """ Adds a listener to an event

        Parameters:

            event
              the event to listen for

            listener
              the handler for the event (should be a function / callable)

        """

        if listener is not None:
            listeners = len(self._map[event])
            if self._max_listeners is not None\
                and listeners >= self._max_listeners:
                print >> sys.stderr, self.max_errstr.format(listeners + 1,
                                                            event)

            self._map[event].append(listener)

        return self

    def on(self, *args):
        """ Alias for add_listener

        """

        return self.add_listener(*args)

    def once(self, event, listener=None):
        """ Add a listener, but only execute it the first time the event
            occurs, then remove it

        Parameters:

            event
              the event to listen for

            listener
              the listener function / callable

        """

        def handler(*args, **kwargs):
            """ Runs the listener and then remove it from the list

            """

            listener(*args, **kwargs)
            self.remove_listener(event, handler)

        return self.add_listener(event, handler)

    def remove_listener(self, event, listener=None):
        """ Remove a listener from an event

        Parameters:

            event
              the event from which to remove it

            listener
              the handler to remove

        """

        try:
            self._map[event].remove(listener)
        except ValueError:
            pass

        return self

    def remove_all_listeners(self, event):
        """ Clears all listeners from an event

        Parameters:

            event
              the event to clear listeners from

        """

        self._map[event] = []

        return self

    def listeners(self, event):
        """ Gets a COPY of the list of listeners on an event

        Parameters:

            event
              the event for which to lookup the listeners

        """

        return self._map[event][:]

    def emit(self, event, *args, **kwargs):
        """ Emit an event, triggering the handlers on it with certain arguments

        Parameters:

            event
              the event to trigger

            args
              arguments to pass to the triggered listeners

            kwargs
              keyword arguments to pass to the triggered listeners

        """

        for subscriber in self._map[event][:]:
            subscriber(*args, **kwargs)

        return self
