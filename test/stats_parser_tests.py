import simulations.simulation as simulation
import simulations.simulation_runner as simrunner
import simulations.statsparser as stats

import os
import random
import string

from simulations.utils.optionparser import OptionParser
from nose.tools import assert_equal
from nose.tools import assert_raises

def filename_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

class Sim(simulation.Simulation):
    def _run(self):
        return "runs"
        
class StatsParser(stats.StatsParser):

    def _add_listeners(self):
        super(StatsParser, self)._add_listeners()
        self.on('oparser set up', self._set_options)
        self.on('options parsed', self._check_options)
        self.on('result', self._handle_result)
        self.on('result options', self._handle_result_options)
        self.on('done', self._when_done)
        
    @staticmethod    
    def _set_options(self):
        self.oparser.add_option("-t", "--test", action="store_true", dest="test", default=False, help="Testing")
        
    @staticmethod
    def _check_options(self):
        if not self.options.test:
            self.oparser.error("Test flag not passed")
    
    @staticmethod
    def _handle_result_options(self, out, options):
        print >>out, "{0}".format(options)
        self._result_options = options
        
    @staticmethod
    def _handle_result(self, out, count, result):
        try:
            self._results
        except AttributeError:
            self._results = []
            
        print >>out, result
        self._results.append((count, result))
    
    @staticmethod
    def _when_done(self, out):
        return "test"

class TestStatsParser:
    
    def setUp(self):
        self.stats = StatsParser()
        self.batch = simrunner.SimulationRunner(Sim)
        self.dir = "/tmp/" + filename_generator(8)
        
        try:
            os.makedirs(self.dir, 0755)
        except:
            pass
    
    def tearDown(self):
        if os.path.isdir(self.dir):
            files = os.listdir(self.dir)
            for f in files:
                if f == "." or f == "..": continue
                if f[-8:] == ".testout":
                    os.remove(self.dir + os.sep + f)
            os.rmdir(self.dir)
    
    def test_init(self):
        assert self.stats is not None, "Stats did not get set up"
        assert isinstance(self.stats.oparser, OptionParser), "OptionParser is not set up"
        assert self.stats.options is None, "Options is not None"
        assert self.stats._args is None, "Args is not None"
        
    def test_handler_options(self):
        sim2 = StatsParser(option_error_handler=2, option_exit_handler=3)
        
        assert_equal(sim2.oparser._errorhandler, 2)
        assert_equal(sim2.oparser._exithandler, 3)
        
    def test_options_setup(self):
        assert self.stats.oparser.has_option("-F"), "No -F option"
        assert self.stats.oparser.has_option("--statsfile"), "No --statsfile option"
        assert self.stats.oparser.has_option("-O"), "No -O option"
        assert self.stats.oparser.has_option("--outfile"), "No --outfile option"
        assert self.stats.oparser.has_option("-V"), "No -V option"
        assert self.stats.oparser.has_option("--verbose"), "No --verbose option"
        assert self.stats.oparser.has_option("-t"), "No -t option"
        assert self.stats.oparser.has_option("--test"), "No --test option"
        
    def test_option_failure(self):
        args = ["-F", self.dir + os.sep + "results.testout", "-V", "--test"]
        
        assert_raises(SystemExit, self.stats.go, args)
        
    def test_option_failure2(self):
        with open(self.dir + os.sep + "results.testout", "w") as testfile:
            print >>testfile, "test"
            
        args = ["-F", self.dir + os.sep + "results.testout", "-V"]
        
        assert_raises(SystemExit, self.stats.go, args)
        
    def test_go(self):
        bargs = ["-F",  "iter_{0}.testout", "-N", "4", "-P", "2", "-O", self.dir, "-S", "results.testout"]
        self.batch.go(bargs)
        
        sargs = ["-F", self.dir + os.sep + "results.testout", "-V", "--test"]
        assert self.stats.go(sargs) is None
        assert_equal(self.stats.options.stats_file, self.dir + os.sep + "results.testout")
        assert self.stats.options.out_file is None, "out_file got set"
        assert_equal(self.stats.options.verbose, True)
        assert_equal(self.stats.options.test, True)
        assert_equal(self.stats._result_options, self.batch.options)
        assert_equal(self.stats._results, [(1, "runs"), (2, "runs"), (3, "runs"), (4, "runs")])
        
    def test_go2(self):
        bargs = ["-F",  "iter_{0}.testout", "-N", "5", "-P", "2", "-O", self.dir, "-S", "results.testout"]
        self.batch.go(bargs)
        
        sargs = ["-F", self.dir + os.sep + "results.testout", "-O", self.dir + os.sep + "stats.testout", "--test"]
        assert self.stats.go(sargs) is None
        assert_equal(self.stats.options.stats_file, self.dir + os.sep + "results.testout")
        assert_equal(self.stats.options.out_file, self.dir + os.sep + "stats.testout")
        assert_equal(self.stats.options.verbose, False)
        assert_equal(self.stats.options.test, True)
        assert_equal(self.stats._result_options, self.batch.options)
        assert_equal(self.stats._results, [(1, "runs"), (2, "runs"), (3, "runs"), (4, "runs"), (5, "runs")])
        
        with open(self.dir + os.sep + "stats.testout", "rb") as outfile:
            assert_equal(outfile.read(), "".join(["{0}\n".format(self.stats._result_options)] + (["runs\n"] * 5)))
            
    def test_go3(self):
        bargs = ["-F",  "iter_{0}.testout", "-N", "5", "-P", "2", "-O", self.dir, "-S", "results.testout"]
        self.batch.go(bargs)
        
        sargs = ["-F", self.dir + os.sep + "results.testout", "-O", self.dir + os.sep + "stats.testout", "-V", "--test"]
        assert self.stats.go(sargs) is None
        assert_equal(self.stats.options.stats_file, self.dir + os.sep + "results.testout")
        assert_equal(self.stats.options.out_file, self.dir + os.sep + "stats.testout")
        assert_equal(self.stats.options.verbose, True)
        assert_equal(self.stats.options.test, True)
        assert_equal(self.stats._result_options, self.batch.options)
        assert_equal(self.stats._results, [(1, "runs"), (2, "runs"), (3, "runs"), (4, "runs"), (5, "runs")])
        
        with open(self.dir + os.sep + "stats.testout", "rb") as outfile:
            assert_equal(outfile.read(), "".join(["{0}\n".format(self.stats._result_options)] + (["runs\n"] * 5)))
            
    def test_go4(self):
        with open(self.dir + os.sep + "results.testout", "w") as testfile:
            print >>testfile, "test"
        
        sargs = ["-F", self.dir + os.sep + "results.testout", "-O", self.dir + os.sep + "stats.testout", "--test"]
        assert_raises(ValueError, self.stats.go, sargs)
        assert_equal(self.stats.options.stats_file, self.dir + os.sep + "results.testout")
        assert_equal(self.stats.options.out_file, self.dir + os.sep + "stats.testout")
        assert_equal(self.stats.options.verbose, False)
        assert_equal(self.stats.options.test, True)
