""" Handle the basics of running parallel simulations

Classes:
Simulation -- Framework for a basic simulation
SimulationBatch -- Handles option parsing and a multiprocessing pool for simulations

"""

__author__="gmcwhirter"

import cPickle
import multiprocessing as mp

from optparse import OptionParser

def _run_simulation(sim):
    return sim.run()

class SimulationBatch:

    """ Handles option parsing and a multiprocessing pool for simulations

    Public Methods:
    go -- Kick off the batch of simulations

    Methods to Implement:
    _set_options -- Set OptionParser options specific to the simulation
    _check_options -- Verify OptionParser options specific to the simulation
    _set_data -- Construct simulation data object
    _format_run -- Format the results of a simulation run
    _when_done -- Clean up after all simulations are complete (optional)

    """

    def __init__(self, SimulationClass):
        """ Set up the simulation batch handler

        Parameters:
        SimulationClass -- The class representing the simulation to run

        """

        self._oparser = OptionParser()
        self._options = None
        self._args = None
        self._data = {}
        self._task_dup_num = False
        self._set_base_options()
        self._set_options()
        self._SimulationClass = SimulationClass

    def go(self):
        """ Verify options and run the batch of simulations"""

        (self._options, self._args) = self._oparser.parse_args()
        self._check_base_options()
        self._check_options()
        self._set_data()

        output_base = "{0}/{1}".format(self._options.output_dir, "{0}")

        stats = open(output_base.format(self._options.stats_file), "wb")

        pool = mp.Pool(self._options.pool_size)
        if not self._options.quiet:
            print "Pool Started: {0}".format(pool)

        mp.log_to_stderr()

        if not self._options.quiet:
            print "Running {0} duplications.".format(self._options.dup)

        if self._options.file_dump:
            tasks = [self._SimulationClass(self._data, i, output_base.format(self._options.output_file.format(i+1)), self._options.skip, self._options.quiet) for i in range(self._options.dup)]
        else:
            tasks = [self._SimulationClass(self._data, i, None, self._options.skip, self._options.quiet) for i in range(self._options.dup)]

        results = pool.imap_unordered(_run_simulation, tasks)
        finished_count = 0
        print >>stats, cPickle.dumps(self._options)
        print >>stats
        for result in results:
            finished_count += 1
            if not self._options.quiet:
                print self._formatRun(result)
            print >>stats, cPickle.dumps(result)
            print >>stats
            stats.flush()
            print "done #{0}".format(finished_count)

        stats.close()
        return self._whenDone()

    def _set_base_options(self):
        """ Set up the basic OptionParser options

        Options:
        -D | --nofiledump -- Do not dump individual simulation output
        -F | --filename -- Format string for file name of individual duplication output
        -K | --skip -- Only dump every K-many simulation runs to file
        -N | --duplications -- Number of trials to run
        -O | --output -- Directory to which to output the results
        -P | --poolsize -- Number of simultaneous trials
        -Q | --quiet -- Suppress all output except aggregate pickle dump
        -S | --statsfile -- File name for aggregate, pickled output

        """

        self._oparser.add_option("-N", "--duplications", type="int", action="store", dest="dup", default=1, help="number of duplications")
        self._oparser.add_option("-O", "--output", action="store", dest="output_dir", default="./output", help="directory to dump output files")
        self._oparser.add_option("-F", "--filename", action="store", dest="output_file", default="duplication_{0}", help="output file name template")
        self._oparser.add_option("-D", "--nofiledump", action="store_false", dest="file_dump", default=True, help="do not output duplication files")
        self._oparser.add_option("-K", "--skip", action="store", type="int", dest="skip", default=1, help="number of generations between dumping output -- 0 for only at the end")
        self._oparser.add_option("-S", "--statsfile", action="store", dest="stats_file", default="aggregate", help="file for aggregate stats to be dumped")
        self._oparser.add_option("-P", "--poolsize", action="store", type="int", dest="pool_size", default=2, help="number of parallel computations to undertake")
        self._oparser.add_option("-Q", "--quiet", action="store_true", dest="quiet", default=False, help="suppress standard output")

    def _check_base_options(self):
        """ Verify the values passed to the base options

        Checks:
        - Number of duplications is positive

        """

        if not self._options.dup or self._options.dup <= 0:
            self._oparser.error("Number of duplications must be positive")

    def _format_run(self, result):
        return result

    def _set_options(self):
        pass

    def _check_options(self):
        pass

    def _set_data(self):
        pass

    def _when_done(self):
        pass

class Simulation:

    """ Base class for an individual simulation

    Public Methods:
    run -- Runs the simulation

    """

    def __init__(self, data, iteration, outfile, skip, quiet):
        """ Sets up the simulation parameters

        Parameters:
        data -- The data object created by the SimulationBatch
        iteration -- The iteration number of the simulation
        outfile -- The name of a file to which to dump output (or None, indicating stdout)
        skip -- The skip of iterations between dumping output (if iteration % skip == 0, output dumps)
        quiet -- Flag to suppress all output

        """

        self._data = data
        self._num = iteration
        self._outfile = outfile
        self._skip = skip
        self._quiet = quiet

    def run(self):
        pass
