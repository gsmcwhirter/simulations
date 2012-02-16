""" Simulation classes that handle variations of discrete-time replicator dynamics

Classes:

    :py:class:`DiscreteReplicatorDynamics`
      implements generic discrete time replicator dynamics

Functions:

    :py:func:`initial_set_handler`
      Default handler for 'initial set' events

    :py:func:`generation_report_handler`
      Default handler for 'generation' events

"""

import numpy as np
import simulations.dynamics.replicator_fastfuncs as fastfuncs

from simulations.simulation import Simulation


def _create_caches(this, *args):
    """ Handler to wrap around :py:meth:`DiscreteReplicatorDynamics._create_classes`

    """

    this._create_caches()
    this._num_profiles = this._profiles_cache.shape[0]
    this._profile_size = this._profiles_cache.shape[1]
    this._background_rate = np.float64(this.background_rate)
    this._effective_zero = np.float64(this.effective_zero)

    if this._one_or_many == DiscreteReplicatorDynamics.TYPE_ONE:
        this._num_types = np.int(len(this.types))
        this._interaction_arity = np.int(this.interaction_arity)
    elif this._one_or_many == DiscreteReplicatorDynamics.TYPE_MANY:
        this._num_types = np.array([len(i) for i in this.types])
        this._num_pops = np.int(len(this.types))


class DiscreteReplicatorDynamics(Simulation):
    """ Implements an abstract discrete-time replicator dynamics

    Keyword Parameters:

        effective_zero
          The effective zero value for floating-point comparisons
          (default 1e-10)

        types
          A list of names for the possible types (used to calculate
          dimensionality, defaults to the return value of :py:meth:`~DiscreteReplicatorDynamics._default_types`)

        background_rate
          The natural rate of reproduction (parameter in the dynamics,
          default 0.)

    Methods to Implement:

        :py:meth:`~simulations.base.Base._add_listeners`
          Adds listeners to various events

        :py:meth:`~DiscreteReplicatorDynamics._default_types`
          Returns the default value for :py:attr:`DiscreteReplicatorDynamics.types` when no
          keyword parameter is provided to :py:meth:`~DiscreteReplicatorDynamics.__init__`.

        :py:meth:`~DiscreteReplicatorDynamics._null_population`
          Returns a population that won't be equal to any starting population

        :py:meth:`~DiscreteReplicatorDynamics._pop_equals`
          Returns whether two populations are identical or not

        :py:meth:`~DiscreteReplicatorDynamics._random_population`
          Returns a random starting population

        :py:meth:`~DiscreteReplicatorDynamics._step_generation`
          Returns the next generation, given the current one

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

    TYPE_ONE = 1
    TYPE_MANY = 2

    def __init__(self, *args, **kwdargs):
        """ Handles several keyword parameters and sends the rest up the inheritance chain.

        Keyword Parameters:

            effective_zero
              The effective zero value for floating-point comparisons
              (default 1e-10)

            types
              A list of names for the possible types (used to calculate
              dimensionality, defaults to the return value of :py:meth:`~DiscreteReplicatorDynamics._default_types`)

            background_rate
              The natural rate of reproduction (parameter in the dynamics,
              default 0.)

        """

        super(DiscreteReplicatorDynamics, self).__init__(*args, **kwdargs)

        self.result_data = None
        self.force_stop = False

        if 'effective_zero' in kwdargs and kwdargs['effective_zero']:
            self.effective_zero = float(kwdargs['effective_zero'])
        else:
            self.effective_zero = 1e-10

        if 'types' in kwdargs and kwdargs['types']:
            self.types = kwdargs['types']
        else:
            self.types = self._default_types()

        if 'background_rate' in kwdargs and kwdargs['background_rate']:
            self.background_rate = float(kwdargs['background_rate'])
        else:
            self.background_rate = 0.

        self._profiles_cache = None
        self._payoffs_cache = None
        self._one_or_many = None
        self._effective_zero = None
        self._background_rate = None
        self._num_profiles = None
        self._num_types = None
        self._profile_size = None
        self._interaction_arity = None
        self._num_pops = None

        self.on('initial set', _create_caches)

    def _add_default_listeners(self):
        """ Sets up default event listeners

        Handlers:

            - stable state - :py:func:`stable_state_handler`
            - force stop - :py:func:`stable_state_handler`
            - initial set - :py:func:`initial_set_handler`
            - generation - :py:func:`generation_report_handler`

        """

        super(DiscreteReplicatorDynamics, self)._add_default_listeners()

        self.add_listener('stable state', stable_state_handler)
        self.add_listener('force stop', stable_state_handler)
        self.on('initial set', initial_set_handler)
        self.on('generation', generation_report_handler)

    def _default_types(self):
        """ Returns a default type object for the population(s)
            (should implement)

        """

        return []

    def _random_population(self):
        """ Generate a random population of appropriate
            dimensionality (should implement)

        """

        return ()

    def _null_population(self):
        """ Generates a population guaranteed to compare falsely with a random
            population (should implement)

        """

        return ()

    def _step_generation(self, pop, one_or_many=None):
        """ Step one population or list of populations to the next generation

        Parameters:

            pop
              The population or list of populations to send to the next generation

        """
        # x_i(t+1) = (a + u(e^i, x(t)))*x_i(t) / (a + u(x(t), x(t)))
        # a is background (lifetime) birthrate

        if self._profiles_cache is None or self._payoffs_cache is None:
            _create_caches(self)

        if self._one_or_many is None:
            om = one_or_many
        else:
            om = self._one_or_many

        if om == self.TYPE_ONE:
            return fastfuncs.one_dimensional_step(pop,
                                                  self._profiles_cache,
                                                  self._payoffs_cache,
                                                  self._num_types,
                                                  self._interaction_arity,
                                                  self._background_rate,
                                                  self._effective_zero,
                                                  self._num_profiles,
                                                  self._profile_size)

        if om == self.TYPE_MANY:
            return fastfuncs.n_dimensional_step(pop,
                                                self._profiles_cache,
                                                self._payoffs_cache,
                                                self._num_types,
                                                self._background_rate,
                                                self._effective_zero,
                                                self._num_pops,
                                                self._num_profiles,
                                                self._profile_size)

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

        last_generation = self._null_population()
        generation_count = 0
        last_equal = 0
        while last_equal != 1 and not self.force_stop:
            generation_count += 1
            last_generation = this_generation
            tmp = self._step_generation(last_generation)
            last_equal = tmp[0:1][0]
            try:
                last_equal = last_equal[0]
            except IndexError:
                pass

            this_generation = tmp[1:]

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


def initial_set_handler(this, initial_pop):
    """ Handles the 'initial set' event by default for discrete
        replicator dynamics

    Parameters:

        this
          a reference to the simulation

        initial_pop
          the initial population

    """

    print >> this.out, "Initial State: {0}".format(initial_pop)
    print >> this.out


def generation_report_handler(this, genct, thisgen, lastgen):
    """ Print out a report of the current generation

    Parameters:

        this
          a reference to the simulation

        genct
          the generation number

        thisgen
          the current population

        lastgen
          the previous population

    """

    print >> this.out, "-" * 72
    print >> this.out, "Generation {0}:".format(genct)
    print >> this.out, "\t{0}".format(thisgen)
    print >> this.out
    this.out.flush()
