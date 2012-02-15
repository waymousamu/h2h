
grammar = r'''
wsobject           := null / (alphanum / attribute / propertyset / innerobject)+
innerobject        := leftparen, name, ws, object_open, (propertyset / attribute)+, object_close, rightparen
propertyset        := leftparen, 'propertySet', ws, object_open, leftparen, name, ws, object_open, datalist, object_close, rightparen, object_close, rightparen
datalist           := (leftparen, attribute+, rightparen)+
attribute          := leftparen, name, ws, value, rightparen
name               := [a-zA-Z_]+
value              := (null / identifier / text / unquotedtext)+
object_open        := ws?, '"', leftparen
object_close       := rightparen, '"', ws?
null               := leftparen, rightparen
leftparen          := ws?, '[', ws?
rightparen         := ws?, ']', ws?
identifier         := alphanum, ('.', alphanum)*
text               := '"', (alphanum / ws / punctuation)*, '"'
unquotedtext       := (alphanum / punctuation)+
alphanum           := [a-zA-Z0-9]+
punctuation        := [!@#$%^&()+=|\{}:;<>,.~`-_'?/]
ws                 := [ \t\r\n]+
'''

TESTS = [
    ('name', ['a', 'name', 'required_name', 'dataConnection']),
    ('null', ['[]']),
    ('text', [
        '''"This is a required
property. This is an actual database name, and it's not the locally
catalogued database name. The Universal JDBC Driver does not rely on
information catalogued in the DB2 database directory."''',
            ]),
    ('unquotedtext', [
        'ssl://cics_dev', '/opt/Websphere/util.jar',]),
    ('attribute', [
        '[varName varValue]', '[varName varValue] ', '[varName varValue]     ',
        '[varName "some text!"]',
            ]),
    ('datalist', [
        '''[[description "This is a required
property. This is an actual database name, and its not the locally
catalogued database name. The Universal JDBC Driver does not rely on
information catalogued in the DB2 database directory."]
[name databaseName]
[required true]
[type java.lang.String]
[value []]]''',
        '''[[description "This is a required
property. This is an actual database name, and its not the locally
catalogued database name. The Universal JDBC Driver does not rely on
information catalogued in the DB2 database directory."]
[name databaseName]
[required true]
[type java.lang.String]
[value []]]
[[description "This is a required
property. This is an actual database name, and its not the locally
catalogued database name. The Universal JDBC Driver does not rely on
information catalogued in the DB2 database directory."]
[name databaseName]
[required true]
[type java.lang.String]
[value []]]''',
                ]),
    ('propertyset', [
        '''[propertySet "[[resourceProperties "[[[description "This is a required
property. This is an actual database name, and its not the locally
catalogued database name. The Universal JDBC Driver does not rely on
information catalogued in the DB2 database directory."]
[name databaseName]
[required ssl://cics_dev]
[type java.lang.String]
[value []]]]"]]"]''',
        '''[propertySet "[[resourceProperties "[[[description ConnectionURL]
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
[value PIDTEST]]]"]]"]''',
                ]),
    ('innerobject', [
        '''[connectionPool "[[agedTimeout 0]
[connectionTimeout 180]
[freePoolDistributionTableSize 0]
[maxConnections 10]
[minConnections 1]
[numberOfUnsharedPoolPartitions 0]
[properties []]
[purgePolicy FailingConnectionOnly]
[reapTime 180]
[testConnection false]
[testConnectionInterval 0]
[unusedTimeout 1800]]"]
        ''',
                ]),
    ('wsobject', [
        "[]", "1",
        '''[authDataAlias []] [minConnections 1]''',
        '''[authDataAlias []] [minConnections 1]
[connectionPool "[[agedTimeout 0]
[connectionTimeout 180]
[freePoolDistributionTableSize 0]
[maxConnections 10]
[minConnections 1]
[numberOfUnsharedPoolPartitions 0]
[properties []]
[purgePolicy FailingConnectionOnly]
[reapTime 180]
[testConnection false]
[testConnectionInterval 0]
[unusedTimeout 1800]]"]
[provider ECIResourceAdapter]
        ''',
'''
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
[testConnection false]
[testConnectionInterval 0]
[unusedTimeout 1800]]"]
[propertySet "[[resourceProperties "[[[description ConnectionURL]
[name ConnectionURL]
[required false]
[type java.lang.String]
[value ssl://cics_dev]] [[description KeyRingClass]
[name KeyRingClass]
[required false]
[type java.lang.String]
[value opt/IBM/WebSphere/AppServer/etc/CTGKeyFile.jks]] [[description KeyRingPassword]
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
[value PIDTEST]]]"]]"]
''',
'''
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
256,TRACE_DIAGNOSTICS = 512,TRACE_SQLJ = 1024,TRACE_ALL = 1, ."]
[name traceLevel]
[required false]
[type java.lang.Integer]
[value []]]
]"]]"]

''',
'''
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
''', ]),
        ]

from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import DispatchProcessor

parser = Parser(grammar)
for production, tests in TESTS:
    print production
    for test in tests:
        success, children, nextcharacter = parser.parse(test, production=production)
        #print success, children, nextcharacter
        assert success and nextcharacter==len(test)
        print 'success'
    print

