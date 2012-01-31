""" Handle the parsing and aggregation of simulation results

Classes:
    
    StatsParser
      main statistics parsing class

"""

import cPickle
import os
import sys

from simulations.utils.eventemitter import EventEmitter
from simulations.utils.optionparser import OptionParser

class StatsParser(EventEmitter):
    """ Base class for parsing result files.
    
    Public Methods:
        
        go
          Kick off parsing the results
        
    Methods to Implement:
        
        _add_listeners
          Add listeners for various parsing events
        
    Events (all handlers are called with self as the first parameter):
        
        done
          emitted when results are totally done (replaces _when_done)
          
        go
          emitted when the go method is called
        
        oparser set up
          emitted after the OptionParser is set up and able to add options
          
        options parsed
          emitted after the OptionParser has parsed arguments
        
        result
          emitted for a result with parameters (self, out, duplication, result)
        
        result options
          emitted for the result options with parameters (self, out, options) 
        
    """

    def __init__(self, **kwdargs):
        """ Sets up the parsing aparatus
        
        Keyword Parameters:
            
            option_error_handler
              An error handler for the option parser
            
            option_exit_handler
              An exit handler for the option parser
        
        """
        
        EventEmitter.__init__(self)
        
        self.options = None
        self._args = None
        
        self._add_listeners()

        self.oparser = OptionParser()
        self._set_base_options()
        
        if 'option_error_handler' in kwdargs:
            self.oparser.set_error_handler(kwdargs['option_error_handler'])
    
        if 'option_exit_handler' in kwdargs:
            self.oparser.set_exit_handler(kwdargs['option_exit_handler'])
        
        self.emit('oparser set up', self)
        
    def go(self, option_args=None, option_values=None):
        """ Pass off the parsing of the results file after some data manipulation
        
        Parameters:
            
            option_args
              arguments to pass to the option parser. Defaults to sys.argv[1:].
            
            option_values
              target of option parsing (probably should not use)
        
        """

        self.emit('go', self)
        
        (self.options, self._args) = self.oparser.parse_args(args=option_args, values=option_values)

        self._check_base_options()
        self.emit('options parsed', self)        
        
        with open(self.options.stats_file, "rb") as statsfile:
            if self.options.out_file:
                if self.options.verbose:
                    print "Sending output to {0}...".format(self.options.out_file)
                
                with open(self.options.out_file, "w") as out:
                    self._go(statsfile, out)
                    if self.options.verbose:
                        print "Executing _when_done handler..."
                    
                    self.emit('done', self, out)
            else:
                if self.options.verbose:
                    print "Sending output to stdout..."
                
                self._go(statsfile, sys.stdout)
                if self.options.verbose:
                    print "Executing _when_done handler..."
            
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
                    self.emit('result options', self, out, cPickle.loads(pickle))
                else:
                    if self.options.verbose:
                        print "Delegating to _handle_result."
                    self.emit('result', self, out, count, cPickle.loads(pickle))
                
                pickle = ""
                
                if self.options.verbose:
                    print "Prepared for next entry."
                
            else:
                pickle += line
        
        if count < 1:
            raise ValueError("Stats file contained no duplication results")
        elif self.options.verbose:
            print "Processing done. Entries for {0} duplications found.".format(count)
        
    def _set_base_options(self):
        """ Set up the basic OptionParser options

        Options:
            
            -F | --statsfile=file       File name of the results file
            -O | --outfile=file         File to which to print data
            -V | --verbose              Print detailed output to stdout as things are processed

        """

        self.oparser.add_option("-F", "--statsfile", action="store", dest="stats_file", default="./output/aggregate", help="file holding aggregate stats to be parsed")
        self.oparser.add_option("-O", "--outfile", action="store", dest="out_file", default=None, help="file to which to print data")
        self.oparser.add_option("-V", "--verbose", action="store_true", dest="verbose", default=False, help="detailed output?")

    def _check_base_options(self):
        """ Verify the values passed to the base options
        
        Checks:

            - Stats file exists

        """

        if not self.options.stats_file or not os.path.isfile(self.options.stats_file):
            self.oparser.error("The stats file specified does not exist")
            
    def _add_listeners(self):
        """ Set up listeners for various events (should implement)
        
        """
        
        pass
            
