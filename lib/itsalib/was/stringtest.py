
from simpleparse.common import numbers, strings

from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import DispatchProcessor

grammar = r'''
text        := string
value       := 
TESTS = [
        (

parser = Parser(grammar)
for production, tests in TESTS:
    print production
    for test in tests:
        success, children, nextcharacter = parser.parse(test, production=production)
        #print success, children, nextcharacter
        assert success and nextcharacter==len(test)
        print 'success'
    print

