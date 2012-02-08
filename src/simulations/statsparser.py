""" Handle the parsing and aggregation of simulation results

Classes:

    :py:class:`StatsParser`
      main statistics parsing class

"""

import cPickle
import os
import sys

from simulations.base import Base
from simulations.base import withoptions


@withoptions
class StatsParser(Base):
    """ Base class for parsing result files.

    Keyword Parameters:

        option_error_handler
          An error handler for the :py:class:`~simulations.utils.optionparser.OptionParser`

        option_exit_handler
          An exit handler for the :py:class:`~simulations.utils.optionparser.OptionParser`

    Public Methods:

        :py:meth:`~StatsParser.go`
          Kick off parsing the results

    Methods to Implement:

        :py:meth:`~simulations.base.Base._add_listeners`
          Add listeners for various parsing events

    Events:

        done(this, out)
          emitted when results are totally done

        go(this)
          emitted when the :py:meth:`~StatsRunner.go` method is called

        oparser set up(this)
          emitted after the :py:class:`~simulations.utils.optionparser.OptionParser`
          is set up and able to add options

        options parsed(this)
          emitted after the :py:class:`~simulations.utils.optionparser.OptionParser`
          has parsed arguments

        result(this, out, duplication, result)
          emitted when a result is ready to be interpreted

        result options(this, out, options)
          emitted when the simulation runner options are ready to be interpreted

    """

    def __init__(self, *args, **kwdargs):
        """ Sets up the parsing aparatus

        Keyword Parameters:

            option_error_handler
              An error handler for the :py:class:`~simulations.utils.optionparser.OptionParser`

            option_exit_handler
              An exit handler for the :py:class:`~simulations.utils.optionparser.OptionParser`

        """

        super(StatsParser, self).__init__(*args, **kwdargs)

    def go(self, **kwdargs):
        """ Pass off the parsing of the results file after some data manipulation

        Keyword Parameters:

            option_args
              arguments to pass to the :py:class:`~simulations.utils.optionparser.OptionParser`.
              Defaults to sys.argv[1:].

            option_values
              target of option parsing (probably should not use)

        """

        self.emit('go', self)

        if 'option_args' in kwdargs:
            option_args = kwdargs['option_args']
        else:
            option_args = None

        if 'option_values' in kwdargs:
            option_values = kwdargs['option_values']
        else:
            option_values = None

        (self.options, self.args) = self.oparser.parse_args(args=option_args, values=option_values)

        self._check_base_options()
        self.emit('options parsed', self)

        with open(self.options.stats_file, "rb") as statsfile:
            if self.options.out_file:
                if self.options.verbose:
                    print "Sending output to {0}...".format(self.options.out_file)

                with open(self.options.out_file, "w") as out:
                    self._go(statsfile, out)
                    self.emit('done', self, out)
            else:
                if self.options.verbose:
                    print "Sending output to stdout..."

                self._go(statsfile, sys.stdout)
                self.emit('done', self, sys.stdout)

    def _go(self, statsfile, out):
        """ Actually parses the data

        Parameters:

            statsfile
              a file object for the file to parse

            out
              the output target (either a file object or sys.stdout)

        """

        count = -1
        pickle = ""

        if self.options.verbose:
            print "Beginning processing of stats file..."

        for line in statsfile:
            if line == "\n":
                if self.options.verbose:
                    print "Entry boundary encountered."

                count += 1

                if count == 0:
                    if self.options.verbose:
                        print "Delegating to _handle_result_options."
                    self.emit('result options',
                                self,
                                out,
                                cPickle.loads(pickle)
                             )
                else:
                    if self.options.verbose:
                        print "Delegating to _handle_result."
                    self.emit('result',
                                self,
                                out,
                                count,
                                cPickle.loads(pickle))

                pickle = ""

                if self.options.verbose:
                    print "Prepared for next entry."

            else:
                pickle += line

        if count < 1:
            raise ValueError("Stats file contained no duplication results")
        elif self.options.verbose:
            resstr = "Processing done. Entries for {0} duplications found."
            print resstr.format(count)

    def _set_base_options(self):
        """ Set up the basic :py:class:`~simulations.utils.optionparser.OptionParser` options

        Options:

        -F FILE, --statsfile=FILE       File name of the results file
        -O FILE, --outfile=FILE         File to which to print data
        -V, --verbose                   Print detailed output to stdout as things are processed

        """

        self.oparser.add_option("-F", "--statsfile", action="store",
                                        dest="stats_file",
                                        default="./output/aggregate",
                                        help="file holding aggregate stats")
        self.oparser.add_option("-O", "--outfile", action="store",
                                        dest="out_file", default=None,
                                        help="file to which to print data")
        self.oparser.add_option("-V", "--verbose", action="store_true",
                                        dest="verbose", default=False,
                                        help="detailed output?")

    def _check_base_options(self):
        """ Verify the values passed to the base options

        Checks:

            - Stats file exists

        """

        file_exists = os.path.isfile(self.options.stats_file)
        if not self.options.stats_file or not file_exists:
            self.oparser.error("The stats file specified does not exist")
