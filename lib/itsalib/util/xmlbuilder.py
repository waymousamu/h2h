
from SimpleXMLWriter import XMLWriter
from cStringIO import StringIO

class _XmlElement(list):
    def __init__(self, tag):
        self.tag = tag
        self.text = None
        self.attrib = {}

    def __call__(self, text='', **kwargs):
        self.text = text
        self.attrib = kwargs
        return self
    
    def __repr__(self):
        return "<_XmlElement %s>" % self.tag
    
    def append(self, value):
        list.append(self, value)
        return value

    def __getattr__(self, value):
        if value == "add_comment":
            return self.append( _XmlComment() )
        elif value == "add_text":
            return self.append( _XmlText() )
        else:
            return self.append( _XmlElement(value) )

    def _write(self, writer):
        #class is a keyword, so can't use it as an attribute name
        #use 'class_' then replace it here
        class_ = None
        for key in self.attrib.iterkeys():
            if key == 'class_':
                class_ = self.attrib[key]
                del self.attrib[key]
                break
        if class_ is not None:
            self.attrib['class'] = class_
        #now write this element
        if not self.__len__() and not self.text:
	        writer.element( self.tag, None, self.attrib )
        else:
            writer.start(self.tag, self.attrib)
            if self.text is not None:
                writer.data(self.text)
            #write any children if any
            for node in self:
                node._write(writer)
            writer.end()

class _XmlText(_XmlElement):

    def __init__(self):
        self.text = ''

    def __call__(self, text=''):
        self.text = text
        return self

    def _write(self, writer):
        writer.data(self.text)
        for node in self:
            node._write(writer)

    def __repr__(self):
        return "<_XmlText>"

class _XmlComment(_XmlText):

    def _write(self, writer):
        writer.comment(self.text)

    def __repr__(self):
        return "<_XmlComment>"

class XmlFragment(_XmlElement):
    '''
    >>> xml = XmlFragment()
    >>> root = xml.div()
    >>> print root
    <_XmlElement div>
    >>> print xml
    <div />
    >>> firstchild = root.p("Some text", id="1")
    >>> print xml
    <div><p id="1">Some text</p></div>
    >>> firstchild.br()
    <_XmlElement br>
    >>> print xml
    <div><p id="1">Some text<br /></p></div>
    >>> firstchild.add_text("more text, ")
    <_XmlText>
    >>> print xml
    <div><p id="1">Some text<br />more text, </p></div>
    >>> firstchild.add_text("and more.").br()
    <_XmlElement br>
    >>> print xml
    <div><p id="1">Some text<br />more text, and more.<br /></p></div>
    >>> root.add_comment("COMMENT")
    <_XmlComment>
    >>> print xml
    <div><p id="1">Some text<br />more text, and more.<br /></p><!-- COMMENT -->
    </div>
    '''
    def __init__(self, encoding="utf-8"):
        self.encoding = encoding

    def _write(self, writer):
        for node in self:
            node._write(writer)

    def write(self, outfile):
        w = XMLWriter(outfile, self.encoding)
        self._write( w )

    def __str__(self):
        s = StringIO()
        self.write( s )
        ret = s.getvalue()
        s.close()
        return ret
    
class MissingDocumentRootException(Exception): pass

class XmlDocument(XmlFragment):
    '''
    >>> xml = XmlDocument("us-ascii")
    >>> print xml
    Traceback (most recent call last):
        ...
    MissingDocumentRootException
    >>> root = xml.items(catalog="R&D")
    >>> print xml
    <?xml version='1.0'?>
    <items catalog="R&amp;D" />
    >>> root.item("Item 1", id="1")
    <_XmlElement item>
    >>> root.item("Item 2", id="2")
    <_XmlElement item>
    >>> print xml
    <?xml version='1.0'?>
    <items catalog="R&amp;D"><item id="1">Item 1</item><item id="2">Item 2</item></items>
    '''
    def _write(self, writer):
        if not len(self):
            raise MissingDocumentRootException
        writer.declaration()
        for node in self:
            node._write(writer)
        
def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()

