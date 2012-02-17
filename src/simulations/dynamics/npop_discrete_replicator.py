""" Simulation class that implements n-population discrete-time replicator dynamics

Classes:

    :py:class:`NPopDiscreteReplicatorDynamics`
      implements n-population discrete time replicator dynamics

Functions:

    :py:func:`stable_state_handler`
      Default handler for 'stable state' and 'force stop' events in n
      populations

"""

import numpy as np
import numpy.random as rand
import simulations.dynamics.replicator_fastfuncs as fastfuncs

from simulations.dynamics.discrete_replicator import DiscreteReplicatorDynamics


class NPopDiscreteReplicatorDynamics(DiscreteReplicatorDynamics):
    """ Implements n-population discrete time replicator dynamics

    Keyword Parameters:

        effective_zero
          The effective zero value for floating-point comparisons
          (default 1e-10)

        types
          A list of names for the possible types (used to calculate
          dimensionality, defaults to the return value of :py:meth:`~NPopDiscreteReplicatorDynamics._default_types`)

        background_rate
          The natural rate of reproduction (parameter in the dynamics,
          default 0.)

    Methods to Implement:

        :py:meth:`~NPopDiscreteReplicatorDynamics._profile_payoffs`
          Returns the payoff for a type given a strategy profile

    Events:

        force stop(this, genct, finalgen, prevgen, firstgen)
          emitted when the generation iteration is broken by a forced stop
          condition (instead of stable state event)

        generation(this, genct, thisgen, lastgen)
          emitted when a generation is complete

        initial set(this, initial_pop)
          emitted when the initial population is set up

        stable state(this, genct, finalgen, prevgen, firstgen)
          emitted when a stable state is reached

    """

    def __init__(self, *args, **kwdargs):
        """ Checks for kwdargs parameters and then delegates to the parent.

        """

        super(NPopDiscreteReplicatorDynamics, self).__init__(*args, **kwdargs)

        self._one_or_many = self.TYPE_MANY

    def _add_default_listeners(self):
        """ Sets up default event listeners for various events

        Handlers:

            - stable state - :py:func:`stable_state_handler`
            - force stop - :py:func:`stable_state_handler`

        """

        super(NPopDiscreteReplicatorDynamics, self)._add_default_listeners()

        self.on('stable state', stable_state_handler)
        self.on('force stop', stable_state_handler)

    def _default_types(self):
        """ Returns the default types if none are given to the constructor

        """

        return [
            ['A', 'B'],
            ['C', 'D']
        ]

    def _random_population(self):
        """ Generate a set of random population on the unit simplex of
            appropriate dimensionalities

        """
        rand.seed()

        samples = [rand.dirichlet([1] * len(self.types[i]))
                        for i in xrange(len(self.types))]

        type_cts = [len(i) for i in self.types]
        max_type_ct = max(type_cts)

        initpop = np.zeros([len(self.types), max_type_ct], dtype=np.float64)

        for i, sample in enumerate(samples):
            initpop[i, :type_cts[i]] = samples[i]

        return initpop

    def _null_population(self):
        """ Generates a population that will not be equal to any initial population

        """

        type_cts = [len(i) for i in self.types]
        max_type_ct = max(type_cts)

        initpop = np.zeros([max_type_ct] * len(self.types), dtype=np.float64)

        return initpop

    def _profile_payoffs(self, profile):
        """ You should implement this method

        Parameters:

            profile
              the strategy profile that is being played (tuple of integers)

        """

        return [1, 1]

    def _create_caches(self):
        self._profiles_cache = fastfuncs.generate_profiles(np.array([np.int(len(i))
                                                            for i in self.types]))
        self._payoffs_cache = np.array([np.array(self._profile_payoffs(c), dtype=np.float64)
                                                    for c in self._profiles_cache])


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
