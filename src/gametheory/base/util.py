""" Provides utility functions for the framework

Functions:
    
    random_string
      generates a random string of characters

"""

import random
import string

def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    """ Generates a random string of characters
    
    Parameters:
        
        size
          the length of the string (default 6)
          
        chars
            the list of characters to use in the generation
                    (default string.ascii_uppercase + string.digits)
    
    """
    
    return ''.join(random.choice(chars) for x in range(size))
