""" Handle the basics of running parallel simulations

Classes:

    Simulation
      Framework for a basic simulation

"""

import os
import sys

from simulations.base import Base
from simulations.base import listener


def _close_out_fd(this):
    """ Closes the self._out object that simulations should print to

    """

    if this.out_opened:
        this.out.close()
        this.out_opened = False

    this.out = None


def _open_out_fd(this):
    """ Opens the self._out object that simulations should print to

    """

    if this.out_opened:
        _close_out_fd(this)

    if this.is_running:
        if this.outfile is None:
            this.out = sys.stdout
        elif this.outfile:
            this.out = open(this.outfile, "w")
            this.out_opened = True
        else:
            this.out_opened = True
            this.out = open(os.devnull, "w")


@listener('run', _open_out_fd)
@listener('done', _close_out_fd)
@listener('outfile changed', _open_out_fd)
class Simulation(Base):
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
              The name of a file to which to dump output (or None, indicating
              stdout)

        """

        super(Simulation, self).__init__(*args, **kwdargs)

        self.data = data
        self.num = iteration
        self.outfile = None
        self.out = None
        self.out_opened = False
        self.result = None
        self.is_running = False

        self.set_output_file(outfile)

    def set_output_file(self, fname):
        """ Sets the name of the outfile

        Parameters:

            fname
              The file name for the outfile (or None or False)

        """

        self.outfile = fname
        self.emit('outfile changed', self)

    def run(self):
        """ Runs the simulation. Handles opening and closing the self.out file
            object.

        """

        self.is_running = True
        self.emit('run', self)
        self.result = self._run()
        self.emit('done', self)
        return self.result

    def _run(self, *args, **kwdargs):
        """ Actual functionality for running the simulation (should implement)

        """
        pass
