import simulations.dynamics.onepop_discrete_replicator as dr
import simulations.dynamics.replicator_fastfuncs as fastfuncs
import simulations.simulation as simulation
import math
import numpy as np

from nose.tools import assert_equal


class PDSim(dr.OnePopDiscreteReplicatorDynamics):
    _payoffs = [[3, 0], [4, 1]]

    def __init__(self, *args, **kwdargs):
        if 'types' in kwdargs:
            types = kwdargs['types']
        else:
            types = ['C', 'D']

        super(PDSim, self).__init__(*args, types=types, **kwdargs)

    def _profile_payoffs(self, profile):
        return [self._payoffs[profile[0]][profile[1]], self._payoffs[profile[1]][profile[0]]]


class PDSim2(dr.OnePopDiscreteReplicatorDynamics):
    _payoffs = [[3, 0], [4, 1]]

    def __init__(self, *args, **kwdargs):
        if 'types' in kwdargs:
            types = kwdargs['types']
        else:
            types = ['C', 'D']

        super(PDSim2, self).__init__(*args, types=types, **kwdargs)

    def _profile_payoffs(self, profile):
        return [self._payoffs[profile[0]][profile[1]], self._payoffs[profile[1]][profile[0]]]

    def _add_listeners(self):
        super(PDSim2, self)._add_listeners()

        def generation_listener(this, ct, this_pop, last_pop):
            this.result_data = "test"

        self.on('generation', generation_listener)


class PDSim3(dr.OnePopDiscreteReplicatorDynamics):
    _payoffs = [[3, 0], [4, 1]]

    def __init__(self, *args, **kwdargs):
        if 'types' in kwdargs:
            types = kwdargs['types']
        else:
            types = ['C', 'D']

        super(PDSim3, self).__init__(*args, types=types, **kwdargs)

    def _profile_payoffs(self, profile):
        payoffs = [self._payoffs[profile[0]][profile[1]], self._payoffs[profile[1]][profile[0]]]
        return payoffs

    def _add_listeners(self):
        super(PDSim3, self)._add_listeners()

        def generation_listener(this, ct, this_pop, last_pop):
            this.force_stop = True
            this.result_data = "test2"

        self.on('generation', generation_listener)


class PD3Sim(dr.OnePopDiscreteReplicatorDynamics):
    _payoffs = [
        #me C
        [
            #pl2 C
            [3, 0],
            #pl2 D
            [0, 0]
        ],
        #me D
        [
            #pl2 C
            [8, 4],
            #pl2 D
            [4, 1]
        ]
    ]

    def __init__(self, *args, **kwdargs):
        if 'types' in kwdargs:
            types = kwdargs['types']
        else:
            types = ['C', 'D']

        if 'interaction_arity' in kwdargs:
            ia = kwdargs['interaction_arity']
        else:
            ia = 3

        super(PD3Sim, self).__init__(*args, types=types, interaction_arity=ia, **kwdargs)

    def _profile_payoffs(self, profile):
        return [self._payoffs[profile[0]][profile[1]][profile[2]],
                self._payoffs[profile[1]][profile[2]][profile[0]],
                self._payoffs[profile[2]][profile[0]][profile[1]]]


class TestDiscreteReplicatorDynamics:

    def setUp(self):
        self.sim = dr.OnePopDiscreteReplicatorDynamics({}, 1, False)

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
            assert False, "_profile_payoffs is not defined"
        except TypeError:
            assert False, "_profile_payoffs not given the right parameters"

    def test_effective_zero(self):
        try:
            assert self.sim.effective_zero is not None
            assert_equal(self.sim.effective_zero, 1e-10)
        except AttributeError:
            assert False, "effective_zero is not defined"

    def test_pop_equals(self):
        #try:
        assert fastfuncs.pop_equals(np.array((1., 0.)), np.array((1., self.sim.effective_zero / 10.)), self.sim.effective_zero)
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
        assert (self.sim._step_generation(np.array((.5, .5), dtype=np.float64), 1)[1:] == np.array((.5, .5), dtype=np.float64)).all(), "Generation was not stationary"
        assert (self.sim._step_generation(np.array((0., 1.), dtype=np.float64), 1)[1:] == np.array((0., 1.), dtype=np.float64)).all(), "Generation was not stationary"
        #except AttributeError:
        #    assert False, "_step_generation is not defined"
        #except TypeError:
        #    assert False, "_step_generation not given the right parameters"

    def test_random_population(self):
        try:
            assert self.sim._random_population
            randpop = self.sim._random_population()
            assert_equal(len(randpop), len(self.sim.types))
            assert all(randpop[i] >= 0. for i in xrange(len(randpop)))
            assert abs(math.fsum(randpop) - 1.) < 1e-10
        except AttributeError:
            assert False, "_random_population is not defined"


class TestDiscreteReplicatorCustomization:

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_config(self):
        sim = dr.OnePopDiscreteReplicatorDynamics({},
                                                  1,
                                                  False,
                                                  interaction_arity=4,
                                                  types=['C', 'D'],
                                                  effective_zero=1e-11,
                                                  background_rate=1e-6)
        assert_equal(sim.interaction_arity, 4)
        assert_equal(sim.types, ['C', 'D'])
        assert_equal(sim.effective_zero, 1e-11)
        assert_equal(sim.background_rate, 1e-6)


class TestDiscreteReplicatorInstance:

    def setUp(self):
        self.sim = PDSim({}, 1, False)

    def tearDown(self):
        pass

    def test_interaction(self):
        assert_equal(self.sim._profile_payoffs((0, 0))[0], 3)
        assert_equal(self.sim._profile_payoffs((0, 1))[0], 0)
        assert_equal(self.sim._profile_payoffs((1, 0))[0], 4)
        assert_equal(self.sim._profile_payoffs((1, 1))[0], 1)

        assert_equal(self.sim._profile_payoffs((0, 0))[1], 3)
        assert_equal(self.sim._profile_payoffs((0, 1))[1], 4)
        assert_equal(self.sim._profile_payoffs((1, 0))[1], 0)
        assert_equal(self.sim._profile_payoffs((1, 1))[1], 1)

    def test_step_generation(self):
        assert (self.sim._step_generation(np.array((.5, .5), dtype=np.float64), 1)[1:] == np.array((.375, .625), dtype=np.float64)).all(), "Generation movement was not correct"
        assert (self.sim._step_generation(np.array((0., 1.), dtype=np.float64), 1)[1:] == np.array((0., 1.), dtype=np.float64)).all(), "Generation movement was not correct"

    def test_run(self):
        (gen_ct, initial_pop, final_pop, custom_data) = self.sim.run()
        assert (fastfuncs.pop_equals(final_pop, np.array((0., 1.)), self.sim.effective_zero) or\
                fastfuncs.pop_equals(initial_pop, np.array((1., 0.)), self.sim.effective_zero)), "Final population was unexpected: {0} from {1} -> {2}".format(final_pop,
                                                                             initial_pop,
                                                                             self.sim._step_generation(initial_pop))
        assert gen_ct >= 1
        assert_equal(len(initial_pop), len(self.sim.types))
        assert custom_data is None, "custom data got set somehow"
        assert self.sim.result_data is None, "result_data got set somehow"

    def test_run3(self):
        self.sim.is_running = True
        self.sim.emit('run', self.sim)
        (gen_ct, initial_pop, final_pop, custom_data) = self.sim._run(np.array((1. - 5. * self.sim.effective_zero,
                                                                    5. * self.sim.effective_zero), dtype=np.float64))
        self.sim.emit('done', self.sim)

        assert fastfuncs.pop_equals(final_pop, np.array((0., 1.)), self.sim.effective_zero), "Final population was unexpected: {0} from {1} -> {2}".format(final_pop,
                                                  initial_pop,
                                                  self.sim._step_generation(np.array(initial_pop, dtype=np.float64)))
        assert gen_ct >= 1
        assert_equal(len(initial_pop), len(self.sim.types))


class TestDiscreteReplicatorInstance2:

    def setUp(self):
        self.sim = PDSim2({}, 1, False)

    def tearDown(self):
        pass

    def test_run5(self):
        (gen_ct, initial_pop, final_pop, custom_data) = self.sim.run()
        assert (fastfuncs.pop_equals(final_pop, np.array((0., 1.)), self.sim.effective_zero) or\
               fastfuncs.pop_equals(initial_pop, np.array((1., 0.)), self.sim.effective_zero)), "Final population was unexpected: {0} from {1} -> {2}".format(final_pop,
                                                                             initial_pop,
                                                                             self.sim._step_generation(initial_pop))
        assert gen_ct >= 1
        assert_equal(len(initial_pop), len(self.sim.types))
        assert_equal(self.sim.result_data, "test")
        assert_equal(custom_data, "test")


class TestDiscreteReplicatorInstance3:

    def setUp(self):
        self.sim = PDSim3({}, 1, False)

    def tearDown(self):
        pass

    def test_run6(self):
        (gen_ct, initial_pop, final_pop, custom_data) = self.sim.run()
        assert not (fastfuncs.pop_equals(final_pop, np.array((0., 1.)), self.sim.effective_zero) or\
                fastfuncs.pop_equals(initial_pop, np.array((1., 0.)), self.sim.effective_zero)), "Final population was unexpected: {0} from {1} -> {2}".format(final_pop,
                                                                             initial_pop,
                                                                             self.sim._step_generation(initial_pop))
        assert_equal(gen_ct, 1)
        assert_equal(len(initial_pop), len(self.sim.types))
        assert_equal(self.sim.result_data, "test2")
        assert_equal(custom_data, "test2")
        assert_equal(self.sim.force_stop, True)


class TestDiscreteReplicatorThreeway:

    def setUp(self):
        self.sim = PD3Sim({}, 1, False)

    def tearDown(self):
        pass

    def test_interaction2(self):
        assert_equal(self.sim._profile_payoffs((0, 0, 0))[0], 3)
        assert_equal(self.sim._profile_payoffs((0, 0, 0))[1], 3)
        assert_equal(self.sim._profile_payoffs((0, 0, 0))[2], 3)

        assert_equal(self.sim._profile_payoffs((1, 0, 0))[0], 8)
        assert_equal(self.sim._profile_payoffs((1, 0, 0))[1], 0)
        assert_equal(self.sim._profile_payoffs((1, 0, 0))[2], 0)

        assert_equal(self.sim._profile_payoffs((0, 1, 0))[0], 0)
        assert_equal(self.sim._profile_payoffs((0, 1, 0))[1], 8)
        assert_equal(self.sim._profile_payoffs((0, 1, 0))[2], 0)

        assert_equal(self.sim._profile_payoffs((0, 0, 1))[0], 0)
        assert_equal(self.sim._profile_payoffs((0, 0, 1))[1], 0)
        assert_equal(self.sim._profile_payoffs((0, 0, 1))[2], 8)

        assert_equal(self.sim._profile_payoffs((1, 1, 0))[0], 4)
        assert_equal(self.sim._profile_payoffs((1, 1, 0))[1], 4)
        assert_equal(self.sim._profile_payoffs((1, 1, 0))[2], 0)

        assert_equal(self.sim._profile_payoffs((1, 0, 1))[0], 4)
        assert_equal(self.sim._profile_payoffs((1, 0, 1))[1], 0)
        assert_equal(self.sim._profile_payoffs((1, 0, 1))[2], 4)

        assert_equal(self.sim._profile_payoffs((0, 1, 1))[0], 0)
        assert_equal(self.sim._profile_payoffs((0, 1, 1))[1], 4)
        assert_equal(self.sim._profile_payoffs((0, 1, 1))[2], 4)

        assert_equal(self.sim._profile_payoffs((1, 1, 1))[0], 1)
        assert_equal(self.sim._profile_payoffs((1, 1, 1))[1], 1)
        assert_equal(self.sim._profile_payoffs((1, 1, 1))[2], 1)

    def test_step_generation2(self):
        assert (self.sim._step_generation(np.array((.5, .5), dtype=np.float64))[1:] == np.array((.15, .85), dtype=np.float64)).all(), "Generation did not move right"
        assert (self.sim._step_generation(np.array((0., 1.), dtype=np.float64))[1:] == np.array((0., 1.), dtype=np.float64)).all(), "Generation did not move right"

    def test_run2(self):
        (gen_ct, initial_pop, final_pop, custom_data) = self.sim.run()
        assert fastfuncs.pop_equals(final_pop, np.array((0., 1.)), self.sim.effective_zero), "Final population was unexpected: {0} from {1} -> {2}".format(final_pop,
                                                                             initial_pop,
                                                                             self.sim._step_generation(initial_pop))
        assert gen_ct >= 1
        assert_equal(len(initial_pop), len(self.sim.types))

    def test_run4(self):
        self.sim.is_running = True
        self.sim.emit('run', self.sim)
        (gen_ct, initial_pop, final_pop, custom_data) = self.sim._run(np.array((1. - 2. * self.sim.effective_zero,
                                                                    2. * self.sim.effective_zero), dtype=np.float64))
        self.sim.emit('done', self.sim)

        assert fastfuncs.pop_equals(final_pop, np.array((0., 1.)), self.sim.effective_zero), "Final population was unexpected: {0}".format(final_pop)
        assert gen_ct >= 1
        assert_equal(len(initial_pop), len(self.sim.types))
