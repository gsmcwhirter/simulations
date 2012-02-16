import simulations.dynamics.discrete_replicator as dr

from nose.tools import assert_equal


class TestDRDefaults:

    def setUp(self):
        self.sim = dr.DiscreteReplicatorDynamics(1, 2, None)

    def test_default_types(self):
        assert_equal(self.sim._default_types(), [])
        assert_equal(self.sim._random_population(), ())
        assert_equal(self.sim._null_population(), ())
