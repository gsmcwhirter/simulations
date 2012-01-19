""" Handle the basics of running parallel simulations

Classes:
    Simulation -- Framework for a basic simulation
    SimulationBatch -- Handles option parsing and a multiprocessing pool for simulations

"""

import cPickle
import multiprocessing as mp
import os
import sys

from gametheory.base.eventemitter import EventEmitter
from gametheory.base.optionparser import OptionParser

def _run_simulation(task):
    """ A simple function to run the simulation. Used with the multiprocessing pool.
    
    """
    
    klass = task.pop(0)
    sim = klass(*task)
    
    return sim.run()

class SimulationBatch(EventEmitter):

    """ Handles option parsing and a multiprocessing pool for simulations

    Public Methods:
        go -- Kick off the batch of simulations

    Methods to Implement:
        _add_listeners -- Set up event listeners for run events
        
    Events (all handlers are called with self as the first parameter):
        done -- emitted when results are totally done (replaces _when_done)
        go -- emitted when the go method is called
        made output_dir -- emitted if/when the output directory needs to be created
        oparser set up -- emitted after the OptionParser is set up and able to add options
        options parsed -- emitted after the OptionParser has parsed arguments
        pool started -- emitted after the multiprocessing pool is set up
        result -- emitted when a result is complete (passes self and the result as parameters)
        start -- emitted just before the pool imap_unordered is called

    """

    def __init__(self, SimulationClass, *args, **kwdargs):
        """ Set up the simulation batch handler

        Parameters:
            SimulationClass -- The class representing the simulation to run
        
        Keyword Parameters:
            option_error_handler -- An error handler for the option parser
            option_exit_handler -- An exit handler for the option parser

        """
        
        super(SimulationBatch, self).__init__()
        
        self._options = None
        self._args = None
        self._data = {}
        self._task_dup_num = False
        self._SimulationClass = SimulationClass
        
        self.on('oparser set up', self._set_base_options)
        self.on('options parsed', self._check_base_options)
        self.on('pool started', self._default_pool_started_handler)
        self.on('start', self._default_start_handler)
        self.on('result', self._default_result_handler)
        
        self._add_listeners()

        self._oparser = OptionParser()
        
        try:
            self._oparser.set_error_handler(kwdargs['option_error_handler'])
        except KeyError:
            pass
    
        try:
            self._oparser.set_exit_handler(kwdargs['option_exit_handler'])
        except KeyError:
            pass
    
        self.emit('oparser set up', self)

    def go(self, option_args=None, option_values=None):
        """ Verify options and run the batch of simulations
        
        Parameters:
            option_args -- arguments to pass to the option parser. Defaults to sys.argv[1:].
            option_values -- target of option parsing (probably should not use)
            
        """

        self.emit('go', self)

        (self._options, self._args) = self._oparser.parse_args(args=option_args, values=option_values)
        
        self.emit('options parsed', self)
        
        if not os.path.isdir(self._options.output_dir):
            self.emit('made output_dir', self)
            os.makedirs(self._options.output_dir, 0755)

        output_base = ("{0}" + os.sep + "{1}").format(self._options.output_dir, "{0}")

        stats = open(output_base.format(self._options.stats_file), "wb")

        mplog = mp.log_to_stderr()
        mplog.setLevel(mp.SUBWARNING)

        pool = mp.Pool(self._options.pool_size)
        self.emit('pool started', self, pool)

        tasks = [[self._SimulationClass, self._data, i, None] for i in range(self._options.dup)]
        if self._options.file_dump:
            for i in range(len(tasks)):
                tasks[i][3] = output_base.format(self._options.output_file.format(i+1))
        elif self._options.quiet:
            for i in range(len(tasks)):
                tasks[i][3] = False
                
        self.emit('start', self)

        results = pool.imap_unordered(_run_simulation, tasks)
        self.finished_count = 0
        print >>stats, cPickle.dumps(self._options)
        print >>stats
        for result in results:
            print >>stats, cPickle.dumps(result)
            print >>stats
            stats.flush()
    
            self.emit('result', self, result)

        stats.close()
        self.emit('done', self)

    @staticmethod
    def _set_base_options(this):
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

        this._oparser.add_option("-N", "--duplications", type="int", action="store", dest="dup", default=1, help="number of duplications")
        this._oparser.add_option("-O", "--output", action="store", dest="output_dir", default="./output", help="directory to dump output files")
        this._oparser.add_option("-F", "--filename", action="store", dest="output_file", default="duplication_{0}", help="output file name template")
        this._oparser.add_option("-D", "--nofiledump", action="store_false", dest="file_dump", default=True, help="do not output duplication files")
        this._oparser.add_option("-S", "--statsfile", action="store", dest="stats_file", default="aggregate", help="file for aggregate stats to be dumped")
        this._oparser.add_option("-P", "--poolsize", action="store", type="int", dest="pool_size", default=2, help="number of parallel computations to undertake")
        this._oparser.add_option("-Q", "--quiet", action="store_true", dest="quiet", default=False, help="suppress standard output")

    @staticmethod
    def _check_base_options(this):
        """ Verify the values passed to the base options

        Checks:
            - Number of duplications is positive

        """

        if not this._options.dup or this._options.dup <= 0:
            this._oparser.error("Number of duplications must be positive")
    
    @staticmethod
    def _default_result_handler(this, result):
        """ Default handler for the 'result' event
        
        Parameters:
            result -- the result object
        
        """
        
        this.finished_count += 1
        if not this._options.quiet:
            print result
            print "done #{0}".format(this.finished_count)
            
    @staticmethod
    def _default_pool_started_handler(this, pool):
        """ Default handler for the 'pool started' event
        
        Parameters:
            pool -- the pool that was started
        
        """
        
        if not this._options.quiet:
            print "Pool Started: {0} workers".format(this._options.pool_size)
            
    @staticmethod
    def _default_start_handler(this):
        """ Default handler for the 'start' event
        
        """
        
        if not this._options.quiet:
            print "Running {0} duplications.".format(this._options.dup)
    
    def _add_listeners(self):
        """ Set up listeners for various events (should implement)
        
        """
        
        pass

class Simulation(EventEmitter):

    """ Base class for an individual simulation

    Public Methods:
        run -- Runs the simulation
        set_output_file -- Sets the output file name
        
    Methods to Implement:
        _add_listeners -- Set up listeners for various simulation events
        _run -- Actual simulation functionality
        
    Events (all handlers are called with self as the first parameter):
        done -- emitted when the run is complete and results have been stored
        outfile changed -- emitted when the outfile name has been changed by set_output_file
        outfile error -- emitted when there was an error opening the output file
        run -- emitted just before _run is called

    """

    def __init__(self, data, iteration, outfile):
        """ Sets up the simulation parameters

        Parameters:
            data -- The data object created by the SimulationBatch
            iteration -- The iteration number of the simulation
            outfile -- The name of a file to which to dump output (or None, indicating stdout)

        """
        
        super(Simulation, self).__init__()

        self._data = data
        self._num = iteration
        self._outfile = None
        self._out = None
        self._out_opened = False
        self.result = None
        
        self.on('run', self._open_out_fd)
        self.on('done', self._close_out_fd)
        self.on('outfile changed', self._open_out_fd)
        
        self._add_listeners()
        
        self.set_output_file(outfile)
        
    def set_output_file(self, fname):
        """ Sets the name of the outfile
        
        Parameters:
            fname -- The file name for the outfile (or None or False)
            
        """
        
        self._outfile = fname
        self.emit('outfile changed', self)
        
    @staticmethod
    def _open_out_fd(this):
        """ Opens the self._out object that simulations should print to
        
        """
        
        if this._out_opened:
            this._close_out_fd(this)
            
        if this._outfile is None:
            this._out = sys.stdout
        elif this._outfile:
            this._out = open(this._outfile, "w")
            this._out_opened = True
        else:
            this._out_opened = True
            this._out = open(os.devnull, "w")
            
    @staticmethod
    def _close_out_fd(this):
        """ Closes the self._out object that simulations should print to
        
        """
        
        if this._out_opened:
            this._out.close()
            this._out_opened = False
            
        this._out = None

    def run(self):
        """ Runs the simulation. Handles opening and closing the self._out file object.
        
        """
        
        self.emit('run', self)
        self.result = self._run()
        self.emit('done', self)
        return self.result
    
    def _add_listeners(self):
        """ Set up listeners for various events (should implement)
        
        """
        
        pass
    
    def _run(self):
        """ Actual functionality for running the simulation (should implement)
        
        """
        pass
