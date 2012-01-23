""" Handle the basics of running parallel simulations

Classes:
    
    Simulation
      Framework for a basic simulation
    
    SimulationBatch
      Handles option parsing and a multiprocessing pool for simulations

"""

import cPickle
import gametheory.base.simulation_runner as simrunner
import os
import pp
import sys

from gametheory.base.eventemitter import EventEmitter
from gametheory.base.handlers import simbatch_default_result_handler
from gametheory.base.handlers import simbatch_default_pool_handler
from gametheory.base.handlers import simbatch_default_start_handler
from gametheory.base.optionparser import OptionParser
from gametheory.base.util import random_string

class SimulationBatch(EventEmitter):
    """ Handles option parsing and a multiprocessing pool for simulations

    Public Methods:
        
        go
          Kick off the batch of simulations

    Methods to Implement:
        
        _add_listeners
          Set up event listeners for run events
        
    Events (all handlers are called with self as the first parameter):
        
        done
          emitted when results are totally done (replaces _when_done)
        
        go
          emitted when the go method is called
        
        made output_dir
          emitted if/when the output directory needs to be created
        
        oparser set up
          emitted after the OptionParser is set up and able to add options
        
        options parsed
          emitted after the OptionParser has parsed arguments
        
        pool started
          emitted after the multiprocessing pool is set up
        
        result
          emitted when a result is complete (passes self and the result as parameters)
        
        start
          emitted just before the pool imap_unordered is called

    """

    def __init__(self, simulation_class, default_handlers=True, **kwdargs):
        """ Set up the simulation batch handler

        Parameters:
            
            simulation_class
              The class representing the simulation to run
            
            default_handlers
              Flag to set default event handlers for some events (default True)
        
        Keyword Parameters:
            
            option_error_handler
              An error handler for the option parser
            
            option_exit_handler
              An exit handler for the option parser

        """
        
        super(SimulationBatch, self).__init__()
        
        self.options = None
        self.args = None
        self.data = {}
        self._task_dup_num = False
        self._simulation_class = simulation_class
        self.finished_count = 0
        self.identifier = random_string()
        
        if default_handlers: 
            self.on('pool started', simbatch_default_pool_handler)
            self.on('start', simbatch_default_start_handler)
            self.on('result', simbatch_default_result_handler)
        
        self._add_listeners()

        self.oparser = OptionParser()
        
        if 'option_error_handler' in kwdargs:
            self.oparser.set_error_handler(kwdargs['option_error_handler'])
    
        if 'option_exit_handler' in kwdargs:
            self.oparser.set_exit_handler(kwdargs['option_exit_handler'])
    
        self._set_base_options()
        self.emit('oparser set up', self)

    def go(self, option_args=None, option_values=None):
        """ Verify options and run the batch of simulations
        
        Parameters:
            
            option_args
              arguments to pass to the option parser. Defaults to sys.argv[1:].
            
            option_values
              target of option parsing (probably should not use)
            
        """

        self.emit('go', self)

        (self.options, self.args) = self.oparser.parse_args(args=option_args, values=option_values)
        
        self._check_base_options()
        self.emit('options parsed', self)
        
        if not os.path.isdir(self.options.output_dir):
            self.emit('made output_dir', self)
            os.makedirs(self.options.output_dir, 0755)

        output_base = ("{0}" + os.sep + "{1}").format(self.options.output_dir, "{0}")

        stats = open(output_base.format(self.options.stats_file), "wb")
        
        serverlist = ()
        if self.options.cluster_string:
            serverlist = tuple(self.options.cluster_string.split(","))
        pool = pp.Server(ppservers=serverlist, secret=self.options.cluster_secret)

        self.emit('pool started', self, pool)

        tasks = [[self._simulation_class, self.data, i, None] for i in range(self.options.dup)]
        if self.options.file_dump:
            for i in range(len(tasks)):
                tasks[i][3] = output_base.format(self.options.output_file.format(i+1))
        elif self.options.quiet:
            for i in range(len(tasks)):
                tasks[i][3] = False
                
        self.emit('start', self)
        
        def finish_run(this, out, result):
            """ The pp task callback to handle finished simulations as they come in
            
            Parameters:
                
                this
                  a reference to self
                
                out
                  the file-like object to which to print data
                
                result
                  the result object returned by the simulation
            
            """
            
            print >> out, cPickle.dumps(result)
            print >> out
            out.flush() 
            this.finished_count += 1
            
            this.emit('result', this, result)

        try:
            print >> stats, cPickle.dumps(self.options)
            print >> stats
            
            job_template = pp.Template(pool, simrunner.run_simulation, callback=finish_run, callbackargs=(self, stats), group=self.identifier)
            
            for task in tasks:
                job_template.submit(task)
            
            pool.wait(self.identifier)
        except KeyboardInterrupt:
            pool.destroy()
            print "caught KeyboardInterrupt"
            sys.exit(1)

        stats.close()
        self.emit('done', self)

    def _set_base_options(self):
        """ Set up the basic OptionParser options

        Options:
            
            -D | --nofiledump           Do not dump individual simulation output
            -F | --filename=file        Format string for file name of individual duplication output
            -N | --duplications=num     Number of trials to run
            -O | --output=dir           Directory to which to output the results
            -P | --poolsize=num         Number of simultaneous trials
            -Q | --quiet                Suppress all output except aggregate pickle dump
            -S | --statsfile=file       File name for aggregate, pickled output
            --cluster                   List of cluster servers to use via parallelpython
            --clustersecret             Password to access the cluster servers

        """

        self.oparser.add_option("-N", "--duplications", type="int", action="store", dest="dup", default=1, help="number of duplications")
        self.oparser.add_option("-O", "--output", action="store", dest="output_dir", default="./output", help="directory to dump output files")
        self.oparser.add_option("-F", "--filename", action="store", dest="output_file", default="duplication_{0}", help="output file name template")
        self.oparser.add_option("-D", "--nofiledump", action="store_false", dest="file_dump", default=True, help="do not output duplication files")
        self.oparser.add_option("-S", "--statsfile", action="store", dest="stats_file", default="aggregate", help="file for aggregate stats to be dumped")
        self.oparser.add_option("-P", "--poolsize", action="store", type="int", dest="pool_size", default=2, help="number of parallel computations to undertake")
        self.oparser.add_option("-Q", "--quiet", action="store_true", dest="quiet", default=False, help="suppress standard output")
        self.oparser.add_option("--cluster", action="store", type="string", dest="cluster_string", default=None, help="list of cluster servers")
        self.oparser.add_option("--clustersecret", action="store", type="string", dest="cluster_secret", default=None, help="password for the cluster")

    def _check_base_options(self):
        """ Verify the values passed to the base options

        Checks:
            
            - Number of duplications is positive

        """

        if not self.options.dup or self.options.dup <= 0:
            self.oparser.error("Number of duplications must be positive")
    
    def _add_listeners(self):
        """ Set up listeners for various events (should implement)
        
        """
        
        pass

class Simulation(EventEmitter):
    """ Base class for an individual simulation

    Public Methods:
        
        run
          Runs the simulation
        
        set_output_file
          Sets the output file name
        
    Methods to Implement:
        
        _add_listeners
          Set up listeners for various simulation events
        
        _run
          Actual simulation functionality
        
    Events (all handlers are called with self as the first parameter):
        
        done 
          emitted when the run is complete and results have been stored
        
        outfile changed
          emitted when the outfile name has been changed by set_output_file
        
        outfile error
          emitted when there was an error opening the output file
        
        run 
          emitted just before _run is called

    """

    def __init__(self, data, iteration, outfile, *args, **kwdargs):
        """ Sets up the simulation parameters

        Parameters:
            
            data
              The data object created by the SimulationBatch
            
            iteration
              The iteration number of the simulation
            
            outfile
              The name of a file to which to dump output (or None, indicating stdout)

        """
        
        super(Simulation, self).__init__()

        self.data = data
        self.num = iteration
        self.outfile = None
        self.out = None
        self.out_opened = False
        self.result = None
        
        self.on('run', self.open_out_fd)
        self.on('done', self.close_out_fd)
        self.on('outfile changed', self.open_out_fd)
        
        self._add_listeners()
        
        self.set_output_file(outfile)
        
    def set_output_file(self, fname):
        """ Sets the name of the outfile
        
        Parameters:
            
            fname
              The file name for the outfile (or None or False)
            
        """
        
        self.outfile = fname
        self.emit('outfile changed', self)
        
    @staticmethod
    def open_out_fd(this):
        """ Opens the self._out object that simulations should print to
        
        """
        
        if this.out_opened:
            this.close_out_fd(this)
            
        if this.outfile is None:
            this.out = sys.stdout
        elif this.outfile:
            this.out = open(this.outfile, "w")
            this.out_opened = True
        else:
            this.out_opened = True
            this.out = open(os.devnull, "w")
            
    @staticmethod
    def close_out_fd(this):
        """ Closes the self._out object that simulations should print to
        
        """
        
        if this.out_opened:
            this.out.close()
            this.out_opened = False
            
        this.out = None

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
