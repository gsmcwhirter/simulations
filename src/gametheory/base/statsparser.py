""" Handle the parsing and aggregation of simulation results

Classes:
    StatsParser -- main statistics parsing class

"""

import cPickle
import os
import sys

from gametheory.base.optionparser import OptionParser

class StatsParser:
    """ Base class for parsing result files.
    
    Public Methods:
        go -- Kick off parsing the results
        
    Methods to Implement:
        _set_options 
        _set_options -- Set OptionParser options specific to the simulation
        _check_options -- Verify OptionParser options specific to the simulation
        _handle_result_options -- Handle the options dumped at the top of the results file
        _handle_result -- Handle the results from a single duplication
        _when_done -- Clean up after all simulations are complete (optional)
        
    """

    def __init__(self, *args, **kwdargs):
        """ Sets up the parsing aparatus
        
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
        self._set_base_options()
        self._set_options()
        
    def go(self, option_args=None, option_values=None):
        """ Pass off the parsing of the results file after some data manipulation
        
        Parameters:
            option_args -- arguments to pass to the option parser. Defaults to sys.argv[1:].
            option_values -- target of option parsing (probably should not use)
        
        """
        
        (self._options, self._args) = self._oparser.parse_args(args=option_args, values=option_values)
        self._check_base_options()
        self._check_options()
        
        #do stuff
        with open(self._options.stats_file, "rb") as statsfile:
            if self._options.out_file:
                if self._options.verbose:
                    print "Sending output to {0}...".format(self._options.out_file)
                
                with open(self._options.out_file, "w") as out:
                    self._go(statsfile, out)
            else:
                if self._options.verbose:
                    print "Sending output to stdout..."
                
                self._go(statsfile, sys.stdout)
        
        if self._options.verbose:
            print "Executing _when_done handler..."
            
        return self._when_done()
        
    def _go(self, statsfile, out):
        """ Actually parses the data
        
        Parameters:
            statsfile -- a file object for the file to parse
            out -- the output target (either a file object or sys.stdout)
        
        """
        
        count = -1
        pickle = ""
        
        if self._options.verbose:
            print "Beginning processing of stats file..."
        
        for line in statsfile:
            if line == "\n":
                if self._options.verbose:
                    print "Entry boundary encountered."
                
                count += 1
                
                if count == 0:
                    if self._options.verbose:
                        print "Delegating to _handle_result_options."
                    self._handle_result_options(out, cPickle.loads(pickle))
                else:
                    if self._options.verbose:
                        print "Delegating to _handle_result."
                    self._handle_result(out, count, cPickle.loads(pickle))
                
                pickle = ""
                
                if self._options.verbose:
                    print "Prepared for next entry."
                
            else:
                pickle += line
        
        if count < 1:
            raise ValueError("Stats file contained no duplication results")
        elif self._options.verbose:
            print "Processing done. Entries for {0} duplications found.".format(count)
        
    def _set_base_options(self):
        """ Set up the basic OptionParser options

        Options:
            -F | --statsfile -- File name of the results file
            -O | --outfile -- File to which to print data
            -V | --verbose -- Print detailed output to stdout as things are processed

        """

        self._oparser.add_option("-F", "--statsfile", action="store", dest="stats_file", default="./output/aggregate", help="file holding aggregate stats to be parsed")
        self._oparser.add_option("-O", "--outfile", action="store", dest="out_file", default=None, help="file to which to print data")
        self._oparser.add_option("-V", "--verbose", action="store_true", dest="verbose", default=False, help="detailed output?")

    def _check_base_options(self):
        """ Verify the values passed to the base options

        Checks:
            - Stats file exists

        """

        if not self._options.stats_file or not os.path.isfile(self._options.stats_file):
            self._oparser.error("The stats file specified does not exist")
            
    def _set_options(self):
        """ Set options on the optionparser (should implement)
        
        """
        
        pass

    def _check_options(self):
        """ Check options on the optionparser are valid (should implement)
        
        """
        
        pass

    def _handle_result_options(self, out, options):
        """ Do things with the options from the run of duplications (should implement)
        
        Parameters:
            out -- The target of any printed output (for print >>out, "stuff")
            options -- The options data structure
        
        """
        
        pass
    
    def _handle_result(self, out, dup_num, dup_data):
        """ Do things with a duplication result (should implement)
        
        Parameters:
            out -- The target of any printed output (for print >>out, "stuff")
            dup_num -- The number of the duplication (indexed from 1)
            dup_data -- The duplication result data
        
        """
        
        pass

    def _when_done(self):
        """ Do things after all duplications are done (optional to implement)
        
        """
        
        pass
