""" Provides default handlers for various events

Functions:
    
    simulation_batch_default_pool_started_handler
      Default handler for 'pool started' events
    
    simulation_batch_default_start_handler
      Default handler for 'start' events
      
    simulation_batch_default_result_handler
      Default handler for 'result' events

"""

import sys

def simbatch_default_result_handler(this, result, out=None):
    """ Default handler for the 'result' event
    
    Parameters:
        
        this
          a reference to the simulation batch
          
        result 
          the result object
          
        out
          the file descriptor to print to
    
    """
    
    if out is None:
        out = sys.stdout
    
    if not this.options.quiet:
        print >> out, result
        print >> out, "done #{0}".format(this.finished_count)
        
def simbatch_default_pool_handler(this, pool, out=None):
    """ Default handler for the 'pool started' event
    
    Parameters:
        
        this
          a reference to the simulation batch
          
        pool 
          the pool that was started
          
        out
          the file descriptor to print to
    
    """
    
    if out is None:
        out = sys.stdout
    
    if not this.options.quiet:
        print >> out, "Pool Started: {0} workers".format(pool.get_ncpus())
        
def simbatch_default_start_handler(this, out=None):
    """ Default handler for the 'start' event
    
    Parameters:
        
        this
          a reference to the simulation batch
          
        out
          the file descriptor to print to
    
    """
    
    if out is None:
        out = sys.stdout
    
    if not this.options.quiet:
        print >> out, "Running {0} duplications.".format(this.options.dup)
    
