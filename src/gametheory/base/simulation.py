""" Handle the basics of running parallel simulations

Classes:
    OptionParser -- Extension of optparse.OptionParser to allow prevention of auto-exit
    Simulation -- Framework for a basic simulation
    SimulationBatch -- Handles option parsing and a multiprocessing pool for simulations

"""

__author__="gmcwhirter"

import cPickle
import multiprocessing as mp
import os
import sys

from gametheory.base.optionparser import OptionParser

def _run_simulation(sim):
    """ A simple function to run the simulation. Used with the multiprocessing pool.
    
    """
    
    return sim.run()

class SimulationBatch(object):

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

    def __init__(self, SimulationClass, *args, **kwdargs):
        """ Set up the simulation batch handler

        Parameters:
            SimulationClass -- The class representing the simulation to run
        
        Keyword Parameters:
            option_error_handler -- An error handler for the option parser
            option_exit_handler -- An exit handler for the option parser

        """

        self._oparser = OptionParser()
        
        try:
            self._oparser.set_error_handler(kwdargs['option_error_handler'])
        except KeyError:
            pass
    
        try:
            self._oparser.set_exit_handler(kwdargs['option_exit_handler'])
        except KeyError:
            pass
        
        self._options = None
        self._args = None
        self._data = {}
        self._task_dup_num = False
        self._set_base_options()
        self._set_options()
        self._SimulationClass = SimulationClass

    def go(self, option_args=None, option_values=None):
        """ Verify options and run the batch of simulations
        
        Parameters:
            option_args -- arguments to pass to the option parser. Defaults to sys.argv[1:].
            option_values -- target of option parsing (probably should not use)
            
        """

        (self._options, self._args) = self._oparser.parse_args(args=option_args, values=option_values)
        self._check_base_options()
        self._check_options()
        self._set_data()
        
        if not os.path.isdir(self._options.output_dir):
            os.makedirs(self._options.output_dir, 0755)

        output_base = ("{0}" + os.sep + "{1}").format(self._options.output_dir, "{0}")

        stats = open(output_base.format(self._options.stats_file), "wb")

        mplog = mp.log_to_stderr()
        mplog.setLevel(mp.SUBWARNING)

        pool = mp.Pool(self._options.pool_size)
        if not self._options.quiet:
            print "Pool Started: {0} workers".format(self._options.pool_size)        

        if not self._options.quiet:
            print "Running {0} duplications.".format(self._options.dup)

        tasks = [self._SimulationClass(self._data, i, None) for i in range(self._options.dup)]
        if self._options.file_dump:
            for i in range(len(tasks)):
                tasks[i].set_output_file(output_base.format(self._options.output_file.format(i+1)))
        elif self._options.quiet:
            for i in range(len(tasks)):
                tasks[i].set_output_file(False)

        results = pool.imap_unordered(_run_simulation, tasks)
        finished_count = 0
        print >>stats, cPickle.dumps(self._options)
        print >>stats
        for result in results:
            finished_count += 1
            if not self._options.quiet:
                print self._format_run(result)
            print >>stats, cPickle.dumps(result)
            print >>stats
            stats.flush()
            if not self._options.quiet:
                print "done #{0}".format(finished_count)

        stats.close()
        return self._when_done()

    def _set_base_options(self):
        """ Set up the basic OptionParser options

        Options:
            -D | --nofiledump -- Do not dump individual simulation output
            -F | --filename -- Format string for file name of individual duplication output
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

class Simulation(object):

    """ Base class for an individual simulation

    Public Methods:
        run -- Runs the simulation
        set_output_file -- Sets the output file name
        
    Methods to Implement:
        _run -- Actual simulation functionality

    """

    def __init__(self, data, iteration, outfile):
        """ Sets up the simulation parameters

        Parameters:
            data -- The data object created by the SimulationBatch
            iteration -- The iteration number of the simulation
            outfile -- The name of a file to which to dump output (or None, indicating stdout)

        """

        self._data = data
        self._num = iteration
        self._outfile = outfile
        
        self._out = open(os.devnull, "w")
        self._out_opened = True
        self.result = None
        
    def set_output_file(self, fname):
        """ Sets the name of the outfile
        
        Parameters:
            fname -- The file name for the outfile (or None or False)
            
        """
        
        self._outfile = fname
        
    def _open_out_fd(self):
        """ Opens the self._out object that simulations should print to
        
        """
        
        if self._out_opened:
            self._close_out_fd()
            
        if self._outfile is None:
            self._out = sys.stdout
        elif self._outfile:
            self._out_opened = True
            self._out = open(self._outfile, "w")
        else:
            self._out_opened = True
            self._out = open(os.devnull, "w")
            
    def _close_out_fd(self):
        """ Closes the self._out object that simulations should print to
        
        """
        
        if self._out_opened:
            self._out.close()
            self._out_opened = False
            
        self._out = None

    def run(self):
        """ Runs the simulation. Handles opening and closing the self._out file object.
        
        """
        
        self._open_out_fd()
        self.result = self._run()
        self._close_out_fd()
        return self.result
    
    def _run(self):
        pass
