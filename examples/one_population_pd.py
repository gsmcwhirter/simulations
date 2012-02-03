## This is hackery to make this run from where it is. Do not do this.
import os
import sys

path = os.path.realpath(__file__)
sys.path.insert(0, os.path.abspath(os.sep.join([path, "..", "..", "src"])))
## End hackery

from simulations.simulation_runner import SimulationRunner
from simulations.dynamics.onepop_discrete_replicator import OnePopDiscreteReplicatorDynamics
from simulations.base import listener
from simulations.base import once


def firstgen(this, gennum, thisgen, lastgen):
    """ Prints 'Working...' after the first generation step is complete

    """

    print >> this.out, 'Working...'


def initialset(this, firstpop):
    """ Prints out a notice for the first population being chosen

    """

    print >> this.out, 'Initial population selected.'


def stablestate(this, genct, thisgen, lastgen, firstgen):
    """ Prints a notice when a stable state is reached

    """

    print >> this.out, 'Stable state reached!'


def forcestop(this, genct, thisgen, lastgen, firstgen):
    """ Prints a notice when the simulation is force-stopped

    """

    print >> this.out, 'Force stopped!'


def generation(this, genct, thisgen, lastgen):
    """ Prints a notice that a generation is done.

    """

    print >> this.out, 'Generation {0} complete.'.format(genct)


def simdone(this, result):
    """ Prints a notice that one of the sims has finished.

    """

    print "Simulation {0} complete.".format(this.finished_count)


def alldone(this):
    """ Prints a notice when all simulations are done.

    """

    print "All done."


@listener('generation', generation)
@listener('force stop', forcestop)
@listener('stable state', stablestate)
@listener('initial set', initialset)
@once('generation', firstgen)
class PrisonersDilemmaSim(OnePopDiscreteReplicatorDynamics):

    _payoffs = [[3, 0], [4, 1]]

    def __init__(self, *args, **kwdargs):
        super(PrisonersDilemmaSim, self).__init__(*args, **kwdargs)

        self.types = ['C', 'D']

    def _interaction(self, me, profile):

        if me == 0 or me == 1:
            return self._payoffs[profile[me]][profile[1 - me]]
        else:
            raise ValueError("Profile index out of bounds")


@listener('result', simdone)
@listener('done', alldone)
class PDSimRunner(SimulationRunner):
    pass

if __name__ == '__main__':
    runner = PDSimRunner(PrisonersDilemmaSim)
    runner.go(pp_modules=("from one_population_pd import PrisonersDilemmaSim",))
