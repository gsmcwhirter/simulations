""" Handler for running simulations in a multiprocessing environment

Classes:

    SimulationRunner
      Handles option parsing and a pp server pool for simulations

Functions:

    default_pool_started_handler
      Default handler for 'pool started' events

    default_start_handler
      Default handler for 'start' events

    default_result_handler
      Default handler for 'result' events

    run_simulation
      runs a simulation task

"""

import cPickle
import os
import pp
import sys

from simulations.utils.eventemitter import EventEmitter
from simulations.utils.fake_server import Server as FakeServer
from simulations.utils.optionparser import OptionParser
from simulations.utils.functions import random_string


class SimulationRunner(EventEmitter):
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
          emitted when a result is complete (passes self and the result as
          parameters)

        start
          emitted just before the pool imap_unordered is called

    """

    def __init__(self, simulation_class, *args, **kwdargs):
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

        EventEmitter.__init__(self)

        self.options = None
        self.args = None
        self.data = {}
        self._task_dup_num = False
        self._simulation_class = simulation_class
        self.finished_count = 0
        self.identifier = random_string()

        if 'default_handlers' not in kwdargs or kwdargs['default_handlers']:
            self.on('pool started', default_pool_handler)
            self.on('start', default_start_handler)
            self.on('result', default_result_handler)

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

        (self.options, self.args) = self.oparser.parse_args(
                                        args=option_args,
                                        values=option_values
                                    )

        self._check_base_options()
        self.emit('options parsed', self)

        if not os.path.isdir(self.options.output_dir):
            self.emit('made output_dir', self)
            os.makedirs(self.options.output_dir, 0755)

        output_base = ("{0}" + os.sep + "{1}").format(
                                                self.options.output_dir, "{0}"
                                                )

        stats = open(output_base.format(self.options.stats_file), "wb")

        serverlist = ()

        if self.options.cluster_string:
            serverlist = tuple(self.options.cluster_string.split(","))

        if len(serverlist) > 1 or self.options.pool_size > 1:
            pool = pp.Server(self.options.pool_size,
                                ppservers=serverlist,
                                secret=self.options.cluster_secret)
        else:
            pool = FakeServer(self.options.pool_size,
                                      ppservers=serverlist,
                                      secret=self.options.cluster_secret)

        self.emit('pool started', self, pool)

        tasks = [[self._simulation_class, self.data, i, None]
                    for i in range(self.options.dup)]
        if self.options.file_dump:
            for i in range(len(tasks)):
                tasks[i][3] = output_base.format(
                    self.options.output_file.format(
                        i + 1
                    )
                )
        elif self.options.quiet:
            for i in range(len(tasks)):
                tasks[i][3] = False

        self.emit('start', self)

        def finish_run(this, out, result):
            """ The pp task callback to handle finished simulations

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

            job_template = pp.Template(pool, run_simulation,
                                             callback=finish_run,
                                             callbackargs=(self, stats),
                                             group=self.identifier)

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

            -D | --nofiledump           Do not dump individual simulation
                                            output
            -F | --filename=file        Format string for file name of
                                            individual duplication output
            -N | --duplications=num     Number of trials to run
            -O | --output=dir           Directory to which to output the
                                            results
            -P | --poolsize=num         Number of simultaneous trials
            -Q | --quiet                Suppress all output except aggregate
                                            pickle dump
            -S | --statsfile=file       File name for aggregate, pickled output
            --cluster                   List of cluster servers to use via
                                            parallelpython
            --clustersecret             Password to access the cluster servers

        """

        self.oparser.add_option("-N", "--duplications", type="int",
                                    action="store", dest="dup", default=1,
                                    help="number of duplications")
        self.oparser.add_option("-O", "--output", action="store",
                                    dest="output_dir", default="./output",
                                    help="directory to dump output files")
        self.oparser.add_option("-F", "--filename", action="store",
                                    dest="output_file",
                                    default="duplication_{0}",
                                    help="output file name template")
        self.oparser.add_option("-D", "--nofiledump", action="store_false",
                                    dest="file_dump", default=True,
                                    help="do not output duplication files")
        self.oparser.add_option("-S", "--statsfile", action="store",
                                    dest="stats_file", default="aggregate",
                                    help="file for aggregate stats")
        self.oparser.add_option("-P", "--poolsize", action="store", type="int",
                                    dest="pool_size", default=None,
                                    help="number of parallel computations")
        self.oparser.add_option("-Q", "--quiet", action="store_true",
                                    dest="quiet", default=False,
                                    help="suppress standard output")
        self.oparser.add_option("--cluster", action="store", type="string",
                                    dest="cluster_string", default=None,
                                    help="list of cluster servers")
        self.oparser.add_option("--clustersecret", action="store",
                                    type="string", dest="cluster_secret",
                                    default=None,
                                    help="password for the cluster")

    def _check_base_options(self):
        """ Verify the values passed to the base options

        Checks:

            - Number of duplications is positive

        """

        if not self.options.dup or self.options.dup <= 0:
            self.oparser.error("Number of duplications must be positive")

        if self.options.pool_size is None:
            self.options.pool_size = 'autodetect'
        elif self.options.pool_size < 0:
            self.oparser.error("Pool size must be non-negative")

    def _add_listeners(self):
        """ Set up listeners for various events (should implement)

        """

        pass


def run_simulation(task):
    """ A simple function to run the simulation. Used with the pp server.

    Parameters:

        task
          a list/tuple whose first element is a Simulation class and the rest
          of whose elements are parameters for __init__

    """

    klass = task.pop(0)
    sim = klass(*task)

    return sim.run()


def default_result_handler(this, result, out=None):
    """ Default handler for the 'result' event

    Parameters:

        this
          a reference to the simulation batch

        result
          the result object

        out
          the file descriptor to print to

    """

    if out is None:
        out = sys.stdout

    if not this.options.quiet:
        print >> out, result
        print >> out, "done #{0}".format(this.finished_count)


def default_pool_handler(this, pool, out=None):
    """ Default handler for the 'pool started' event

    Parameters:

        this
          a reference to the simulation batch

        pool
          the pool that was started

        out
          the file descriptor to print to

    """

    if out is None:
        out = sys.stdout

    if not this.options.quiet:
        print >> out, "Pool Started: {0} workers".format(pool.get_ncpus())


def default_start_handler(this, out=None):
    """ Default handler for the 'start' event

    Parameters:

        this
          a reference to the simulation batch

        out
          the file descriptor to print to

    """

    if out is None:
        out = sys.stdout

    if not this.options.quiet:
        print >> out, "Running {0} duplications.".format(this.options.dup)