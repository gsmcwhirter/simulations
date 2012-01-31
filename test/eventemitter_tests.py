from simulations.utils.eventemitter import EventEmitter

from nose.tools import assert_equal

class TestEventEmitter:
    
    def setUp(self):
        self.emitter = EventEmitter()
        self.result = None
        
    def tearDown(self):
        pass
    
    def test_add_remove(self):
        assert_equal(self.emitter.listeners('test'), [])
        assert_equal(self.emitter.on('test', 1), self.emitter)
        assert_equal(self.emitter.listeners('test'), [1])
        assert_equal(self.emitter.on('test', 2), self.emitter)
        assert_equal(self.emitter.listeners('test'), [1,2])
        assert_equal(self.emitter.add_listener('test', 3), self.emitter)
        assert_equal(self.emitter.listeners('test'), [1,2,3])
        assert_equal(self.emitter.add_listener('test', 4), self.emitter)
        assert_equal(self.emitter.listeners('test'), [1,2,3,4])
        assert_equal(self.emitter.remove_listener('test', 3), self.emitter)
        assert_equal(self.emitter.listeners('test'), [1,2,4])
        assert_equal(self.emitter.remove_all_listeners('test'), self.emitter)
        assert_equal(self.emitter.listeners('test'), [])
        
        for i in range(11):
            self.emitter.on('test', i)
        
        assert_equal(self.emitter.listeners('test'), range(11))
        
    def test_emit(self):
        assert self.result is None, "self.result is not None"
        
        def test(this):
            this.result = 1
        
        self.emitter.on('test', test)
        assert_equal(self.emitter.listeners('test'), [test])
        
        assert_equal(self.emitter.emit('test', self), self.emitter)
        assert_equal(self.emitter.listeners('test'), [test])
        assert_equal(self.result, 1)
        
    def test_once(self):
        assert self.result is None, "self.result is not None"
        
        def test(this):
            if this.result is None:
                this.result = 0
                
            this.result += 1
            
        assert_equal(self.emitter.on('test', test), self.emitter)
        assert_equal(self.emitter.once('test', test), self.emitter)
        
        assert_equal(self.emitter.listeners('test')[0], test)
        assert_equal(len(self.emitter.listeners('test')), 2)
        
        self.emitter.emit('test', self)
        assert_equal(self.result, 2)
        assert_equal(self.emitter.listeners('test'), [test])
        
        self.emitter.emit('test', self)
        assert_equal(self.result, 3)
        assert_equal(self.emitter.listeners('test'), [test])
        
    def test_max_listeners(self):
        assert_equal(self.emitter._max_listeners, 10)
        assert_equal(self.emitter.set_max_listeners(12), self.emitter)
        assert_equal(self.emitter._max_listeners, 12)
        
    def test_remove_notthere(self):
        assert_equal(self.emitter.listeners('test'), [])
        try:
            assert_equal(self.emitter.remove_listener('test', 2), self.emitter)
        except ValueError:
            assert False, "Threw an error when trying to remove a non-existent listener"
