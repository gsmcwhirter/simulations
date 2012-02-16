""" Simulation class that implements one-population discrete-time replicator dynamics

Classes:

    :py:class:`OnePopDiscreteReplicatorDynamics`
      implements one-population discrete time replicator dynamics

Functions:

    :py:func:`stable_state_handler`
      Default handler for 'stable state' and 'force stop' events

"""

import itertools
import numpy as np
import numpy.random as rand
import simulations.dynamics.replicator_fastfuncs as fastfuncs

from simulations.dynamics.discrete_replicator import DiscreteReplicatorDynamics


def _create_caches(this, *args):
    this._profiles_cache = fastfuncs.generate_profiles(np.repeat(np.int(len(this.types)), this.interaction_arity))
    this._payoffs_cache = np.array([np.array(this._profile_payoffs(c), dtype=np.float64)
                                                for c in this._profiles_cache])


class OnePopDiscreteReplicatorDynamics(DiscreteReplicatorDynamics):
    """ Implements one-population discrete time replicator dynamics

    Keyword Parameters:

        effective_zero
          The effective zero value for floating-point comparisons
          (default 1e-10)

        interaction_arity
          The number of players in a given interaction (default 2)

        types
          A list of names for the possible types (used to calculate
          dimensionality, defaults to the return value of :py:meth:`~OnePopDiscreteReplicatorDynamics._default_types`)

        background_rate
          The natural rate of reproduction (parameter in the dynamics,
          default 0.)

    Methods to Implement:

        :py:meth:`~OnePopDiscreteReplicatorDynamics._interaction`
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
        """ Checks for the interaction_arity keyword argument and passes up the inheritance chain.

        Keyword Parameters:

            effective_zero
              The effective zero value for floating-point comparisons
              (default 1e-10)

            interaction_arity
              The number of players in a given interaction (default 2)

            types
              A list of names for the possible types (used to calculate
              dimensionality, defaults to the return value of
              :py:meth:`~OnePopDiscreteReplicatorDynamics._default_types`)

            background_rate
              The natural rate of reproduction (parameter in the dynamics,
              default 0.)

        """

        super(OnePopDiscreteReplicatorDynamics, self).__init__(*args, **kwdargs)

        if 'interaction_arity' in kwdargs and kwdargs['interaction_arity']:
            self.interaction_arity = int(kwdargs['interaction_arity'])
        else:
            self.interaction_arity = 2

        self._profiles_cache = None
        self._payoffs_cache = None

        self.on('initial set', _create_caches)

    def _add_default_listeners(self):
        """ Sets up default event listeners

        Handlers:

            - stable state - :py:func:`stable_state_handler`
            - force stop - :py:func:`stable_state_handler`

        """

        super(OnePopDiscreteReplicatorDynamics, self)._add_default_listeners()

        self.add_listener('stable state', stable_state_handler)
        self.add_listener('force stop', stable_state_handler)

    def _default_types(self):
        """ Returns a default type object for the population(s)

        """

        return ['A', 'B']

    def _random_population(self):
        """ Generate a random population on the unit simplex of appropriate
            dimensionality

        """

        rand.seed()

        return rand.dirichlet([1] * len(self.types))

    def _null_population(self):
        """ Generates a population guaranteed to compare falsely with a random
            population

        """

        return np.array([0.] * len(self.types), dtype=np.float64)

    def _pop_equals(self, last, this):
        """ Determine if two populations are equal, accounting for floating
            point issues

        Parameters:

            last
              one of the populations

            this
              the other population

        """

        return not any((abs(i - j) >= self.effective_zero).any()
                        for i, j in itertools.izip(last, this))

    def _step_generation(self, pop):
        """ Step one population to the next generation

        Parameters:

            pop
              The population to send to the next generation

        """
        # x_i(t+1) = (a + u(e^i, x(t)))*x_i(t) / (a + u(x(t), x(t)))
        # a is background (lifetime) birthrate

        if self._profiles_cache is None or self._payoffs_cache is None:
            _create_caches(self)

        return fastfuncs.one_dimensional_step(pop,
                                              self._profiles_cache,
                                              self._payoffs_cache,
                                              np.int(len(self.types)),
                                              np.int(self.interaction_arity),
                                              np.float64(self.background_rate))

    def _interaction(self, my_place, profile):
        """ You should implement this method.
        DEPRECATED - use :py:meth:`~OnePopDiscreteReplicatorDynamics._payoffs` instead

        Parameters:

            my_place
              which place of the types the payoff is being calculated for

            profile
              the strategy profile that is being played (tuple of integers)

        """

        return self._profile_payoffs(profile)[my_place]

    def _profile_payoffs(self, profile):
        """ You should implement this method

        Parameters:

            profile
              the strategy profile that is being played (tuple of integers)

        """

        return [1, 1]


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

    print >> this.out, "\t{0}".format(thisgen)

    fstr3 = "\t\t{0:>5}: {1:>20}: {2}"
    for i, pop in enumerate(thisgen):
        if abs(pop - 0.) > this.effective_zero:
            print >> this.out, fstr3.format(i, this.types[i], pop)
    print >> this.out
