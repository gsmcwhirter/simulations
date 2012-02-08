""" Provides utility functions for the framework

Functions:

    :py:func:`random_string`
      generates a random string of characters

"""

import random


def random_string(size=6, chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """ Generates a random string of characters

    Parameters:

        size
          the length of the string (default 6)

        chars
            the list of characters to use in the generation

    """

    return ''.join(random.choice(chars) for x in range(size))
