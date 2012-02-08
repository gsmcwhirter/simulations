""" Handles basic functionality shared by a number of other modules

Classes:

    :py:class:`Base`
      Handles basic __init__ and listener patterns shared among several classes

Decorators:

    :py:func:`listener`
      A class decorator adding a listener without disrupting :py:meth:`~Base._add_listeners`

    :py:func:`once`
      A class decorator adding a once-only listener without disrupting
      :py:meth:`~Base._add_listeners`

    :py:func:`withoptions`
      A class decorator adding basic :py:class:`~simulations.utils.optionparser.OptionParser`
      functionality

"""

from simulations.utils.eventemitter import EventEmitter
from simulations.utils.optionparser import OptionParser


class Base(EventEmitter):
    """ The base class that handles common functionality from which other
        :py:class:`~simulations.utils.eventemitter.EventEmitter` classes are derived

        Keyword Parameters:

            default_handlers
              If true or not present, adds the default handlers defined in :py:meth:`Base._add_default_listeners`

    """

    def __init__(self, *args, **kwdargs):
        """ Handles the initialization process

        Keyword Parameters:

            default_handlers
              If true or not present, adds the default handlers defined in :py:meth:`Base._add_default_listeners`

        """

        super(Base, self).__init__()

        self.options = None
        self.args = None
        self.oparser = None

        if 'default_handlers' not in kwdargs or kwdargs['default_handlers']:
            self._add_default_listeners()

        self._add_listeners()

    def _add_default_listeners(self):
        """ Sets up default listeners for various events (should implement)

        """

        pass

    def _add_listeners(self):
        """ Set up listeners for various events (should implement)

        """

        pass


def withoptions(klass):
    """ A class wrapper that handles using an :py:class:`~simulations.utils.optionparser.OptionParser`

    Adds Keyword Parameters:

        option_error_handler
          An error handler for the :py:class:`~simulations.optionparser.OptionParser`

        option_exit_handler
          An exit handler for the :py:class:`~simulations.optionparser.OptionParser`

    Adds Events:

        oparser set up
          emitted after the :py:class:`~simulations.utils.optionparser.OptionParser`
          is set up and able to add options

    """

    old_init = klass.__init__

    def newinit(self, *args, **kwdargs):
        """ Wraps the old __init__ method and adds functionality for option
            parsing

        """

        old_init(self, *args, **kwdargs)

        self.options = None
        self.args = None

        self.oparser = OptionParser()

        if 'option_error_handler' in kwdargs:
            self.oparser.set_error_handler(kwdargs['option_error_handler'])

        if 'option_exit_handler' in kwdargs:
            self.oparser.set_exit_handler(kwdargs['option_exit_handler'])

        self._set_base_options()
        self.emit('oparser set up', self)

    klass.__init__ = newinit

    return klass


def listener(event, handler):
    """ Class decorator to add listeners in a brief way

    This is effectively the same as adding a call to
    :py:meth:`~simulations.utils.eventemitter.EventEmitter.add_listener` in
    :py:meth:`~Base._add_listeners`.

    Parameters:

        event
          the name of the event to listen for

        handler
          the event handler

    """

    def wrapper(klass):
        """ Wraps _add_listeners on klass, adding a new listener for an event

        """

        old_add_listeners = klass._add_listeners

        def _add_listeners(self):
            """ Sets up listeners for various events

            """

            old_add_listeners(self)
            self.add_listener(event, handler)

        klass._add_listeners = _add_listeners

        return klass

    return wrapper


def once(event, handler):
    """ Class decorator to handler once-listeners in a brief way.

    This is effectively the same as adding a call to
    :py:meth:`~simulations.utils.eventemitter.EventEmitter.once` in
    :py:meth:`~Base._add_listeners`.

    Parameters:

        event
          the name of the event to listen for

        handler
          the event handler

    """

    def wrapper(klass):
        """ Wraps _add_listeners on klass, adding a new once-only listener for an event.

        """

        old_add_listeners = klass._add_listeners

        def _add_listeners(self):
            """ Sets up listeners for various events

            """

            old_add_listeners(self)
            self.once(event, handler)

        klass._add_listeners = _add_listeners

        return klass

    return wrapper
