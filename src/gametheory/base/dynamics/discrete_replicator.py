""" Simulation classes that handle variations of discrete-time replicator dynamics

Classes:
    OnePopDiscreteReplicatorDynamics
    NPopDiscreteReplicatorDynamics

"""

import itertools
import math
import numpy.random as rand
import operator

from gametheory.base.simulation import Simulation

class OnePopDiscreteReplicatorDynamics(Simulation):
    """ Implements an abstract discrete-time replicator dynamics
    
    Methods to Implement:
        _interaction -- Returns the payoff for an given set of types
        
    Values to Implement:
        _types -- A list of names for the possible types (used to calculate dimensionality)
        _interaction_arity -- The number of players in a given interaction (default 2)
        _background_rate -- The natural rate of reproduction (parameter in the dynamics)
    
    """
    
    _effective_zero = 1e-10
    _types = ['A','B']
    _interaction_arity = 2
    _background_rate = 0.
    
    def _random_population(self):
        """ Generate a random population on the unit simplex of appropriate dimensionality
        
        """
        
        rand.seed()
        
        return tuple(rand.dirichlet([1] * len(self._types)))
    
    def _pop_equals(self, last, this):
        """ Determine if two populations are equal, accounting for floating point issues
        
        Parameters:
            last -- one of the populations
            this -- the other population
        
        """
        
        return not any(abs(i - j) >= self._effective_zero for i, j in itertools.izip(last, this))
    
    def _step_generation(self, pop):
        """ Step one population to the next generation
        
        Parameters:
            pop -- The population to send to the next generation
        
        """
        # x_i(t+1) = (a + u(e^i, x(t)))*x_i(t) / (a + u(x(t), x(t)))
        # a is background (lifetime) birthrate
        
        num_types = len(self._types)
        payoffs = [
            math.fsum(
                math.fsum(
                    float(self._interaction(k, *profile)) * float(reduce(operator.mul, [pop[profile[j]] for j in xrange(len(profile)) if j != i], 1.))
                    for profile in itertools.product(
                            *([xrange(num_types) for _ in xrange(k)] + [[i]] + [xrange(num_types) for _ in xrange(k+1, self._interaction_arity)])
                    ))
                for k in xrange(self._interaction_arity)
            ) / float(self._interaction_arity)
            for i in xrange(num_types)
        ]
        
        avg_payoff = math.fsum(payoffs[i] * float(pop[i]) for i in xrange(num_types))
        
        new_pop = [float(pop[i]) * ((float(self._background_rate) + float(payoffs[i])) / (float(self._background_rate) + avg_payoff)) for i in xrange(num_types)]
        
        return tuple(new_pop)
    
    def _run(self, initial_pop=None):
        """ Actually run the simulation
        
        Parameters:
            initial_pop -- (optional) initial population. Randomizes if not provided.
        
        """
        
        if initial_pop is None:
            initial_pop = self._random_population()
        
        this_generation = initial_pop
        
        print >>self._out, "Initial State: {0}".format(initial_pop)
        print >>self._out
        
        last_generation = tuple([0.] * len(self._types))
        generation_count = 0
        while not self._pop_equals(last_generation, this_generation):
            generation_count += 1
            last_generation = this_generation
            this_generation = self._step_generation(last_generation)
            
            self._generation_report(generation_count, this_generation, last_generation)
            
        print >>self._out, "=" * 72
        print >>self._out, "Stable state! ({0} generations)".format(generation_count)
        print >>self._out, "\t{0}".format(this_generation)
        for i, pop in enumerate(this_generation):
            if abs(pop - 0.) > self._effective_zero:
                print >>self._out, "\t\t{0}: {1}".format(i, pop)
        print >>self._out

        return (generation_count, initial_pop, this_generation)
    
    def _interaction(self, me, type1, type2):
        """ You should implement this method.
        
        Parameters:
            me -- which place of the types the payoff is being calculated for
            type1 -- the first player type (integer)
            type2 -- the second player type (integer)
            ...
            typen -- the nth player type (integer)
        
        """
        
        return 1
    
    def _generation_report(self, generation_count, this_generation, last_generation):
        """ Print out a report of the current generation
        
        Parameters:
            generation_count -- the generation number
            this_generation -- the current population
            last_generation -- the previous population
        
        """
        
        print >>self._out, "-" * 72
        print >>self._out, "Generation {0}:".format(generation_count)
        print >>self._out, "\t{0}".format(this_generation)
        print >>self._out
        self._out.flush()

class NPopDiscreteReplicatorDynamics(Simulation):
    """ Implements an abstract discrete-time replicator dynamics
    
    Methods to Implement:
        _interaction -- Returns the payoff for types
        
    Values to Implement:
        _types -- A list of lists of names for the possible types (used to calculate dimensionality of each population and number of populations)
        _background_rate -- The natural rate of reproduction (parameter in the dynamics)
    
    """

    _effective_zero = 1e-10
    _types = [
        ['A','B'], 
        ['C','D']
    ]
    _background_rate = 0.
    
    def _random_population(self):
        """ Generate a set of random population on the unit simplex of appropriate dimensionalities
        
        """
        rand.seed()
        
        return tuple([tuple(rand.dirichlet([1] * len(self._types[i]))) for i in xrange(len(self._types))])
    
    def _indiv_pop_equals(self, last, this):
        """ Determine if two populations of the same type are equal or not, accounting for floating point issues
        
        Parameters:
            last -- one of the populations
            this -- the other population
        
        """
        return not any(abs(i - j) >= self._effective_zero for i, j in itertools.izip(last, this))
    
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
        num_types = [len(self._types[k]) for k in xrange(len(pop))]
        
        print pop
        
        for k in xrange(len(pop)):
            payoffs[k] = [
                math.fsum(
                    float(self._interaction(k, *profile)) * float(reduce(operator.mul, [pop[j][profile[j]] for j in xrange(len(profile)) if j != k], 1.)) 
                    for profile in itertools.product(
                        *([xrange(j) for j in num_types[:k]] + [[i]] + [xrange(j) for j in num_types[k+1:]])
                    ))
                for i in xrange(num_types[k])
            ]
            
            print payoffs[k]
            
            avg_payoffs[k] = math.fsum(payoffs[k][i] * float(pop[k][i]) for i in xrange(num_types[k]))
        
        new_pop = [
            tuple([
                float(pop[k][i]) * (float(self._background_rate + payoffs[k][i]) / float(self._background_rate + avg_payoffs[k]))
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
        
        print >>self._out, "Initial State: {0}".format(initial_pop)
        print >>self._out
        
        last_generation = tuple([tuple([0.] * len(self._types[k])) for k in xrange(len(self._types))])
        generation_count = 0
        while not self._pop_equals(last_generation, this_generation):
            generation_count += 1
            last_generation = this_generation
            this_generation = self._step_generation(last_generation)
            
            self._generation_report(generation_count, this_generation, last_generation)
            
        print >>self._out, "=" * 72
        print >>self._out, "Stable state! ({0} generations)".format(generation_count)
        for k in xrange(len(this_generation)):
            print >>self._out, "\tPopulation {0}:".format(k)
            print >>self._out, "\t{0}".format(this_generation[k])
            for i, pop in enumerate(this_generation[k]):
                if abs(pop - 0.) > self._effective_zero:
                    print >>self._out, "\t\t{0}: {1}".format(i, pop)
        print >>self._out

        return (generation_count, initial_pop, this_generation)
    
    def _interaction(self, me, type1, type2):
        """ You should implement this method.
        
        Parameters:
            me -- which place of the types the payoff is being calculated for
            type1 -- the first player type (integer)
            type2 -- the second player type (integer)
            ...
            typen -- the nth player type (integer)
        
        """
        
        return 1
    
    def _generation_report(self, generation_count, this_generation, last_generation):
        """ Print out a report of the current generation
        
        Parameters:
            generation_count -- the generation number
            this_generation -- the current population
            last_generation -- the previous population
        
        """
        
        print >>self._out, "-" * 72
        print >>self._out, "Generation {0}:".format(generation_count)
        print >>self._out, "\t{0}".format(this_generation)
        print >>self._out
        self._out.flush()
