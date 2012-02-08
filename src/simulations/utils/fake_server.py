""" Has a fake class that simulates the interface of pp.Server but is only single-threaded

Classes:

    :py:class:`Server`
      A fake :py:class:`pp.Server` class

"""

from pp import DestroyedServerError


class Server(object):
    """ A fake :py:class:`pp.Server` implementation -- just single-ordered.

    """

    default_port = 60000
    default_secret = 'epo20pdosl;dksldkmm'

    def __init__(self, ncpus='autodetect',
                       ppservers=(),
                       secret=None,
                       restart=False,
                       proto=2):
        """ Does essentially nothing

        """

        self._destroyed = False

    def destroy(self):
        """ Sets _destroyed flag

        """

        self._destroyed = True

    def get_active_nodes(self):
        """ Returns {'fake': 1}

        """

        return {'fake': 1}

    def get_ncpus(self):
        """ Returns 1

        """

        return 1

    def get_stats(self):
        """ Returns an empty dictionary

        """

        return {}

    def print_stats(self):
        """ Does nothing

        """

        pass

    def set_ncpus(self, ncpus='autodetect'):
        """ Does nothing

        """

        pass

    def wait(self, group=None):
        """ Does nothing

        """

        pass

    def submit(self, func, args, depfuncs=(),
                                 modules=(),
                                 callback=None,
                                 callbackargs=(),
                                 group='default',
                                 globls=None):
        """ Runs a task, calling any callback provided and returning a function
            that returns the results. (Emulates :py:class:`pp.Server`)

            NOTE: the depfuncs, modules, globals, and group parameters are
                  not used.

        """

        if self._destroyed:
            raise DestroyedServerError("Cannot submit jobs: server"\
                    " instance has been destroyed")

        result = func(*args)
        if callback is not None:
            callback(*(callbackargs + (result,)))

        def retfunc():
            return result

        return retfunc
