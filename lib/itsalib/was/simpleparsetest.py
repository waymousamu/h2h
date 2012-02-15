
grammar = '''
para           := (plain / markup)+
plain          := (word / whitespace / punctuation)+
whitespace     := [ \t\r\n]+
alphanums      := [a-zA-Z0-9]+
word           := alphanums, (wordpunct, alphanums)*, contraction?
wordpunct      := [-_]
contraction    := "'", ('am'/'clock'/'d'/'ll'/'m'/'re'/'s'/'t'/'ve')
markup         := emph / strong / module / code / title
emph           := '-', plain, '-'
strong         := '*', plain, '*'
module         := '[', plain, ']'
code           := "'", plain, "'"
title          := '_', plain, '_'
punctuation    := (safepunct / mdash)
mdash          := '--'
safepunct      := [!@#$%^&()+=|\{}:;<>,.?/"]
'''

codes = \
{ 'emph'    : ('<em>', '</em>'),
  'strong'  : ('<strong>', '</strong>'),
  'module'  : ('<em><code>', '</code></em>'),
  'code'    : ('<code>', '</code>'),
  'title'   : ('<cite>', '</cite>'),
}

import os
from sys import stdin, stdout, stderr
from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import DispatchProcessor


tests = [
'''
hello *you*!
''',
]

class Processor(DispatchProcessor):
	def plain( self, (tag,start,stop,subtags), buffer ):
		print (tag,start,stop,subtags), buffer
	def word( self, (tag,start,stop,subtags), buffer ):
		print (tag,start,stop,subtags), buffer
	def markup( self, (tag,start,stop,subtags), buffer ):
		print (tag,start,stop,subtags), buffer

parser = Parser(grammar)
for test in tests:
    success, children, nextcharacter = parser.parse( test, production="para", processor=Processor())
    #print success, children, nextcharacter
    assert success and nextcharacter==len(test)
    print

from simpleparse import generator
from simpleparse.stt.TextTools import TextTools

input = tests[0]
parser = generator.buildParser(grammar).parserbyname("para")
taglist = TextTools.tag(input, parser)
for tag, beg, end, parts in taglist[1]:
    if tag == 'plain':
        stdout.write(input[beg:end])
    elif tag == 'markup':
        markup = parts[0]
        mtag, mbeg, mend = markup[:3]
        start, stop = codes.get(mtag, ('<!-- unknown -->','<!-- / -->'))
        stdout.write(start + input[mbeg+1:mend-1] + stop)
stderr.write('parsed %s chars of %s\n' %  (taglist[-1], len(input)))


