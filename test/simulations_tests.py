import gametheory.base.simulation as simulation

from optparse import OptionParser

class Sim(simulation.Simulation):
    def run(self):
        return "runs"

class Batch(simulation.SimulationBatch):
    def _set_options(self):
        self._oparser.add_option("-t", "--test", action="store_true", dest="test", default=False, help="Testing")
        
    def _check_options(self):
        if not self._options.test:
            self._oparser.error("Test flag not passed")
    
    def _set_data(self):
        self._data['test'] = self._options.test
        
    def _when_done(self):
        return "test"

class TestSimulation:
    
    def setUp(self):
        self.sim = Sim(1, 2, 3, 4, 5)

    def tearDown(self):
        self.sim = None
        
    def test_simulation_init(self):
        assert self.sim is not None
        assert self.sim._data == 1
        assert self.sim._num == 2
        assert self.sim._outfile == 3
        assert self.sim._skip == 4
        assert self.sim._quiet == 5
    
    def test_simulation_run(self):
        assert self.sim.run() == "runs"    

class TestSimulationBatch:
    
    def setUp(self):
        self.batch = Batch(Sim)
        
    def tearDown(self):
        self.batch = None
        
    def test_batch_init(self):
        assert self.batch is not None
        assert isinstance(self.batch._oparser, OptionParser)
        assert self.batch._options is None
        assert self.batch._args is None
        assert self.batch._data == {}
        assert self.batch._task_dup_num == False
        
    def test_batch_option_setup(self):
        assert self.batch._oparser.has_option("-D")
        assert self.batch._oparser.has_option("--nofiledump")
        assert self.batch._oparser.has_option("-F")
        assert self.batch._oparser.has_option("--filename")
        assert self.batch._oparser.has_option("-K")
        assert self.batch._oparser.has_option("--skip")
        assert self.batch._oparser.has_option("-N")
        assert self.batch._oparser.has_option("--duplications")
        assert self.batch._oparser.has_option("-O")
        assert self.batch._oparser.has_option("--output")
        assert self.batch._oparser.has_option("-P")
        assert self.batch._oparser.has_option("--poolsize")
        assert self.batch._oparser.has_option("-Q")
        assert self.batch._oparser.has_option("--quiet")
        assert self.batch._oparser.has_option("-S")
        assert self.batch._oparser.has_option("--statsfile")
        assert self.batch._oparser.has_option("-t")
        assert self.batch._oparser.has_option("--test")
        
    def test_batch_go(self):
        pass
