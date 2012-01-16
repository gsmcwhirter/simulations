import gametheory.base.simulation as simulation

from nose import with_setup

def setup_sim():
    class TestSim(simulation.Simulation):
        def run(self):
            return "runs"

    sim = TestSim(1, 2, 3, 4, 5)

def teardown_sim():
    pass

@with_setup(setup_sim, teardown_sim)
def test_simulation_init():
    assert sim.getData() == 1
    assert sim.getIteration() == 2
    assert sim.getOutfile() == 3
    assert sim.getSkip() == 4
    assert sim.getQuiet() == 5

@with_setup(setup_sim, teardown_sim)
def test_simulation_run():
    assert sim.run() == "runs"