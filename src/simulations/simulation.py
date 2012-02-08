""" Handle the basics of running parallel simulations

Classes:

    :py:class:`~simulations.simulation.Simulation`
      Framework for a basic simulation

"""

import os
import sys

from simulations.base import Base
from simulations.base import listener


def _close_out_fd(this):
    """ Closes the :py:attr:`Simulation.out` object that simulations should print to

    Parameters:

        this
          A reference to a :py:class:`Simulation` instance

    """

    if this.out_opened:
        this.out.close()
        this.out_opened = False

    this.out = None


def _open_out_fd(this):
    """ Opens the :py:attr:`Simulation.out` object that simulations should print to

    Parameters:

        this
          A reference to a :py:class:`Simulation` instance

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

    Parameters:

        data
          The data dictionary for the simulation. Usually created by the
          :py:class:`~simulations.simulation_runner.SimulationRunner`

        iteration
          The iteration number of the simulation. Usually handled by the
          :py:class:`~simulations.simulation_runner.SimulationRunner`

        outfile
          The name of a file to which to dump output (or None, indicating
          stdout)

    Public Methods:

        :py:meth:`run`
          Runs the simulation

        :py:meth:`set_output_file`
          Sets the output file name

    Methods to Implement:

        :py:meth:`~simulations.base.Base._add_listeners`
          Set up listeners for various simulation events

        :py:meth:`~Simulation._run`
          Actual simulation functionality

    Events:

        done(this)
          emitted when :py:meth:`~Simulation.run` is complete and results have been stored

        outfile changed(this)
          emitted when the outfile name has been changed by :py:meth:`~Simulation.set_output_file`

        outfile error(this)
          emitted when there was an error opening the output file

        run(this)
          emitted just before :py:meth:`~Simulation._run` is called

    """

    def __init__(self, data, iteration, outfile, *args, **kwdargs):
        """ Sets up the simulation parameters

        Parameters:

            data
              The data dictionary for the simulation. Usually created by the
              :py:class:`~simulations.simulation_runner.SimulationRunner`

            iteration
              The iteration number of the simulation. Usually handled by the
              :py:class:`~simulations.simulation_runner.SimulationRunner`

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
        """ Runs the simulation. Handles opening and closing the :py:attr:`~Simulation.out` file
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
