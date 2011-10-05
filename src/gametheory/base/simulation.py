__author__="gmcwhirt"
__date__ ="$Sep 27, 2011 4:23:03 PM$"

import cPickle
import multiprocessing as mp

from contextlib import contextmanager
from optparse import OptionParser

effective_zero_diff = 1e-11
effective_zero = 1e-10


class Simulation:

    def __init__(self, runSimulation):
        self._oparser = OptionParser()
        self._options = None
        self._args = None
        self._data = {}
        self._task_dup_num = False
        self.__setBaseParserOptions()
        self._setParserOptions()
        self._runSimulation = runSimulation

    @contextmanager
    def __mpPool(self, size, quiet):
        try:
            pool = mp.Pool(size)
            if not quiet:
                print "Pool Started: {0}".format(pool)
            yield pool
        finally:
            pool.close()
            pool.terminate()
            print "Terminated by Interrupt!"


    def go(self):
        (self._options, self._args) = self._oparser.parse_args()
        self.__checkBaseParserOptions()
        self._checkParserOptions()
        self._setData()

        output_base = "{0}/{1}".format(self._options.output_dir, "{0}")

        stats = open(output_base.format(self._options.stats_file), "wb")

        with self.__mpPool(self._options.pool_size, self._options.quiet) as pool:

            mp.log_to_stderr()

            if not self._options.quiet:
                print "Running {0} duplications.".format(self._options.dup)

            task_base = self._buildTask()
            task_extras = [self._options.skip, self._options.quiet]

            if self._task_dup_num and self._options.file_dump:
                tasks = [tuple([i] + task_base + [output_base.format(self._options.output_file.format(i + 1))] + task_extras) for i in range(self._options.dup)]
            elif self._task_dup_num:
                tasks = [tuple([i] + task_base + [None] + task_extras) for i in range(self._options.dup)]
            elif self._options.file_dump:
                tasks = [tuple(task_base + [output_base.format(self._options.output_file.format(i + 1))] + task_extras) for i in range(self._options.dup)]
            else:
                tasks = [tuple(task_base + [None] + task_extras)] * self._options.dup

            results = pool.imap_unordered(self._runSimulation, tasks)
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
        self._whenDone()

    def __setBaseParserOptions(self):
        self._oparser.add_option("-d", "--duplications", type="int", action="store", dest="dup", default=1, help="number of duplications")
        self._oparser.add_option("-o", "--output", action="store", dest="output_dir", default="./output", help="directory to dump output files")
        self._oparser.add_option("-f", "--filename", action="store", dest="output_file", default="duplication_{0}", help="output file name template")
        self._oparser.add_option("-g", "--nofiledump", action="store_false", dest="file_dump", default=True, help="do not output duplication files")
        self._oparser.add_option("-k", "--skip", action="store", type="int", dest="skip", default=1, help="number of generations between dumping output -- 0 for only at the end")
        self._oparser.add_option("-s", "--statsfile", action="store", dest="stats_file", default="aggregate", help="file for aggregate stats to be dumped")
        self._oparser.add_option("-m", "--poolsize", action="store", type="int", dest="pool_size", default=2, help="number of parallel computations to undertake")
        self._oparser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False, help="suppress standard output")

    def __checkBaseParserOptions(self):
        if not self._options.dup or self._options.dup <= 0:
            self._oparser.error("Number of duplications must be positive")

    def _formatRun(self, result):
        return result

    def _setParserOptions(self):
        pass

    def _checkParserOptions(self):
        pass

    def _setData(self):
        pass

    def _buildTask(self):
        return []

    def _whenDone(self):
        pass

