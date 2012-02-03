""" Simulation classes that handle variations of discrete-time replicator
    dynamics

Classes:

    GenerationMachine
      implements one-population discrete time replicator dynamics

"""

from simulations.dynamics.handlers import initial_set_handler
from simulations.dynamics.handlers import generation_report_handler
from simulations.simulation import Simulation


class GenerationMachine(Simulation):
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

        super(GenerationMachine, self).__init__(*args, **kwdargs)

        self.result_data = None
        self.force_stop = False

    def _add_default_listeners(self):
        """ Sets up default event listeners for various events

        """

        super(GenerationMachine, self)._add_default_listeners()

        self.on('initial set', initial_set_handler)
        self.on('generation', generation_report_handler)

    def _random_population(self):
        """ Generate a random population on the unit simplex of appropriate
            dimensionality (should implement)

        """

        return ()

    def _null_population(self):
        """ Generates a population guaranteed to compare falsely with a random
            population (should implement)

        """

        return ()

    def _pop_equals(self, last, this):
        """ Determine if two populations are equal, accounting for floating
            point issues (should implement)

        Parameters:

            last
              one of the populations

            this
              the other population

        """

        return False

    def _step_generation(self, pop):
        """ Step one population to the next generation (should implement)

        Parameters:

            pop
              The population to send to the next generation

        """

        return pop

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
