s1 = '''
[authDataAlias []]
[authMechanismPreference BASIC_PASSWORD]
[connectionPool "[[agedTimeout 0]
[connectionTimeout 180]
[freePoolDistributionTableSize 0]
[maxConnections 10]
[minConnections 1]
[numberOfUnsharedPoolPartitions 0]
[properties []]
[purgePolicy FailingConnectionOnly]
[reapTime 180]
[surgeThreshold -1]
[testConnection false]
[testConnectionInterval 0]
[unusedTimeout 1800]]"]
[propertySet "[[resourceProperties "[[[description "This is a required
property. This is an actual database name, and its not the locally
catalogued database name. The Universal JDBC Driver does not rely on
information catalogued in the DB2 database directory."]
[name databaseName]
[required true]
[type java.lang.String]
[value DB2Foo]] [[description "The JDBC connectivity-type of a data
source. If you want to use a type 4 driver, set the value to 4. If you
want to use a type 2 driver, set the value to 2. Use of driverType 2
is not supported on WAS z/OS."]
[name driverType]
[required true]
[type java.lang.Integer]
[value 4]] [[description "The TCP/IP address or name for the DRDA server."]
[name serverName]
[required false]
[type java.lang.String]
[value ServerFoo]] [[description "The TCP/IP port number where the
DRDA server resides."]
[name portNumber]
[required false]
[type java.lang.Integer]
[value 007]] [[description "The description of this datasource."]
[name description]
[required false]
[type java.lang.String]
[value []]] [[description "The DB2 trace level for logging to the
logWriter or trace file. Possible trace levels are: TRACE_NONE =
0,TRACE_CONNECTION_CALLS = 1,TRACE_STATEMENT_CALLS =
2,TRACE_RESULT_SET_CALLS = 4,TRACE_DRIVER_CONFIGURATION =
16,TRACE_CONNECTS = 32,TRACE_DRDA_FLOWS =
64,TRACE_RESULT_SET_META_DATA = 128,TRACE_PARAMETER_META_DATA =
256,TRACE_DIAGNOSTICS = 512,TRACE_SQLJ = 1024,TRACE_ALL = -1, ."]
[name traceLevel]
[required false]
[type java.lang.Integer]
[value []]]
]]

'''

s2 = '''
[authDataAlias []]
[authMechanismPreference BASIC_PASSWORD]
[connectionDefinition (cells/CCITstCell001/nodes/Z-CCIDTTNode001|resources.xml#ConnectionDefinition_1184069423281)]
[connectionPool "[[agedTimeout 0]
[connectionTimeout 180]
[freePoolDistributionTableSize 0]
[maxConnections 10]
[minConnections 1]
[numberOfFreePoolPartitions 0]
[numberOfSharedPoolPartitions 0]
[numberOfUnsharedPoolPartitions 0]
[properties []]
[purgePolicy FailingConnectionOnly]
[reapTime 180]
[stuckThreshold 0]
[stuckTime 0]
[stuckTimerTime 0]
[surgeCreationInterval 0]
[surgeThreshold -1]
[testConnection false]
[testConnectionInterval 0]
[unusedTimeout 1800]]"]
[customProperties []]
[description "CTG Connection Factory for CCI ITSA script"]
[jndiName CTGConnectionFactory_LP1]
[logMissingTransactionContext true]
[manageCachedHandles false]
[mapping "[[mappingConfigAlias DefaultPrincipalMapping]]"]
[name CTGConnectionFactory_LP1]
[propertySet "[[resourceProperties "[[[description ConnectionURL]
[name ConnectionURL]
[required false]
[type java.lang.String]
[value ssl://cics_dev]] [[description KeyRingClass]
[name KeyRingClass]
[required false]
[type java.lang.String]
[value /opt/IBM/WebSphere/AppServer/etc/CTGKeyFile.jks]] [[description KeyRingPassword]
[name KeyRingPassword]
[required false]
[type java.lang.String]
[value was6cert]] [[description PortNumber]
[name PortNumber]
[required false]
[type java.lang.String]
[value 8059]] [[description ServerName]
[name ServerName]
[required false]
[type java.lang.String]
[value PIDTEST]] [[description TPNName]
[name TPNName]
[required false]
[type java.lang.String]
[value MRT4]] [[description TranName]
[name TranName]
[required false]
[type java.lang.String]
[value MRT4]] [[name ClientSecurity]
[required false]
[type java.lang.String]] [[name Password]
[required false]
[type java.lang.String]] [[name ServerSecurity]
[required false]
[type java.lang.String]] [[description SocketConnectTimeout]
[name SocketConnectTimeout]
[required false]
[type java.lang.String]
[value 0]] [[description TraceLevel]
[name TraceLevel]
[required false]
[type java.lang.Integer]
[value 1]] [[name UserName]
[required false]
[type java.lang.String]]]"]]"]
[provider ECIResourceAdapter_Z-CCIDTTNode001(cells/CCITstCell001/nodes/Z-CCIDTTNode001|resources.xml#J2CResourceAdapter_1184069423250)]
'''


import re

def string2list(s):
    RE_QUOTE = "[^\[\]\s,]+"
    def quote(matchobj):
        return '"%s", ' % matchobj.group(0)
    s = s.replace(']', '], ').replace('"', '')
    s = '[%s]' % re.sub(RE_QUOTE, quote, s)
    return eval(s)

def list2dict(seq):
    if not seq: return []
    d = {}
    for item in seq:
        head, tail = item[0], item[1:]
        if isinstance(tail[0], basestring):
            d[head] = ' '.join(tail)
        else:
            tail = tail[0]
            if len(tail) > 1 and not isinstance(tail[0][0], basestring):
                #it's a property set
                d[head] = tail
            else:
                d[head] = list2dict(tail)
    return d

def string2dict(s):
    return list2dict(string2list(s))


from pprint import pprint

pprint(string2dict(s1))

On Apr 24, 4:05 am, Paul McGuire <pt...@austin.rr.com> wrote:
> On Apr 23, 8:00 pm, "Eric Wertman" <ewert...@gmail.com> wrote:
> 
> > I have a set of files with this kind of content (it's dumped from WebSphere):
> 
> > [propertySet "[[resourceProperties "[[[description "This is a required
> > property. This is an actual database name, and its not the locally
> > catalogued database name. The Universal JDBC Driver does not rely on
> > ...
> 
> A couple of comments first:
> - What is the significance of '"[' vs. '[' ?  I stripped them all out
> using

The data can be thought of as a serialised object. A simple attribute looks like:

[name someWebsphereObject]

or

[jndiName []]

(if 'jndiName is None')

A complex attribute is an attribute whose value is itself an object (or dict if you prefer). The *value* is indicated with "[...]":

[connectionPool "[[agedTimeout 0]
[connectionTimeout 180]
[freePoolDistributionTableSize 0]
[maxConnections 10]
[minConnections 1]
[numberOfFreePoolPartitions 0]
[numberOfSharedPoolPartitions 0]
[unusedTimeout 1800]]"]


However, 'propertySet' is (in effect) a keyword and its value may be thought of as a 'data table' or 'list of data rows', where 'data row' == dict/object

You can see how the posted example is incomplete because the last 'row' is missing all but one 'column'.

>     text = text.replace('"[','[')
> - Your input text was missing 5 trailing ]'s.
> 

In fact only 2 (you're probably forgetting that the original isn't Python). To fix the example, remove the last 'description' and add two ]'s

> Here's the parser I used, using pyparsing:
> 
> from pyparsing import nestedExpr,Word,alphanums,QuotedString
> from pprint import pprint
> 
> content = Word(alphanums+"_.") | QuotedString('"',multiline=True)
> structure = nestedExpr("[", "]", content).parseString(text)
> 
> pprint(structure.asList())
> 

By the way, I think this would be a good example for the pyparsing recipes page, or even a developerworks article?

http://www.ibm.com/developerworks/websphere/library/techarticles/0801_simms/0801_simms.html

Gerard

