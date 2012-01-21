""" Simulation classes that handle variations of discrete-time replicator dynamics

Classes:
    OnePopDiscreteReplicatorDynamics
    NPopDiscreteReplicatorDynamics

"""

import itertools
import math
import numpy.random as rand
import operator

from gametheory.base.handlers import drep_initial_set_handler
from gametheory.base.handlers import drep_generation_report_handler
from gametheory.base.handlers import drep_npop_stable_state_handler
from gametheory.base.handlers import drep_stable_state_handler
from gametheory.base.simulation import Simulation

class OnePopDiscreteReplicatorDynamics(Simulation):
    """ Implements an abstract discrete-time replicator dynamics
    
    Methods to Implement:
        _interaction -- Returns the payoff for an given set of types
        
    Values to Implement:
        types -- A list of names for the possible types (used to calculate dimensionality)
        interaction_arity -- The number of players in a given interaction (default 2)
        background_rate -- The natural rate of reproduction (parameter in the dynamics)
        
    Events:
        generation -- emitted when a generation is complete (self, generation_number, new_gen, old_gen)
        initial set -- emitted when the initial population is set up (self, initial_pop)
        stable state -- emitted when a stable state is reached (self, generation_count, final_pop, prev_pop, initial_pop)
    
    """
    
    effective_zero = 1e-10
    types = ['A','B']
    interaction_arity = 2
    background_rate = 0.
    
    def __init__(self, *args, **kwdargs):
        """ Checks for default_handlers kwdargs parameter and then delegates to the parent.
        
        """
        
        super(OnePopDiscreteReplicatorDynamics, self).__init__(*args, **kwdargs)
        
        self.result_data = None
        
        if 'default_handlers' not in kwdargs or kwdargs['default_handlers']:
            self.on('initial set', drep_initial_set_handler)
            self.on('generation', drep_generation_report_handler)
            self.on('stable state', drep_stable_state_handler)
    
    def _random_population(self):
        """ Generate a random population on the unit simplex of appropriate dimensionality
        
        """
        
        rand.seed()
        
        return tuple(rand.dirichlet([1] * len(self.types)))
    
    def _pop_equals(self, last, this):
        """ Determine if two populations are equal, accounting for floating point issues
        
        Parameters:
            last -- one of the populations
            this -- the other population
        
        """
        
        return not any(abs(i - j) > self.effective_zero for i, j in itertools.izip(last, this))
    
    def _step_generation(self, pop):
        """ Step one population to the next generation
        
        Parameters:
            pop -- The population to send to the next generation
        
        """
        # x_i(t+1) = (a + u(e^i, x(t)))*x_i(t) / (a + u(x(t), x(t)))
        # a is background (lifetime) birthrate
        
        num_types = len(self.types)
        
        payoffs = [
            math.fsum(
                math.fsum(
                    float(self._interaction(place, profile)) * float(reduce(operator.mul, [pop[profile[prplace]] for prplace in xrange(len(profile)) if prplace != place], 1.))
                    for profile in itertools.product(
                            *([xrange(num_types) for _ in xrange(place)] + [[typ]] + [xrange(num_types) for _ in xrange(place+1, self.interaction_arity)])
                    ))
                for place in xrange(self.interaction_arity)
            ) / float(self.interaction_arity)
            for typ in xrange(num_types)
        ]
        
        avg_payoff = math.fsum(payoffs[i] * float(pop[i]) for i in xrange(num_types))
        
        new_pop = [float(pop[i]) * ((float(self.background_rate) + float(payoffs[i])) / (float(self.background_rate) + avg_payoff)) for i in xrange(num_types)]
        
        return tuple(new_pop)
    
    def _run(self, initial_pop=None):
        """ Actually run the simulation
        
        Parameters:
            initial_pop -- (optional) initial population. Randomizes if not provided.
        
        """
        
        if initial_pop is None:
            initial_pop = self._random_population()
        
        this_generation = initial_pop
        
        self.emit('initial set', self, initial_pop)
        
        last_generation = tuple([0.] * len(self.types))
        generation_count = 0
        while not self._pop_equals(last_generation, this_generation):
            generation_count += 1
            last_generation = this_generation
            this_generation = self._step_generation(last_generation)
            
            self.emit('generation', self, generation_count, this_generation, last_generation)
            
        self.emit('stable state', self, generation_count, this_generation, last_generation, initial_pop)

        return (generation_count, initial_pop, this_generation, self.result_data)
    
    def _interaction(self, my_place, profile):
        """ You should implement this method.
        
        Parameters:
            my_place -- which place of the types the payoff is being calculated for
            profile -- the strategy profile that is being played (tuple of integers)
        
        """
        
        return 1

class NPopDiscreteReplicatorDynamics(Simulation):
    """ Implements an abstract discrete-time replicator dynamics
    
    Methods to Implement:
        _interaction -- Returns the payoff for types
        
    Values to Implement:
        types -- A list of lists of names for the possible types (used to calculate dimensionality of each population and number of populations)
        background_rate -- The natural rate of reproduction (parameter in the dynamics)
        
    Events:
        generation -- emitted when a generation is complete (self, generation_number, new_gen, old_gen)
        initial set -- emitted when the initial population is set up (self, initial_pop)
        stable state -- emitted when a stable state is reached (self, generation_count, final_pop, prev_pop, initial_pop)
    
    """

    effective_zero = 1e-10
    types = [
        ['A','B'], 
        ['C','D']
    ]
    background_rate = 0.
    
    def __init__(self, *args, **kwdargs):
        """ Checks for default_handlers kwdargs parameter and then delegates to the parent.
        
        """
        
        super(NPopDiscreteReplicatorDynamics, self).__init__(*args, **kwdargs)
        
        self.result_data = None
        
        if 'default_handlers' not in kwdargs or kwdargs['default_handlers']:
            self.on('initial set', drep_initial_set_handler)
            self.on('generation', drep_generation_report_handler)
            self.on('stable state', drep_npop_stable_state_handler)
    
    def _random_population(self):
        """ Generate a set of random population on the unit simplex of appropriate dimensionalities
        
        """
        rand.seed()
        
        return tuple([tuple(rand.dirichlet([1] * len(self.types[i]))) for i in xrange(len(self.types))])
    
    def _indiv_pop_equals(self, last, this):
        """ Determine if two populations of the same type are equal or not, accounting for floating point issues
        
        Parameters:
            last -- one of the populations
            this -- the other population
        
        """
        return not any(abs(i - j) >= self.effective_zero for i, j in itertools.izip(last, this))
    
    def _pop_equals(self, last, this):
        """ Determine if two lists of populations are equal or not, accounting for floating point issues
        
        Parameters:
            last -- one of the lists of populations
            this -- the other list of populations
        
        """
        return all(self._indiv_pop_equals(i, j) for i, j in itertools.izip(last, this))
    
    def _step_generation(self, pop):
        """ Step one list of populations to the next generation
        
        Parameters:
            pop -- The list of populations to send to the next generation
        
        """
        # x_i(t+1) = (a + u(e^i, x(t)))*x_i(t) / (a + u(x(t), x(t)))
        # a is background (lifetime) birthrate
        
        payoffs = [None] * len(pop)
        avg_payoffs = [None] * len(pop)
        num_types = [len(self.types[k]) for k in xrange(len(pop))]
        
        print pop
        
        for k in xrange(len(pop)):
            payoffs[k] = [
                math.fsum(
                    float(self._interaction(k, profile)) * float(reduce(operator.mul, [pop[j][profile[j]] for j in xrange(len(profile)) if j != k], 1.)) 
                    for profile in itertools.product(
                        *([xrange(j) for j in num_types[:k]] + [[i]] + [xrange(j) for j in num_types[k+1:]])
                    ))
                for i in xrange(num_types[k])
            ]
            
            print payoffs[k]
            
            avg_payoffs[k] = math.fsum(payoffs[k][i] * float(pop[k][i]) for i in xrange(num_types[k]))
        
        new_pop = [
            tuple([
                float(pop[k][i]) * (float(self.background_rate + payoffs[k][i]) / float(self.background_rate + avg_payoffs[k]))
                for i in xrange(num_types[k])
            ])
            for k in xrange(len(pop))
        ]
        
        return tuple(new_pop)
    
    def _run(self, initial_pop=None):
        """ Actually run the simulation
        
        Parameters:
            initial_pop -- (optional) initial population. Randomizes if not provided.
        
        """
        
        if initial_pop is None:
            initial_pop = self._random_population()
        
        this_generation = initial_pop
        
        self.emit('initial set', self, initial_pop)
        
        last_generation = tuple([tuple([0.] * len(self.types[k])) for k in xrange(len(self.types))])
        generation_count = 0
        while not self._pop_equals(last_generation, this_generation):
            generation_count += 1
            last_generation = this_generation
            this_generation = self._step_generation(last_generation)
            
            self.emit('generation', self, generation_count, this_generation, last_generation)
            
        self.emit('stable state', self, generation_count, this_generation, last_generation, initial_pop)

        return (generation_count, initial_pop, this_generation, self.result_data)
    
    def _interaction(self, my_place, profile):
        """ You should implement this method.
        
        Parameters:
            my_place -- which place of the types the payoff is being calculated for
            profile -- the profile of strategies being played (tuple of integers)
        
        """
        
        return 1
