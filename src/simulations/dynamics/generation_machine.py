""" Provides a very abstract generation-step machine

Classes:

    :py:class:`GenerationMachine`
      A very abstract generation-step machine.
      You should probably not use this directly.

Functions:

    :py:func:`initial_set_handler`
      Default handler for 'initial set' events

    :py:func:`generation_report_handler`
      Default handler for 'generation' events

"""

from simulations.simulation import Simulation


class GenerationMachine(Simulation):
    """ Implements an abstract generation-step machine

    Methods to Implement:

        :py:meth:`~simulations.base.Base._add_listeners`
          Adds listeners to various events

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
        """ Sets up some attributes and delegates up the inheritance chain.

        """

        super(GenerationMachine, self).__init__(*args, **kwdargs)

        self.result_data = None
        self.force_stop = False

    def _add_default_listeners(self):
        """ Sets up default event listeners for various events

        Handlers:

            - initial set - :py:func:`simulations.dynamics.handlers.initial_set_handler`
            - generation - :py:func:`simulations.dynamics.handlers.generation_report_handler`

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
