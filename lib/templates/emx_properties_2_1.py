
from itsalib.template import StaticTemplate

class InitProperties(StaticTemplate):
    """
    __scripts_version__ = ${__scripts_version__}

    #::::::::::::::::::::::::::
    #NAME: cat
    #DESC: Deployment category
    #ALLOWED: Dev, Lab, Prd, Tst
    #EXAMPLE: cat=Tst
    #::::::::::::::::::::::::::-
    cat=${CAT}

    #::::::::::::::::::::::::::
    #NAME: CAT2
    #DESC: Deployment category initial
    #ALLOWED: D, L, P, T
    #EXAMPLE: CAT2=T
    #::::::::::::::::::::::::::-
    CAT2=${CAT2}

    #::::::::::::::::::::::::::-
    #NAME: envid
    #DESC: Environment id
    #EXAMPLE: envid=LP3
    #EXAMPLE: envid=MP4
    #::::::::::::::::::::::::::-
    envid=${ENVID}

    #::::::::::::::::::::::::::-
    #NAME: hostname
    #DESC: The physical name of the server which is being configured
    #EXAMPLE: hostname=axtcci002
    #::::::::::::::::::::::::::-
    hostname=${hostname}

    #::::::::::::::::::::::::::-
    #NAME: cellname
    #DESC: The name of the WAS logical cell
    #FORMAT: CCI%init.properties.cat%Cell00?%
    #EXAMPLE: CCITstCell001
    #::::::::::::::::::::::::::-
    cellname=${cellname}

    #::::::::::::::::::::::::::-
    #NAME: nodename
    #EXAMPLE: Z-CCITstMP4Node001
    #::::::::::::::::::::::::::-
    nodename=${nodename}

    #::::::::::::::::::::::::::-
    #NAME: profilename
    #::::::::::::::::::::::::::-
    profilename=${profilename}

    #::::::::::::::::::::::::::-
    #NAME: dmgr_host
    #DESC: The Deployment manager host
    #EXAMPLE: dmgr_host=axtcci001
    #::::::::::::::::::::::::::-
    dmgrhost=${dmgrhost}

    #::::::::::::::::::::::::::-
    #NAME: dmgr_port
    #DESC: Deployment manager SOAP Port
    #DEFAULT: 10878
    #::::::::::::::::::::::::::-
    dmgrport=${dmgrport}

    #::::::::::::::::::::::::::-
    #NAME: dmgrnodename
    #DESC: The name of the dmgr node
    #FORMAT: CCI%init.properties.cat%%init.properties.envid%CellNode001%
    #EXAMPLE: CCITstMP4CellNode001
    #::::::::::::::::::::::::::-
    dmgrnodename=${WS_DMGR_NODE}

    #::::::::::::::::::::::::::-
    #NAME: backupnodename
    #DESC: The name of the backupnode
    #ALLOWED : backupNode1, backupNode2
    #::::::::::::::::::::::::::-
    backupnodename=${backupnodename}

    #::::::::::::::::::::::::::-
    #NAME: serveralias
    #DESC: The name of the WAS server
    #EXAMPLE : BET-CCIWAS001
    #::::::::::::::::::::::::::-
    serveralias=${serveralias}

    #::::::::::::::::::::::::::-
    #NAME: was_home
    #DESC: The WebSphere installation directory
    #DEFAULT: /opt/WebSphere/AppServer
    #::::::::::::::::::::::::::-
    was_home=${WS_INSTALL_DIR}

    #::::::::::::::::::::::::::-
    #NAME: was_config
    #DESC: The WebSphere configuration directory
    #EXAMPLE: /opt/WebSphere/AppServer/profiles/CCIDmgrProfile/config/
    #::::::::::::::::::::::::::-
    was_config=${WS_INSTALL_CONFIG_DIR}

    #::::::::::::::::::::::::::-
    #NAME: itsa_base_dir
    #DESC: ITSA scripts base directory
    #STATIC VALUE
    #::::::::::::::::::::::::::-
    itsa_base_dir=${itsa_base_dir}

    #::::::::::::::::::::::::::-
    #NAME: itsa_base_dir
    #DESC: Log4j property file location
    #STATIC VALUE
    #::::::::::::::::::::::::::-
    Log4j_Prop_File=${itsa_log4j_props_file}

    #::::::::::::::::::::::::::-
    #EXAMPLE: P.0001CLPROD0001P.0001SVPROD0001
    #::::::::::::::::::::::::::-
    mq_secexit_init_token=${WS_MQ_SECEXIT_INIT_TOKEN}


    #:::::::::::::::::::::::::::
    # NAME: auth_service_name
    # DESC: the name of the Java framework Authentication application
    # ALLOWED: AuthServiceIntEAR, AuthServiceExtEAR
    #:::::::::::::::::::::::::::
    auth_service_name=${WS_FM_AUTH_APPNAME}

    """

print InitProperties,getvarset()
