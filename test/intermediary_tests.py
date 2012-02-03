import simulations.dynamics.discrete_replicator as dr
import simulations.dynamics.generation_machine as gm

from nose.tools import assert_equal

class TestDRDefaults:

    def setUp(self):
        self.sim = dr.DiscreteReplicatorDynamics(1, 2, None)

    def test_default_types(self):
        assert_equal(self.sim._default_types(), [])

class TestGMDefault:

    def setUp(self):
        self.sim = gm.GenerationMachine(1, 2, None)

    def test_defaults(self):
        assert_equal(self.sim._random_population(), ())
        assert_equal(self.sim._null_population(), ())
        assert_equal(self.sim._pop_equals(True, True), False)
        assert_equal(self.sim._step_generation(1), 1)
        assert_equal(self.sim._step_generation(2), 2)
