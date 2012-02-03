import simulations.base as base
import simulations.simulation as simulation

from nose.tools import assert_equal

def ofchanged(this):
    this.changes += 1

@base.listener('outfile changed', ofchanged)
@base.once('outfile changed', ofchanged)
class Sim3(simulation.Simulation):

    def __init__(self, *args, **kwdargs):
        self.changes = 0
        super(Sim3, self).__init__(*args, **kwdargs)

    def _run(self):
        return "runs"

class TestSimulation3:

    def setUp(self):
        self.sim = Sim3(1, 2, None)

    def test_once_decorator(self):
        assert_equal(self.sim.changes, 2)
        self.sim.set_output_file(False)
        assert_equal(self.sim.changes, 3)
        self.sim.set_output_file(None)
        assert_equal(self.sim.changes, 4)
