import numpy as np
import simulations.dynamics.replicator_fastfuncs as fastfuncs


class TestFastFuncs:

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_generate_profiles(self):
        assert fastfuncs.generate_profiles is not None
        assert (fastfuncs.generate_profiles(np.array([2, 2])) ==\
                 np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.int)).all(), "Profiles not generated correctly"
