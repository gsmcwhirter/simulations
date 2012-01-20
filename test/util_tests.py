import gametheory.base.util as util
import re
import string

from nose.tools import assert_equal

class TestUtils:
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_random_string(self):
        assert_equal(len(util.random_string()), 6)
        assert_equal(len(util.random_string(8)), 8)
        assert re.match('[{0}{1}]{{6}}'.format(string.ascii_uppercase, string.digits), util.random_string())
        assert re.match('[{0}{1}]{{8}}'.format(string.ascii_uppercase, string.digits), util.random_string(8))
        assert re.match('[{0}]{{7}}'.format(string.ascii_lowercase), util.random_string(7, string.ascii_lowercase))
