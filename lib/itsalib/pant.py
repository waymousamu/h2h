"""
Helper functions for invoking Ant tasks
"""
from org.apache.tools.ant import IntrospectionHelper
from org.apache.tools.ant import RuntimeConfigurable

from types import *

def nested(**attrs):
    return attrs

class PAnt(object):
    
    def __init__(self, proj):
        self.proj=proj
        
    # Assume it's an Ant task
    def __getattr__(self, method):
        print "Creating task :"+method
        return lambda **attrs: self.execTask(method, **attrs) 
    
    def execTask( self, name, **attrs):
        t=self.createTask(name, **attrs)
        t.execute()

    def createTask( self, name, **attrs):

        t=self.proj.createTask(name)
        conf=t.getRuntimeConfigurableWrapper()
        self.configureElement(t, conf, attrs)
        t.maybeConfigure()

        return t

    def createNestedElement(self, parent, name, attrs):
        ih=IntrospectionHelper.getHelper(self.proj, parent.getClass());
        child = ih.createElement(self.proj, parent, name)
        conf=RuntimeConfigurable(child, name)
        self.configureElement(child, conf, attrs)
        conf.maybeConfigure(self.proj)

        return conf

    def configureElement(self, owner, conf, attrs):
        for attrName, attrVal in attrs.iteritems():
            if type(attrVal) is DictType:
                nConf=self.createNestedElement(owner, attrName, attrVal)
                conf.addChild(nConf)
            else:
                conf.setAttribute(attrName, attrVal)
                
    def createProps(self, dict):
        
        for propName, propVal in dict.iteritems():
            self.proj.setNewProperty(propName, propVal)


