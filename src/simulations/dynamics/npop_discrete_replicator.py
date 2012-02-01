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

from simulations.dynamics.handlers import initial_set_handler
from simulations.dynamics.handlers import generation_report_handler
from simulations.simulation import Simulation


class NPopDiscreteReplicatorDynamics(Simulation):
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

        Simulation.__init__(self, *args, **kwdargs)

        if 'effective_zero' in kwdargs and kwdargs['effective_zero']:
            self.effective_zero = float(kwdargs['effective_zero'])
        else:
            self.effective_zero = 1e-10

        if 'types' in kwdargs and kwdargs['types']:
            self.types = kwdargs['types']
        else:
            self.types = [
                ['A', 'B'],
                ['C', 'D']
            ]

        if 'background_rate' in kwdargs and kwdargs['background_rate']:
            self.background_rate = float(kwdargs['background_rate'])
        else:
            self.background_rate = 0.

        self.result_data = None
        self.force_stop = False

        if 'default_handlers' not in kwdargs or kwdargs['default_handlers']:
            self.on('initial set', initial_set_handler)
            self.on('generation', generation_report_handler)
            self.on('stable state', stable_state_handler)
            self.on('force stop', stable_state_handler)

    def _random_population(self):
        """ Generate a set of random population on the unit simplex of
            appropriate dimensionalities

        """
        rand.seed()

        return tuple([tuple(rand.dirichlet([1] * len(self.types[i])))
                        for i in xrange(len(self.types))])

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

    def _run(self, initial_pop=None):
        """ Actually run the simulation

        Parameters:

            initial_pop
              (optional) initial population. Randomizes if not provided.

        """

        if initial_pop is None:
            initial_pop = self._random_population()

        this_generation = initial_pop

        self.emit('initial set', self, initial_pop)

        last_generation = tuple([tuple([0.] * len(self.types[k]))
                                    for k in xrange(len(self.types))])
        generation_count = 0
        while not self._pop_equals(last_generation, this_generation) and not self.force_stop:
            generation_count += 1
            last_generation = this_generation
            this_generation = self._step_generation(last_generation)

            self.emit('generation',
                        self,
                        generation_count,
                        this_generation,
                        last_generation)

        if self.force_stop:
            self.emit('force stop',
                        self,
                        generation_count,
                        this_generation,
                        last_generation,
                        initial_pop)
        else:
            self.emit('stable state',
                        self,
                        generation_count,
                        this_generation,
                        last_generation,
                        initial_pop)

        return (generation_count,
                initial_pop,
                this_generation,
                self.result_data)

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
    print >> this.out, "=" * 72
    if this.force_stop:
        fstr = "Force stop! ({0} generations)"
    else:
        fstr = "Stable state! ({0} generations)"

    print >> this.out, fstr.format(genct)

    for k in xrange(len(thisgen)):
        print >> this.out, "\tPopulation {0}:".format(k)
        print >> this.out, "\t{0}".format(thisgen[k])
        for i, pop in enumerate(thisgen[k]):
            if abs(pop - 0.) > this.effective_zero:
                fstr3 = "\t\t{0:>5}: {1:>20}: {2}"
                print >> this.out, fstr3.format(i, this.types[k][i], pop)
    print >> this.out
