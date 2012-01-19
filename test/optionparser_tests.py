from gametheory.base.optionparser import OptionParser

from nose.tools import assert_equal
from nose.tools import assert_raises

class TestOptionParser:
    
    def setUp(self):
        self.oparser = OptionParser()
        
    def tearDown(self):
        self.oparser = None

    def erh(self):
        return self.oparser._errorhandler

    def exh(self):
        return self.oparser._exithandler
        
    def test_init(self):
        
        assert self.oparser is not None, "Option parser is not set up"
        
        try:
            self.erh()
        except AttributeError:
            assert False, "oparser._errorhandler not defined"
            
        try:
            self.exh()
        except AttributeError:
            assert False, "oparser._exithandler not defined"
        
    def test_errorhandler(self):
        def handler(msg):
            return msg
        
        self.oparser.set_error_handler(handler)
        assert_equal(self.oparser._errorhandler, handler)
        
        assert_equal(self.oparser.error("test"), "test")
        
    def test_exithandler(self):
        def handler(code, msg):
            return (code, msg)
    
        self.oparser.set_exit_handler(handler)
        assert_equal(self.oparser._exithandler, handler)
        
        assert_equal(self.oparser.exit(1), (1,None))
        assert_equal(self.oparser.exit(1, 2), (1, 2))
        
    def test_defaults(self):
        assert_raises(SystemExit, self.oparser.error, "test")
        assert_raises(SystemExit, self.oparser.exit)
        
