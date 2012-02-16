import simulations.dynamics.npop_discrete_replicator as dr
import simulations.dynamics.replicator_fastfuncs as fastfuncs
import simulations.simulation as simulation
import math
import numpy as np

from nose.tools import assert_equal

class PDSim(dr.NPopDiscreteReplicatorDynamics):
    _payoffs = [[3., 0.],[4., 1.]]

    def __init__(self, *args, **kwdargs):
        super(PDSim, self).__init__(*args, types = [
        ['C', 'D'],
        ['C', 'D']
    ], **kwdargs)

    def _profile_payoffs(self, profile):
        return [self._payoffs[profile[0]][profile[1]], self._payoffs[profile[1]][profile[0]]]

class PDSim2(dr.NPopDiscreteReplicatorDynamics):
    types = [
        ['C', 'D'],
        ['C', 'D']
    ]
    _payoffs = [[3., 0.],[4., 1.]]

    def _profile_payoffs(self, profile):
        return [self._payoffs[profile[0]][profile[1]], self._payoffs[profile[1]][profile[0]]]

    def _add_listeners(self):
        super(PDSim2, self)._add_listeners()

        def generation_listener(this, ct, this_pop, last_pop):
            this.result_data = "test"

        self.on('generation', generation_listener)

class PDSim3(dr.NPopDiscreteReplicatorDynamics):
    types = [
        ['C', 'D'],
        ['C', 'D']
    ]
    _payoffs = [[3., 0.],[4., 1.]]

    def _profile_payoffs(self, profile):
        return [self._payoffs[profile[0]][profile[1]], self._payoffs[profile[1]][profile[0]]]

    def _add_listeners(self):
        super(PDSim3, self)._add_listeners()

        def generation_listener(this, ct, this_pop, last_pop):
            this.result_data = "test2"
            this.force_stop = True

        self.on('generation', generation_listener)

class OddGameSim(dr.NPopDiscreteReplicatorDynamics):

    _payoffs = [
                #first 0
                [
                    #second 0
                    [[2,1,3], [3,1,2], [4,1,1]],
                    #second 1
                    [[1,2,1], [1,3,2], [1,4,3]]
                ],
                #first 1
                [
                    #second 0
                    [[1,2,1], [1,3,2], [1,4,3]],
                    #second 1
                    [[2,1,3], [3,1,2], [4,1,1]]
                ]
                ]

    def __init__(self, *args, **kwdargs):
        super(OddGameSim, self).__init__(*args, **kwdargs)
        self.types = [range(2), range(2), range(3)]

    def _profile_payoffs(self, profile):
        return self._payoffs[profile[0]][profile[1]][profile[2]]

class TestNPopDiscreteReplicatorDynamics:

    def setUp(self):
        self.sim = dr.NPopDiscreteReplicatorDynamics({}, 1, False)

    def tearDown(self):
        pass

    def test_init(self):
        assert self.sim is not None, "Sim is not set up"
        assert isinstance(self.sim, simulation.Simulation), "Sim is not a simulation instance"

    def test_interaction(self):
        try:
            assert self.sim._profile_payoffs
            assert_equal(self.sim._profile_payoffs((0, 1))[0], 1)
            assert_equal(self.sim._profile_payoffs((0, 1))[1], 1)
        except AttributeError:
            assert False, "_interaction is not defined"
        except TypeError:
            assert False, "_interaction not given the right parameters"

    def test_effective_zero(self):
        try:
            assert self.sim.effective_zero is not None
            assert_equal(self.sim.effective_zero, 1e-10)
        except AttributeError:
            assert False, "_effective_zero is not defined"

    def test_pop_equals(self):
        #try:
        assert fastfuncs.pop_equals
        assert fastfuncs.pop_equals(np.array(((1., 0.), (1., 0.)), dtype=np.float64), np.array(((1., self.sim.effective_zero / 10.), (1., self.sim.effective_zero / 10.)), dtype=np.float64), self.sim.effective_zero)
        #except AttributeError:
        #    assert False, "_pop_equals is not defined"
        #except TypeError:
        #    assert False, "_pop_equals not given the right parameters"

    def test_types(self):
        try:
            assert self.sim.types is not None
        except AttributeError:
            assert False, "_types is not defined"

    def test_background_rate(self):
        try:
            assert self.sim.background_rate is not None
            assert_equal(self.sim.background_rate, 0.)
        except AttributeError:
            assert False, "_background_rate is not defined"

    def test_step_generation(self):
        #try:
        assert self.sim._step_generation
        print self.sim._step_generation(np.array(((.5, .5), (.5, .5))))
        assert (self.sim._step_generation(np.array(((.5, .5), (.5, .5))))[1:] ==\
                np.array(((.5, .5), (.5, .5)))).all(), "Generation didn't move right"
        assert (self.sim._step_generation(np.array(((0., 1.), (0., 1.))))[1:] ==\
                np.array(((0., 1.), (0., 1.)))).all(), "Generation didn't move right"
        #except AttributeError:
        #    assert False, "_step_generation is not defined"
        #except TypeError:
        #    assert False, "_step_generation not given the right parameters"

    def test_random_population(self):
        try:
            assert self.sim._random_population
            randpop = self.sim._random_population()
            assert_equal(len(randpop), len(self.sim.types))
            for k in xrange(len(self.sim.types)):
                assert_equal(len(randpop[k]), len(self.sim.types[k]))
                assert all(randpop[k][i] >= 0. for i in xrange(len(randpop[k])))
                assert abs(math.fsum(randpop[k]) - 1.) < 1e-10
        except AttributeError:
            assert False, "_random_population is not defined"

class TestDiscreteReplicatorCustomization:

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_config(self):
        sim = dr.NPopDiscreteReplicatorDynamics({}, 1, False, types=[['C','D'],['C','D']], effective_zero=1e-11, background_rate=1e-6)
        assert_equal(sim.types, [['C','D'],['C','D']])
        assert_equal(sim.effective_zero, 1e-11)
        assert_equal(sim.background_rate, 1e-6)

class TestNPopDiscreteReplicatorInstance:

    def setUp(self):
        self.sim = PDSim({}, 1, False)

    def tearDown(self):
        pass

    def test_interaction(self):
        assert_equal(self.sim._profile_payoffs((0,0))[0], 3)
        assert_equal(self.sim._profile_payoffs((0,1))[0], 0)
        assert_equal(self.sim._profile_payoffs((1,0))[0], 4)
        assert_equal(self.sim._profile_payoffs((1,1))[0], 1)

        assert_equal(self.sim._profile_payoffs((0,0))[1], 3)
        assert_equal(self.sim._profile_payoffs((0,1))[1], 4)
        assert_equal(self.sim._profile_payoffs((1,0))[1], 0)
        assert_equal(self.sim._profile_payoffs((1,1))[1], 1)

    def test_step_generation(self):
        assert (self.sim._step_generation(np.array(((.5, .5),(.5,.5)), dtype=np.float64))[1:] == np.array(((.375, .625), (.375, .625)), dtype=np.float64)).all(), "Generation didn't move right"
        assert (self.sim._step_generation(np.array(((0., 1.),(0.,1.))))[1:] == np.array(((0., 1.),(0., 1.)))).all(), "Generation didn't move right"

    def test_run(self):
        (gen_ct, initial_pop, final_pop, custom_data) = self.sim.run()
        assert fastfuncs.pop_equals(final_pop, np.array(((0., 1.), (0., 1.))), self.sim.effective_zero), "Final population was instead {0}".format(final_pop)
        assert gen_ct >= 1
        assert_equal(len(initial_pop), len(self.sim.types))
        assert custom_data is None, "Custom data got set somehow"

class TestNPopDiscreteReplicatorInstance2:

    def setUp(self):
        self.sim = PDSim2({}, 1, False)

    def tearDown(self):
        pass

    def test_run(self):
        (gen_ct, initial_pop, final_pop, custom_data) = self.sim.run()
        assert fastfuncs.pop_equals(final_pop, np.array(((0., 1.), (0., 1.))), self.sim.effective_zero), "Final population was instead {0}".format(final_pop)
        assert gen_ct >= 1
        assert_equal(len(initial_pop), len(self.sim.types))
        assert_equal(self.sim.result_data, "test")
        assert_equal(custom_data, "test")

class TestNPopDiscreteReplicatorInstance3:

    def setUp(self):
        self.sim = PDSim3({}, 1, False)

    def tearDown(self):
        pass

    def test_run(self):
        (gen_ct, initial_pop, final_pop, custom_data) = self.sim.run()
        assert not fastfuncs.pop_equals(final_pop, np.array(((0., 1.), (0., 1.))), self.sim.effective_zero), "Final population was still {0}".format(final_pop)
        assert_equal(gen_ct, 1)
        assert_equal(len(initial_pop), len(self.sim.types))
        assert_equal(self.sim.result_data, "test2")
        assert_equal(custom_data, "test2")
        assert_equal(self.sim.force_stop, True)


class TestOddGameSim:

    def setUp(self):
        self.sim = OddGameSim({}, 1, False)

    def tearDown(self):
        pass

    def test_run(self):
        (gen_ct, initial_pop, final_pop, custom_data) = self.sim.run()
        assert not fastfuncs.pop_equals(final_pop, np.array(((0., 1., 0.), (0., 1., 0.), (0., 0., 1.))), self.sim.effective_zero), "Final population was {0}".format(final_pop)
        assert gen_ct > 1
        assert_equal(len(initial_pop), len(self.sim.types))
        assert_equal(self.sim.force_stop, False)
