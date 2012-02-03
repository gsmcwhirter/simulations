""" Simulation classes that handle variations of discrete-time replicator
    dynamics

Classes:

    NPopDiscreteReplicatorDynamics
      implements n-population discrete time replicator dynamics

Functions:

    stable_state_handler
      Default handler for 'stable state' and 'force stop' events in n
      populations

"""

import itertools
import math
import numpy.random as rand
import operator

from simulations.dynamics.discrete_replicator import DiscreteReplicatorDynamics


class NPopDiscreteReplicatorDynamics(DiscreteReplicatorDynamics):
    """ Implements an abstract discrete-time replicator dynamics

    Methods to Implement:

        _interaction
          Returns the payoff for types

    Events:

        force stop
          emitted when the generation iteration is broken by a forced stop
          condition (instead of stable state event)

        generation
          emitted when a generation is complete (self, generation_number,
          new_gen, old_gen)

        initial set
          emitted when the initial population is set up (self, initial_pop)

        stable state
          emitted when a stable state is reached (self, generation_count,
          final_pop, prev_pop, initial_pop)

    """

    def __init__(self, *args, **kwdargs):
        """ Checks for kwdargs parameters and then delegates to the parent.

        Keyword Parameters:

            effective_zero
              The effective zero value for floating-point comparisons
              (default 1e-10)

            types
              A list of names for the possible types (used to calculate
              dimensionality, default ['A','B'])

            background_rate
              The natural rate of reproduction (parameter in the dynamics,
              default 0.)

            default_handlers
              Flag to use the default event handlers (default True)

        """

        super(NPopDiscreteReplicatorDynamics, self).__init__(*args, **kwdargs)

    def _add_default_listeners(self):
        """ Sets up default event listeners for various events

        """

        super(NPopDiscreteReplicatorDynamics, self)._add_default_listeners()

        self.on('stable state', stable_state_handler)
        self.on('force stop', stable_state_handler)

    def _default_types(self):
        return [
            ['A', 'B'],
            ['C', 'D']
        ]

    def _random_population(self):
        """ Generate a set of random population on the unit simplex of
            appropriate dimensionalities

        """
        rand.seed()

        return tuple([tuple(rand.dirichlet([1] * len(self.types[i])))
                        for i in xrange(len(self.types))])

    def _null_population(self):

        return tuple([tuple([0.] * len(self.types[k]))
                       for k in xrange(len(self.types))])

    def _indiv_pop_equals(self, last, this):
        """ Determine if two populations of the same type are equal or not,
            accounting for floating point issues

        Parameters:

            last
              one of the populations

            this
              the other population

        """
        return not any(abs(i - j) >= self.effective_zero
                        for i, j in itertools.izip(last, this))

    def _pop_equals(self, last, this):
        """ Determine if two lists of populations are equal or not, accounting
            for floating point issues

        Parameters:

            last
              one of the lists of populations

            this
              the other list of populations

        """
        return all(self._indiv_pop_equals(i, j)
                    for i, j in itertools.izip(last, this))

    def _step_generation(self, pop):
        """ Step one list of populations to the next generation

        Parameters:

            pop
              The list of populations to send to the next generation

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
                    float(self._interaction(k, profile)) *
                            float(reduce(operator.mul, [pop[j][profile[j]]
                                for j in xrange(len(profile)) if j != k], 1.))
                    for profile in itertools.product(
                        *([xrange(j)
                            for j in num_types[:k]] + [[i]] + [xrange(j)
                                for j in num_types[k + 1:]])
                    ))
                for i in xrange(num_types[k])
            ]

            print payoffs[k]

            avg_payoffs[k] = math.fsum(payoffs[k][i] * float(pop[k][i])
                                        for i in xrange(num_types[k]))

        new_pop = [
            tuple([
                float(pop[k][i]) *
                (float(self.background_rate + payoffs[k][i])
                    / float(self.background_rate + avg_payoffs[k]))
                for i in xrange(num_types[k])
            ])
            for k in xrange(len(pop))
        ]

        return tuple(new_pop)

    def _interaction(self, my_place, profile):
        """ You should implement this method.

        Parameters:

            my_place
              which place of the types the payoff is being calculated for

            profile
              the profile of strategies being played (tuple of integers)

        """

        return 1


def stable_state_handler(this, genct, thisgen, lastgen, firstgen):
    """ Print out a report when a stable state is reached.

    Parameters:

        this
          a reference to the simulation

        genct
          the number of generations

        thisgen
          the stable state population

        lastgen
          the previous population

        firstgen
          the initial population

    """

    for k in xrange(len(thisgen)):
        print >> this.out, "\tPopulation {0}:".format(k)
        print >> this.out, "\t{0}".format(thisgen[k])
        for i, pop in enumerate(thisgen[k]):
            if abs(pop - 0.) > this.effective_zero:
                fstr3 = "\t\t{0:>5}: {1:>20}: {2}"
                print >> this.out, fstr3.format(i, this.types[k][i], pop)
    print >> this.out
