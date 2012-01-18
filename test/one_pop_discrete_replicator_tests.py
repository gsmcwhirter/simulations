import gametheory.base.dynamics.discrete_replicator as dr
import gametheory.base.simulation as simulation
import math

from nose.tools import assert_equal

class PDSim(dr.OnePopDiscreteReplicatorDynamics):
    _types = ['C', 'D']
    _payoffs = [[3, 0],[4, 1]]
    
    def _interaction(self, me, type1, type2):
        if me == 0:
            return self._payoffs[type1][type2]
        elif me == 1:
            return self._payoffs[type2][type1]
        else:
            raise ValueError("Unknown me value")
    
class PD3Sim(dr.OnePopDiscreteReplicatorDynamics):
    _types = ['C', 'D']
    _interaction_arity = 3
    _payoffs = [
        [
            [3, 0], #pl2 C
            [0, 0] #pl2 D
        ], #me C
        [
            [8, 4], #pl2 C
            [4, 1] #pl2 D
        ] #me D
    ]
    
    def _interaction(self, me, type1, type2, type3):
        if me == 0:
            return self._payoffs[type1][type2][type3]
        elif me == 1:
            return self._payoffs[type2][type3][type1]
        elif me == 2:
            return self._payoffs[type3][type1][type2]
        else:
            raise ValueError("Unknown me value")

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
            assert self.sim._interaction
            assert_equal(self.sim._interaction(0, 0, 1), 1)
            assert_equal(self.sim._interaction(1, 0, 1), 1)
        except AttributeError:
            assert False, "_interaction is not defined"
        except TypeError:
            assert False, "_interaction not given the right parameters"
            
    def test_effective_zero(self):
        try:
            assert self.sim._effective_zero is not None
            assert_equal(self.sim._effective_zero, 1e-10)
        except AttributeError:
            assert False, "_effective_zero is not defined"
            
    def test_pop_equals(self):
        try:
            assert self.sim._pop_equals
            assert self.sim._pop_equals((1., 0.), (1., self.sim._effective_zero / 10.))
        except AttributeError:
            assert False, "_pop_equals is not defined"
        except TypeError:
            assert False, "_pop_equals not given the right parameters"
            
    def test_types(self):
        try:
            assert self.sim._types is not None
        except AttributeError:
            assert False, "_types is not defined"
            
    def test_background_rate(self):
        try:
            assert self.sim._background_rate is not None
            assert_equal(self.sim._background_rate, 0.)
        except AttributeError:
            assert False, "_background_rate is not defined"
            
    def test_step_generation(self):
        try:
            assert self.sim._step_generation
            assert_equal(self.sim._step_generation((.5, .5)), (.5, .5))
            assert_equal(self.sim._step_generation((0., 1.)), (0., 1.))
        except AttributeError:
            assert False, "_step_generation is not defined"
        except TypeError:
            assert False, "_step_generation not given the right parameters"
            
    def test_random_population(self):
        try:
            assert self.sim._random_population
            randpop = self.sim._random_population()
            assert_equal(len(randpop), len(self.sim._types))
            assert all(randpop[i] >= 0. for i in xrange(len(randpop)))
            assert abs(math.fsum(randpop) - 1.) < 1e-10
        except AttributeError:
            assert False, "_random_population is not defined"
            
class TestDiscreteReplicatorInstance:
    
    def setUp(self):
        self.sim = PDSim({}, 1, False)
        
    def tearDown(self):
        pass
    
    def test_interaction(self):
        assert_equal(self.sim._interaction(0,0,0), 3)
        assert_equal(self.sim._interaction(0,0,1), 0)
        assert_equal(self.sim._interaction(0,1,0), 4)
        assert_equal(self.sim._interaction(0,1,1), 1)
        
        assert_equal(self.sim._interaction(1,0,0), 3)
        assert_equal(self.sim._interaction(1,0,1), 4)
        assert_equal(self.sim._interaction(1,1,0), 0)
        assert_equal(self.sim._interaction(1,1,1), 1)
        
    def test_step_generation(self):
        assert_equal(self.sim._step_generation((.5, .5)), (.375, .625))
        assert_equal(self.sim._step_generation((0., 1.)), (0., 1.))
    
    def test_run(self):
        (gen_ct, initial_pop, final_pop) = self.sim.run()
        assert self.sim._pop_equals(final_pop, (0., 1.)) or self.sim._pop_equals(initial_pop, (1., 0.)), "Final population was unexpected: {0} from {1} -> {2}".format(final_pop, initial_pop, self.sim._step_generation(initial_pop))
        assert gen_ct >= 1
        assert_equal(len(initial_pop), len(self.sim._types))
        
    def test_run3(self):
        self.sim._open_out_fd()
        (gen_ct, initial_pop, final_pop) = self.sim._run((1. - 5. * self.sim._effective_zero, 5. * self.sim._effective_zero))
        self.sim._close_out_fd()
        
        assert self.sim._pop_equals(final_pop, (0., 1.)), "Final population was unexpected: {0} from {1} -> {2}".format(final_pop, initial_pop, self.sim._step_generation(initial_pop))
        assert gen_ct >= 1
        assert_equal(len(initial_pop), len(self.sim._types))
        
class TestDiscreteReplicatorThreeway:        
    
    def setUp(self):
        self.sim = PD3Sim({}, 1, False)
        
    def tearDown(self):
        pass
    
    def test_interaction2(self):
        assert_equal(self.sim._interaction(0,0,0,0), 3)
        assert_equal(self.sim._interaction(1,0,0,0), 3)
        assert_equal(self.sim._interaction(2,0,0,0), 3)
        
        assert_equal(self.sim._interaction(0,1,0,0), 8)
        assert_equal(self.sim._interaction(1,1,0,0), 0)
        assert_equal(self.sim._interaction(2,1,0,0), 0)
        
        assert_equal(self.sim._interaction(0,0,1,0), 0)
        assert_equal(self.sim._interaction(1,0,1,0), 8)
        assert_equal(self.sim._interaction(2,0,1,0), 0)
        
        assert_equal(self.sim._interaction(0,0,0,1), 0)
        assert_equal(self.sim._interaction(1,0,0,1), 0)
        assert_equal(self.sim._interaction(2,0,0,1), 8)
        
        assert_equal(self.sim._interaction(0,1,1,0), 4)
        assert_equal(self.sim._interaction(1,1,1,0), 4)
        assert_equal(self.sim._interaction(2,1,1,0), 0)
        
        assert_equal(self.sim._interaction(0,1,0,1), 4)
        assert_equal(self.sim._interaction(1,1,0,1), 0)
        assert_equal(self.sim._interaction(2,1,0,1), 4)
        
        assert_equal(self.sim._interaction(0,0,1,1), 0)
        assert_equal(self.sim._interaction(1,0,1,1), 4)
        assert_equal(self.sim._interaction(2,0,1,1), 4)
        
        assert_equal(self.sim._interaction(0,1,1,1), 1)
        assert_equal(self.sim._interaction(1,1,1,1), 1)
        assert_equal(self.sim._interaction(2,1,1,1), 1)

    def test_step_generation2(self):
        assert_equal(self.sim._step_generation((.5, .5)), (.15, .85))
        assert_equal(self.sim._step_generation((0., 1.)), (0., 1.))
    
    def test_run2(self):
        (gen_ct, initial_pop, final_pop) = self.sim.run()
        assert self.sim._pop_equals(final_pop, (0., 1.)) or self.sim._pop_equals(initial_pop, (1., 0.)), "Final population was unexpected: {0} from {1} -> {2}".format(final_pop, initial_pop, self.sim._step_generation(initial_pop))
        assert gen_ct >= 1
        assert_equal(len(initial_pop), len(self.sim._types))
        
    def test_run4(self):
        self.sim._open_out_fd()
        (gen_ct, initial_pop, final_pop) = self.sim._run((1. - 2. * self.sim._effective_zero, 2. * self.sim._effective_zero))
        self.sim._close_out_fd()
        
        assert self.sim._pop_equals(final_pop, (0., 1.)), "Final population was unexpected: {0}".format(final_pop)
        assert gen_ct >= 1
        assert_equal(len(initial_pop), len(self.sim._types))
