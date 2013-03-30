#from nose.tools import assert_equal, assert_raises
#from pp import DestroyedServerError
#from simulations.utils.fake_server import Server as FakeServer
#
#
#class TestFakeServer:
#
#    def setUp(self):
#        self.test = []
#        self.server = FakeServer()
#
#        def task(arg1, arg2):
#            return [arg1] * (arg2 + 1)
#
#        self.task = task
#
#    def tearDown(self):
#        pass
#
#    def test_fake_server(self):
#
#        def callback(arg1, arg2, arg3):
#            self.test.append([(arg1, arg2), arg3])
#
#        assert_equal(self.server.get_active_nodes(), {'fake': 1})
#        assert_equal(self.server.get_ncpus(), 1)
#        assert_equal(self.server.get_stats(), {})
#        self.server.print_stats()
#        self.server.set_ncpus('autodetect')
#        self.server.wait()
#        self.server.wait('test')
#
#        for i, j in enumerate(xrange(3)):
#            func = self.server.submit(self.task, (i, j),
#                                        callback=callback,
#                                        callbackargs=(i, j))
#            assert_equal(func(), [i] * (j + 1))
#
#        assert_equal(self.test, [[(0, 0), [0]],
#                                 [(1, 1), [1, 1]],
#                                 [(2, 2), [2, 2, 2]]])
#
#    def test_destroy(self):
#        self.server.destroy()
#        assert_raises(DestroyedServerError,
#                        self.server.submit,
#                        self.task, [1, 2])
