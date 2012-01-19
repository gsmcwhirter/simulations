import gametheory.base.simulation as simulation

import cPickle
import os
import random
import string
import sys

from gametheory.base.optionparser import OptionParser
from nose.tools import assert_equal
from nose.tools import assert_raises

def filename_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

class Sim(simulation.Simulation):
    def _run(self):
        return "runs"

class Sim2(simulation.Simulation):
    def _run(self):
        print >>self._out, "runs"
            
        return "runs"

class Batch(simulation.SimulationBatch):
    
    def _add_listeners(self):
        self.on('oparser set up', self._set_options)
        self.on('options parsed', self._check_options)
        self.on('options parsed', self._set_data)
        self.on('done', self._when_done)
    
    @staticmethod
    def _set_options(self):
        self._oparser.add_option("-t", "--test", action="store_true", dest="test", default=False, help="Testing")
        
    @staticmethod
    def _check_options(self):
        if not self._options.test:
            self._oparser.error("Test flag not passed")
    
    @staticmethod
    def _set_data(self):
        self._data['test'] = self._options.test
        
    @staticmethod
    def _when_done(self):
        return "test"

class TestSimulation:
    
    def setUp(self):
        self.sim = Sim(1, 2, None)

    def tearDown(self):
        self.sim = None
        
    def test_simulation_init(self):
        assert self.sim is not None, "Sim is not set up"
        assert_equal(self.sim._data, 1)
        assert_equal(self.sim._num, 2)
        assert self.sim._outfile is None, "_outfile is not None"
        assert_equal(self.sim._out, sys.stdout)
        assert_equal(self.sim._out_opened, False)
        
    def test_simulation_set_outfile(self):
        self.sim.set_output_file("/tmp/test")
        assert_equal(self.sim._outfile, "/tmp/test")
        assert self.sim._out is not None, "Sim._out is not set up"
        
        self.sim._close_out_fd(self.sim)
        assert self.sim._out is None, "Sim._out was not closed"
        assert_equal(self.sim._out_opened, False)
        
        self.sim._open_out_fd(self.sim)
        assert self.sim._out is not None, "Sim._out was not opened"
        assert_equal(self.sim._out_opened, True)
        
        self.sim.set_output_file("/tmp/test2")
        self.sim._open_out_fd(self.sim)
        assert self.sim._out is not None, "Sim._out was not opened"
        assert_equal(self.sim._out_opened, True)
        
    def test_simulation_run(self):
        assert_equal(self.sim._out_opened, False)
        
        self.sim.set_output_file(False)
        
        result = self.sim.run()
        assert_equal(self.sim.result, "runs")
        assert_equal(result, "runs")
        
        assert_equal(self.sim._out_opened, False)
        
        assert simulation.Simulation._run(self.sim) is None

    def test_delegation_method(self):
        self.sim.set_output_file(None)
        assert_equal(simulation._run_simulation([Sim, 1, 2, None]), "runs")

class TestSimulationBatch:
    
    def setUp(self):
        self.dir = "/tmp/" + filename_generator(8)
        self.batch = Batch(Sim2)
        
    def tearDown(self):
        self.batch = None
        if os.path.isdir(self.dir):
            files = os.listdir(self.dir)
            for f in files:
                if f == "." or f == "..": continue
                if f[-8:] == ".testout":
                    os.remove(self.dir + os.sep + f)
            os.rmdir(self.dir)
        
    def test_batch_init(self):
        assert self.batch is not None, "Batch is not set up"
        assert isinstance(self.batch._oparser, OptionParser), "Option parser is not initialized"
        assert self.batch._options is None, "Options is initialized"
        assert self.batch._args is None, "Args is initialized"
        assert_equal(self.batch._data, {})
        assert_equal(self.batch._task_dup_num, False)
        
    def test_batch_option_setup(self):
        assert self.batch._oparser.has_option("-D"), "No -D option"
        assert self.batch._oparser.has_option("--nofiledump"), "No --nofiledump option"
        assert self.batch._oparser.has_option("-F"), "No -F option"
        assert self.batch._oparser.has_option("--filename"), "No --filename option"
        assert self.batch._oparser.has_option("-N"), "No -N option"
        assert self.batch._oparser.has_option("--duplications"), "No --duplications option"
        assert self.batch._oparser.has_option("-O"), "No -O option"
        assert self.batch._oparser.has_option("--output"), "No --output option"
        assert self.batch._oparser.has_option("-P"), "No -P option"
        assert self.batch._oparser.has_option("--poolsize"), "No --poolsize option"
        assert self.batch._oparser.has_option("-Q"), "No -Q option"
        assert self.batch._oparser.has_option("--quiet"), "No --quiet option"
        assert self.batch._oparser.has_option("-S"), "No -S option"
        assert self.batch._oparser.has_option("--statsfile"), "No --statsfile option"
        assert self.batch._oparser.has_option("-t"), "No -t option"
        assert self.batch._oparser.has_option("--test"), "No --test option"
        
    def test_batch_go(self):
        args = ["-F",  "iter_{0}.testout", "-N", "4", "-P", "2", "-O", self.dir, "-S", "results.testout", "--test"]
        assert self.batch.go(args) is None
        assert_equal(self.batch._options.test, True)
        assert_equal(self.batch._options.dup, 4)
        assert_equal(self.batch._options.output_dir, self.dir)
        assert_equal(self.batch._options.output_file, "iter_{0}.testout")
        assert_equal(self.batch._options.file_dump, True)
        assert_equal(self.batch._options.stats_file, "results.testout")
        assert_equal(self.batch._options.pool_size, 2)
        assert_equal(self.batch._options.quiet, False)
        
        assert_equal(self.batch._data['test'], True)
        
        for i in range(4):
            assert os.path.isfile(self.dir + os.sep + 'iter_{0}.testout'.format(i + 1)), "Dup file {0} is missing".format(i + 1)
        assert os.path.isfile(self.dir + os.sep + 'results.testout'), "Results file is missing"
        
        for i in range(4):
            with open(self.dir + os.sep + 'iter_{0}.testout'.format(i + 1), "r") as dup_file:
                assert_equal(dup_file.read(), "runs\n")
        
        with open(self.dir + os.sep + 'results.testout', "r") as results_file:
            should_be = ''
            should_be += cPickle.dumps(self.batch._options) + "\n"
            should_be += "\n"
            for _ in range(4):
                should_be += cPickle.dumps("runs") + "\n"
                should_be += "\n"
            assert_equal(results_file.read(), should_be)
            
    def test_batch_go2(self):
        args = ["-N", "6", "-P", "2", "-O", self.dir, "-S", "results.testout", "-Q", "--test", "-D"]
        assert self.batch.go(args) is None
        assert_equal(self.batch._options.test, True)
        assert_equal(self.batch._options.dup, 6)
        assert_equal(self.batch._options.output_dir, self.dir)
        assert_equal(self.batch._options.output_file, "duplication_{0}")
        assert_equal(self.batch._options.file_dump, False)
        assert_equal(self.batch._options.stats_file, "results.testout")
        assert_equal(self.batch._options.pool_size, 2)
        assert_equal(self.batch._options.quiet, True)
        
        assert_equal(self.batch._data['test'], True)
        
        for i in range(6):
            assert not os.path.isfile(self.dir + os.sep + 'iter_{0}.testout'.format(i + 1)), "Dup file {0} is missing".format(i + 1)
        assert os.path.isfile(self.dir + os.sep + 'results.testout'), "Results file is missing"
        
        with open(self.dir + os.sep + 'results.testout', "r") as results_file:
            should_be = ''
            should_be += cPickle.dumps(self.batch._options) + "\n"
            should_be += "\n"
            for _ in range(6):
                should_be += cPickle.dumps("runs") + "\n"
                should_be += "\n"
            assert_equal(results_file.read(), should_be)
    
    def test_option_failure(self):
        args = ["-N", "-6", "-P", "2", "-O", self.dir, "-S", "results.testout", "-Q", "-D", "--test"]
        
        assert_raises(SystemExit, self.batch.go, args)
        
    def test_option_failure2(self):
        args = ["-N", "6", "-P", "2", "-O", self.dir, "-S", "results.testout", "-Q", "-D"]
        
        assert_raises(SystemExit, self.batch.go, args)
