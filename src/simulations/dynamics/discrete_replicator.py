""" Simulation classes that handle variations of discrete-time replicator dynamics

Classes:

    :py:class:`DiscreteReplicatorDynamics`
      implements generic discrete time replicator dynamics

"""

from simulations.dynamics.generation_machine import GenerationMachine


class DiscreteReplicatorDynamics(GenerationMachine):
    """ Implements an abstract discrete-time replicator dynamics

    See also :py:class:`simulations.dynamics.generation_machine.GenerationMachine`

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

        :py:meth:`~simulations.dynamics.generation_machine.GenerationMachine._null_population`
          Returns a population that won't be equal to any starting population

        :py:meth:`~simulations.dynamics.generation_machine.GenerationMachine._pop_equals`
          Returns whether two populations are identical or not

        :py:meth:`~simulations.dynamics.generation_machine.GenerationMachine._random_population`
          Returns a random starting population

        :py:meth:`~simulations.dynamics.generation_machine.GenerationMachine._step_generation`
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

    def __init__(self, *args, **kwdargs):
        """ Handles several keyword parameters and sends the rest up the inheritance chain.

        See also :py:meth:`simulations.dynamics.generation_machine.GenerationMachine.__init__`

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

    def _add_default_listeners(self):
        """ Sets up default event listeners

        Handlers:

            - stable state - :py:func:`stable_state_handler`
            - force stop - :py:func:`stable_state_handler`

        """

        super(DiscreteReplicatorDynamics, self)._add_default_listeners()

        self.add_listener('stable state', stable_state_handler)
        self.add_listener('force stop', stable_state_handler)

    def _default_types(self):
        """ Returns a default type object for the population(s)
            (should implement)

        """

        return []

    def _run(self, *args):
        retval = super(DiscreteReplicatorDynamics, self)._run(*args)

        return (retval[0], tuple(retval[1].tolist()), tuple(retval[2].tolist()), retval[3])


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
