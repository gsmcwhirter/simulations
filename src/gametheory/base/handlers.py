""" Provides default handlers for various events

Functions:
    simulation_batch_default_pool_started_handler
    simulation_batch_default_start_handler
    simulation_batch_default_result_handler

"""

import sys

def simbatch_default_result_handler(this, result, out=None):
    """ Default handler for the 'result' event
    
    Parameters:
        result -- the result object
    
    """
    
    if out is None:
        out = sys.stdout
    
    this.finished_count += 1
    if not this.options.quiet:
        print >> out, result
        print >> out, "done #{0}".format(this.finished_count)
        
def simbatch_default_pool_handler(this, pool, out=None):
    """ Default handler for the 'pool started' event
    
    Parameters:
        pool -- the pool that was started
    
    """
    
    if out is None:
        out = sys.stdout
    
    if not this.options.quiet:
        print >> out, "Pool Started: {0} workers".format(pool.get_ncpus())
        
def simbatch_default_start_handler(this, out=None):
    """ Default handler for the 'start' event
    
    """
    
    if out is None:
        out = sys.stdout
    
    if not this.options.quiet:
        print >> out, "Running {0} duplications.".format(this.options.dup)

def drep_initial_set_handler(this, initial_pop):
    """ Handles the 'initial set' event by default for discrete replicator dynamics
    
    """
    
    print >> this.out, "Initial State: {0}".format(initial_pop)
    print >> this.out
    
def drep_generation_report_handler(this, generation_count, this_generation, last_generation):
    """ Print out a report of the current generation
    
    Parameters:
        generation_count -- the generation number
        this_generation -- the current population
        last_generation -- the previous population
    
    """
    
    print >> this.out, "-" * 72
    print >> this.out, "Generation {0}:".format(generation_count)
    print >> this.out, "\t{0}".format(this_generation)
    print >> this.out
    this.out.flush()
    
def drep_stable_state_handler(this, generation_count, this_generation, last_generation, initial_pop):    
    """ Print out a report when a stable state is reached.
    
    Parameters:
        generation_count -- the number of generations
        this_generation -- the stable state population
        last_generation -- the previous population
        initial_pop -- the initial population
    
    """
    
    print >> this.out, "=" * 72
    print >> this.out, "Stable state! ({0} generations)".format(generation_count)
    print >> this.out, "\t{0}".format(this_generation)
    for i, pop in enumerate(this_generation):
        if abs(pop - 0.) > this.effective_zero:
            print >> this.out, "\t\t{0}: {1}".format(i, pop)
    print >> this.out
    
def drep_npop_stable_state_handler(this, generation_count, this_generation, last_generation, initial_pop):    
    """ Print out a report when a stable state is reached.
    
    Parameters:
        generation_count -- the number of generations
        this_generation -- the stable state population
        last_generation -- the previous population
        initial_pop -- the initial population
    
    """
    print >> this.out, "=" * 72
    print >> this.out, "Stable state! ({0} generations)".format(generation_count)
    for k in xrange(len(this_generation)):
        print >> this.out, "\tPopulation {0}:".format(k)
        print >> this.out, "\t{0}".format(this_generation[k])
        for i, pop in enumerate(this_generation[k]):
            if abs(pop - 0.) > this.effective_zero:
                print >> this.out, "\t\t{0}: {1}".format(i, pop)
    print >> this.out
    
