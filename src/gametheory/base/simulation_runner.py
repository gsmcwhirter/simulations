""" Handler for running simulations in a multiprocessing environment

Functions:
    run_simulation -- runs a simulation task

"""

def run_simulation(task):
    """ A simple function to run the simulation. Used with the multiprocessing pool.
    
    Parameters:
        task -- a list/tuple whose first element is a Simulation class and the rest
                    of whose elements are parameters for __init__
        
    """
    
    klass = task.pop(0)
    sim = klass(*task)
    
    return sim.run()
