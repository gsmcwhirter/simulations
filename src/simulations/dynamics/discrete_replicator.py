""" Simulation classes that handle variations of discrete-time replicator
    dynamics

Classes:

    DiscreteReplicatorDynamics
      implements one-population discrete time replicator dynamics

"""

from simulations.dynamics.generation_machine import GenerationMachine


class DiscreteReplicatorDynamics(GenerationMachine):
    """ Implements an abstract discrete-time replicator dynamics

    Methods to Implement:

        _interaction
          Returns the payoff for an given set of types

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
        """ Checks for default_handlers kwdargs parameter and then delegates to
            the parent.

        Keyword Parameters:

            effective_zero
              The effective zero value for floating-point comparisons
              (default 1e-10)

            types
              A list of names for the possible types (used to calculate
              dimensionality, default ['A','B'])

            interaction_arity
              The number of players in a given interaction (default 2)

            background_rate
              The natural rate of reproduction (parameter in the dynamics,
              default 0.)

            default_handlers
              Flag to use the default event handlers (default True)

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

        """

        super(DiscreteReplicatorDynamics, self)._add_default_listeners()

        self.add_listener('stable state', stable_state_handler)
        self.add_listener('force stop', stable_state_handler)

    def _default_types(self):
        """ Returns a default type object for the population(s)
            (should implement)

        """

        return []


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
