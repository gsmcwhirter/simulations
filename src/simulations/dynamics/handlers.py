""" Provides default handlers for various events

Functions:
    
    initial_set_handler
      Default handler for 'initial set' events
    
    generation_report_handler
      Default handler for 'generation' events

"""

def initial_set_handler(this, initial_pop):
    """ Handles the 'initial set' event by default for discrete replicator dynamics
    
    Parameters:
        
        this
          a reference to the simulation
          
        initial_pop
          the initial population
    
    """
    
    print >> this.out, "Initial State: {0}".format(initial_pop)
    print >> this.out
    
def generation_report_handler(this, generation_count, this_generation, last_generation):
    """ Print out a report of the current generation
    
    Parameters:
        
        this
          a reference to the simulation
          
        generation_count
          the generation number
        
        this_generation
          the current population
        
        last_generation
          the previous population
    
    """
    
    print >> this.out, "-" * 72
    print >> this.out, "Generation {0}:".format(generation_count)
    print >> this.out, "\t{0}".format(this_generation)
    print >> this.out
    this.out.flush()
    
