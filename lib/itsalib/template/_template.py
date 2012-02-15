
import re
import inspect
import textwrap
from string import Template as StringTemplate

linesep = '\n'
blocksep = 2*linesep
COMMENTMARKER = '# '
COMMENTWIDTH = 80

__all__ = [
        'ITSATemplate', 'StaticITSATemplate',
        'SafeITSATemplate', 'StaticSafeITSATemplate',
        'FormatTemplate', 'StaticFormatTemplate',
        'StringTemplate', 'StaticStringTemplate',
        'StaticSafeStringTemplate',
        'MultiReplaceFactory',
        ]

RX = r'''
    \{\{
    (?P<variable>[_a-z][_a-z0-9]*)
    (?P<notnull>:)?
    \s*
    (?P<op>[-=?+|])?
    \s*
    (?P<default>.*?)
    \}\}
'''

RAISEOP = '?'
YIELDIFNOTOP = '-'
YIELDANDSETIFNOTOP = '='
YIELDIFOP = '+'
MAPOP = '|'
NOOP = ''
PYTOKEN = "py:"


class ITSATemplate(object):
    '''
    A custom templating scheme.

    Straight replacement. KeyError if doesn't exist:

    >>> t = ITSATemplate("""
    ... Hello {{name}}!
    ... """)
    >>> print t.replace()
    Traceback (most recent call last):
        ...
    KeyError: 'name'
    >>> print t.replace(name='you')
    Hello you!

    Null values evaluate to an empty string (null means boolean False):

    >>> print t.replace(name=None)
    Hello !

    But you can use the 'and is not null' operator to force a KeyError if
    the variable doesn't exist or is null.

    >>> t = ITSATemplate("""
    ... Hello {{name:}}!
    ... """)
    >>> print t.replace(name='')
    Traceback (most recent call last):
        ...
    KeyError: 'name'
    >>> print t.replace(name=False)
    Traceback (most recent call last):
        ...
    KeyError: 'name'
    >>> print t.replace(name=None)
    Traceback (most recent call last):
        ...
    KeyError: 'name'


    If key doesn't exist return default, also setting it:

    >>> t = ITSATemplate("""
    ... Hello {{name=stranger}}!
    ... """)
    >>> print t.replace()
    Hello stranger!
    >>> print t.replace(name='you')
    Hello you!


    If key doesn't exist return default, but don't set it:

    >>> t = ITSATemplate("""
    ... Hello {{name-stranger}}!
    ... """)
    >>> print t.replace()
    Hello stranger!
    >>> print t.replace(name='you')
    Hello you!

    If key *does* exist return default else return nothing:

    >>> t = ITSATemplate("""
    ... Hello {{name+stranger}}!
    ... """)
    >>> print t.replace()
    Hello !
    >>> print t.replace(name=True)
    Hello stranger!

    Difference between '=' and '-'.

    >>> t = ITSATemplate("""
    ... Hello {{name-stranger}}! Bye {{name}}!
    ... """)
    >>> print t.replace()
    Traceback (most recent call last):
        ...
    KeyError: 'name'
    >>> t = ITSATemplate("""
    ... Hello {{name=stranger}}! Bye {{name}}!
    ... """)
    >>> print t.replace()
    Hello stranger! Bye stranger!

    Default values can use standard python formatting.

    >>> t = ITSATemplate("""
    ... {{show+%(time)s %(level)-8s %(msg)s}}
    ... """)
    >>> 
    >>> print t.replace(time="10:31am", level="INFO", msg="mess", show=True)
    10:31am INFO    mess

    
    Map operator. Expects a list (iterator) whose each item is either a tuple
    or a dict. If the variable exists (and optionally is not null), then
    for each tuple/dict yield the formatted default.

    >>> t = ITSATemplate("""
    ... {{names|
    ... Hello %s %s!
    ... }}
    ... """)
    >>> print t.replace()
    Traceback (most recent call last):
        ...
    KeyError: 'names'
    >>> print t.replace(names=[('John', 'Doe'), ('Jane', 'Doe')])
    Hello John Doe!
    Hello Jane Doe!

    Python code.

    >>> t = ITSATemplate("""
    ... {{names+py:' '.join('Hello %s!' % n for n in names)}}
    ... """)
    >>> print t.replace(names=['John', 'Jane'])
    Hello John! Hello Jane!
    '''
    pattern = re.compile(RX, re.IGNORECASE | re.VERBOSE | re.DOTALL)
    defaultop = RAISEOP

    def __init__(self, text):
        self.text = text

    def _format(self, s, ns):
        if s.startswith(PYTOKEN):
            return str(eval(s[len(PYTOKEN):], None, ns))
        else:
            return s % ns

    def replace(self, **kw):
        def onmatch(match):
            data = match.groupdict()
            var = data['variable']
            op = data['op'] or self.defaultop
            notnull = bool(data['notnull'])
            default = data['default']
            no = var not in kw or (not kw[var] and notnull)
            if no:
                if op == MAPOP:
                    op = self.defaultop
                if op == RAISEOP:
                    raise KeyError(var)
                elif op == NOOP:
                    return match.group(0)
                elif op == YIELDIFOP:
                    return ''
                else:
                    ret = self._format(default, kw)
                    if op == YIELDANDSETIFNOTOP:
                        kw[var] = ret
                    return ret
            else:
                if op == YIELDIFOP:
                    return self._format(default, kw)
                elif op == MAPOP:
                    return ''.join(default % s for s in kw[var])
                else:
                    return kw[var] or ''
        return self.pattern.sub(onmatch, self.text)

class SafeITSATemplate(ITSATemplate):
    '''
    By default, no KeyErrors.

    >>> t = SafeITSATemplate("""
    ... Hello {{name}}!
    ... """)
    >>> print t.replace()
    Hello {{name}}!
    >>> print t.replace(name='you')
    Hello you!

    To force a KeyError use '?'.

    >>> t = SafeITSATemplate("""
    ... Hello {{name?}}!
    ... """)
    >>> print t.replace()
    Traceback (most recent call last):
        ...
    KeyError: 'name'

    Map operator.

    >>> t = SafeITSATemplate("""
    ... {{names|
    ... Hello %s %s!
    ... }}
    ... """)
    >>> print t.replace()
    {{names|
    Hello %s %s!
    }}
    >>> print t.replace(names=[('John', 'Doe'), ('Jane', 'Doe')])
    Hello John Doe!
    Hello Jane Doe!

    To get no output at all, send an empty list (or iterator).

    >>> print t.replace(names=[])
    >>>
    '''
    defaultop = NOOP

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#  Static Templates
#
#  A `StaticTemplate` is a class whose docstring is a template.  This is
#  useful for example to collect together short shell script snippets or
#  configuration file templates - things that don't warrant having a separate
#  file.
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class StaticTemplateMeta(type):

    _tmpl = None

    def text(cls):
        return inspect.getdoc(cls)

    def _get_tmpl(cls):
        if cls._tmpl is None:
            cls._tmpl = cls.factory(cls.text())
        return cls._tmpl

    template = property(_get_tmpl)

    def render(cls, **kw):
        return getattr(cls.template, cls.verb)(**kw)

    def __getattr__(cls, key):
        return getattr(cls.template, key)

    def __mod__(cls, arg):
        if hasattr(cls.template, '__mod__'):
            return cls.template.__mod__(arg)
        else:
            return cls.render(**arg)

    def __repr__(cls):
        return cls.text()

    def rawwrite(cls, fd, **kw):
        fd.write(cls.render(**kw))

    def write(cls, fd, **kw):
        fd.write(cls.render(**kw))
        fd.write(blocksep)

    def comment(cls, fd, text, width=COMMENTWIDTH, marker=COMMENTMARKER):
        fd.write(marker*width)
        textwidth = width - 2 - 2 * len(marker)
        for line in ( t.strip() for t in textwrap.wrap(text, textwidth, 
                                                replace_whitespace=False) ):
            fd.write(linesep)
            fd.write(marker)
            padding = ' ' * (width - len(line) - 2)
            fd.write("%s%s%s" % (line, padding, marker))
        fd.write(linesep)
        fd.write(marker*width)
        fd.write(blocksep)

class StaticTemplateBase(object):
    __metaclass__ = StaticTemplateMeta

class StaticITSATemplate(StaticTemplateBase):
    """
    >>> class MyTemplate(StaticITSATemplate):
    ...     '''
    ...     {{name}} had a {{superlative:+really }}{{adj-little}} {{object}},
    ...     it's {{attr}} was {{color-white}} as {{compare}}.
    ...     '''
    >>> print MyTemplate.replace(name='Mary', superlative=False,
    ... object='lamb', attr='fleece', compare='snow')
    Mary had a little lamb,
    it's fleece was white as snow.
    >>> print MyTemplate.replace(name='Mary', superlative=True, adj='big',
    ... object='lamb', attr='fleece', compare='snow')
    Mary had a really big lamb,
    it's fleece was white as snow.
    """
    factory = ITSATemplate
    verb = 'replace'

    @classmethod
    def getvarset(cls):
        def finditer(text):
            for match in cls.factory.pattern.finditer(text):
                yield match.group('variable')
        return set(finditer(cls.text()))

class StaticSafeITSATemplate(StaticITSATemplate):
    factory = SafeITSATemplate

class FormatTemplate(unicode):
    """
    Support for standard Python string formatting.

    A basestring has no suitable verb, ie. a method which takes keyword
    arguments and returns the modified text, so we create our own class
    to do this.
    """
    def format(self, **kw):
        return self.__mod__(kw)

class StaticFormatTemplate(StaticTemplateBase):
    """
    Static version of FormatTemplate.

    >>> class DefaultLog(StaticFormatTemplate):
    ...     '''
    ...     %(time)s %(level)-8s %(msg)s
    ...     '''
    >>> print DefaultLog.render(time="10:31am", level="INFO", msg="message")
    10:31am INFO    message

    To use tuple-substitutions use the '%' operator directly on the class:

    >>> class DefaultLog(StaticFormatTemplate):
    ...     '''
    ...     %s %-8s %s
    ...     '''
    >>> print DefaultLog % ("11:29pm", "WARN", "warning")
    11:29pm WARN    warning
    """
    factory = FormatTemplate
    verb = 'format'

class StaticStringTemplate(StaticTemplateBase):
    """
    Static version of `string.Template` from stdlib.
    """
    factory = StringTemplate
    verb = 'substitute'

    @classmethod
    def getvarset(cls):
        def finditer(text):
            for match in cls.factory.pattern.finditer(text):
                yield match.group('braced') or match.group('named')
        return set(finditer(cls.text()))

class StaticSafeStringTemplate(StaticStringTemplate):
    verb = 'safe_substitute'

def MultiReplaceFactory(startdelim, enddelim):

    class MultiReplaceTemplate(object):

        start = startdelim
        end = enddelim

        def __init__(self, text):
            self.text = text

        def replace(self, **kw):
            keys = kw.keys()
            keys.sort()
            keys.reverse()
            s = self.start
            e = self.end
            patterns = (re.escape('%s%s%s' % (s, key, e)) for key in keys)
            rx = re.compile('|'.join(patternS))
            i, j = len(s), len(e)
            def callback(match):
                key = match.group(0)
                #need len(key)-j rather than -j in case j is zero
                repl = kw[key[i:len(key)-j]]
                return repl
            return rx.sub(callback, self.text)

    return MultiReplaceTemplate


class DelimiterStaticTemplateBase(StaticTemplateBase):
    verb = 'replace'

    @classmethod
    def getvarset(cls):
        return set(cls.factory.pattern.findall(cls.text()))

class BracketsStaticTemplate(DelimiterStaticTemplateBase):
    factory = MultiReplaceFactory('[[', ']]')

class ChevronsStaticTemplate(DelimiterStaticTemplateBase):
    factory = MultiReplaceFactory('<', '>')

class HashesStaticTemplate(DelimiterStaticTemplateBase):
    factory = MultiReplaceFactory('#', '#')

class PercentsStaticTemplate(DelimiterStaticTemplateBase):
    factory = MultiReplaceFactory('%', '%')

#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Creating StaticTemplate python modules from text files
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

extensionmap = {
        '.itsa': 'StaticITSATemplate',
        '.itsatemplate': 'StaticITSATemplate',
        '.tmpl': 'StaticStringTemplate',
        '.template': 'StaticStringTemplate',
        }

class ModuleMaker(StaticITSATemplate):
    """
    from itsalib.template import {{templateclass:=StaticITSATemplate}}

    class {{classname}}({{templateclass}}):
    """

SPACER = ' ' * 8
TRIPLE1 = "'''"
TRIPLE2 = '"""'

def make_module(infile, outfile=None, classname=None):
    from os.path import splitext, basename
    root, ext = splitext(infile)
    outfile = outfile or root + '.py'
    name = classname or basename(root)
    if ext not in extensionmap:
        ext = '.itsa'
    templateclass = extensionmap[ext]
    fd = open(outfile, 'wb')
    fd.write(ModuleMaker.render(templateclass=templateclass,
                                classname=name))
    fd.write(TRIPLE1)
    textin = open(infile)
    for line in textin:
        fd.write(line.replace(TRIPLE1, TRIPLE2))
    fd.write(TRIPLE1)
    fd.close()



## Ian Bicking's tempita

try:
    import tempita.Template as TempitaTemplate

    class StaticTempitaTemplate(StaticTemplateBase):
        factory = tempita.Template
        verb = 'substitute'

    __all__.append('TempitaTemplate')
    __all__.append('StaticTempitaTemplate')
    extensionmap['.tempita'] = StaticTempitaTemplate

except ImportError:
    pass

# makotemplates.org

try:

    from mako.template import Template as MakoTemplate

    class StaticMakoTemplate(StaticTemplateBase):
        factory = MakoTemplate
        verb = 'render'

    __all__.append('MakoTemplate')
    __all__.append('StaticMakoTemplate')
    extensionmap['.mako'] = StaticMakoTemplate

except ImportError:
    pass

if __name__ == '__main__':
    import doctest
    options = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    doctest.testmod(optionflags=options)



