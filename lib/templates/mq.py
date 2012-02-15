
from itsalib.template import StaticITSATemplate

class DefineLocalQueue(StaticITSATemplate):
    """
    DEFINE QLOCAL({{qname}}) +
        DEFPSIST({{defpsist+py:'YES' if defpsist.strip().lower() == 'p' or defpsist.strip().lower() == 'yes' else 'NO'}}) +
        DESCR('{{descr}}') +
        BOTHRESH({{bothresh}}) +
        MAXDEPTH({{maxdepth}}) REPLACE
    """

class DefineRemoteQueue(StaticITSATemplate):
    """
    DEFINE QREMOTE({{qname}}) +
        DEFPSIST({{defpsist+py:'YES' if defpsist.strip().lower() == 'p' or defpsist.strip().lower() == 'yes' else 'NO'}}) +
        DESCR('{{descr}}') +
        RNAME('{{rname}}') +
        RQMNAME('{{rqmname}}') +
        XMITQ({{xmitq}}) REPLACE
    """

class DefineQueueAlias(StaticITSATemplate):
    """
    DEFINE QALIAS({{qname}}) +
        DEFPSIST({{defpsist+py:'YES' if defpsist.strip().lower() == 'p' or defpsist.strip().lower() == 'yes' else 'NO'}}) +
        DESCR('{{descr}}') +
        TARGQ('{{targq}}') REPLACE
    """

class DefineTransmissionQueue(StaticITSATemplate):
    """
    DEFINE QLOCAL({{qname}}) +
        DEFPSIST({{defpsist+py:'YES' if defpsist.strip().lower() == 'p' or defpsist.strip().lower() == 'yes' else 'NO'}}) +
        DESCR('{{descr}}') +
        INITQ('{{initq}}') +
        MAXDEPTH({{maxdepth}}) +
        USAGE(XMITQ) REPLACE
    """
    
class DefineSenderChannel(StaticITSATemplate):
    """
    DEFINE CHANNEL({{qname}}) +
        CHLTYPE(SDR) +
        CONNAME('{{conname}}') +
        XMITQ('{{xmitq}}') +
        CONVERT({{convert+py:'YES' if convert.strip().lower() == 'sender' else 'NO'}}) +
        DESCR('{{descr}}') REPLACE
    """

class DefineReceiverChannel(StaticITSATemplate):
    """
    DEFINE CHANNEL({{qname}}) +
        CHLTYPE(RCVR) +
        MCAUSER('{{mcauser}}') +
        DESCR('{{descr}}') REPLACE
    """

class DeleteLocalQueue(StaticITSATemplate):
    """
    DELETE QLOCAL({{qname}})
    """

DeleteTransmissionQueue = DeleteLocalQueue

class DeleteRemoteQueue(StaticITSATemplate):
    """
    DELETE QREMOTE({{qname}})
    """

class DeleteQueueAlias(StaticITSATemplate):
    """
    DELETE QALIAS({{qname}})
    """

class DeleteChannel(StaticITSATemplate):
    """
    DELETE CHANNEL({{qname}})
    """

