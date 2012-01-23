""" Provides default handlers for various events

Functions:
    
    drep_initial_set_handler
      Default handler for 'initial set' events
    
    drep_generation_report_handler
      Default handler for 'generation' events
    
    drep_stable_state_handler
      Default handler for 'stable state' and 'force stop' events in one population
    
    drep_npop_stable_state_handler
      Default handler for 'stable state' and 'force stop' events in n populations

"""

def drep_initial_set_handler(this, initial_pop):
    """ Handles the 'initial set' event by default for discrete replicator dynamics
    
    Parameters:
        
        this
          a reference to the simulation
          
        initial_pop
          the initial population
    
    """
    
    print >> this.out, "Initial State: {0}".format(initial_pop)
    print >> this.out
    
def drep_generation_report_handler(this, generation_count, this_generation, last_generation):
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
    
def drep_stable_state_handler(this, generation_count, this_generation, last_generation, initial_pop):    
    """ Print out a report when a stable state is reached.
    
    Parameters:
        
        this
          a reference to the simulation
          
        generation_count
          the number of generations
        
        this_generation
          the stable state population
        
        last_generation
          the previous population
        
        initial_pop
          the initial population
    
    """
    
    print >> this.out, "=" * 72
    if this.force_stop:
        print >> this.out, "Force stop! ({0} generations)".format(generation_count)
    else:
        print >> this.out, "Stable state! ({0} generations)".format(generation_count)
    print >> this.out, "\t{0}".format(this_generation)
    for i, pop in enumerate(this_generation):
        if abs(pop - 0.) > this.effective_zero:
            print >> this.out, "\t\t{0:>5}: {1:>20}: {2}".format(i, this.types[i], pop)
    print >> this.out
    
def drep_npop_stable_state_handler(this, generation_count, this_generation, last_generation, initial_pop):    
    """ Print out a report when a stable state is reached.
    
    Parameters:
        
        this
          a reference to the simulation
          
        generation_count
          the number of generations
        
        this_generation
          the stable state population
        
        last_generation
          the previous population
        
        initial_pop
          the initial population
    
    """
    print >> this.out, "=" * 72
    if this.force_stop:
        print >> this.out, "Force stop! ({0} generations)".format(generation_count)
    else:
        print >> this.out, "Stable state! ({0} generations)".format(generation_count)
    for k in xrange(len(this_generation)):
        print >> this.out, "\tPopulation {0}:".format(k)
        print >> this.out, "\t{0}".format(this_generation[k])
        for i, pop in enumerate(this_generation[k]):
            if abs(pop - 0.) > this.effective_zero:
                print >> this.out, "\t\t{0:>5}: {1:>20}: {2}".format(i, this.types[k][i], pop)
    print >> this.out
