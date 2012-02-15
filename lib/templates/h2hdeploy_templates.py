
from itsalib.template import StaticITSATemplate

__all__ = [
        'StaticITSATemplate',
        'DeployScriptTemplate',
        'RunMQTemplate',
        'StartCTGTemplate',
        'BackupScriptTemplate',
        'UndoBackupScriptTemplate',
        ]

class DeployScriptTemplate(StaticITSATemplate):
    '''
    #!/usr/bin/ksh

    envid={{envid:+py:envid.lower()}}
    appdir={{appdir:-/data/env}}
    curdir=`pwd`

    if [ -d $envid ]
    then
        echo "copying directory $curdir/$envid to $appdir/$envid"
        cp -r $envid $appdir
        echo "changing permissions of all files in $appdir/$envid to 755"
        chmod -R 755 $appdir/$envid
        echo "cleaning up."
        rm -rf $envid
        echo "done."
    fi

    exit $?
    '''

class RunMQTemplate(StaticITSATemplate):
    '''
    #!/usr/bin/ksh

    mqscript={{mqscript}}
    mqman="{{mqmanager:+%(mqmanager)s}}"
    appdir="{{appdir:-/data/env}}"
    momconfig="${appdir}/{{envid}}/{{subproj:+%(subproj)s/}}run/mom/config/EbMomConfig.xml"

    echo "MOM config file is: $momconfig"

    if [ "$mqman" == "" ]
    then
        mqman=`dspmq | sed "s/^QMNAME(//;s/).*//"`
        echo "Queue manager is: $mqman"
        echo "Updating file: $momconfig"
        echo "Replacing '#PARAM_QUEUE_MANAGER#' with '$mqman'"
        sed "s/#PARAM_QUEUE_MANAGER#/$mqman/g" $momconfig > out.xml
        mv out.xml $momconfig
        echo "Done."
    fi

    echo "Running MQ script: $mqscript"
    echo "Queue manager: $mqman"
    runmqsc $mqman < $mqscript > mqout.log
    echo "Done. Log: mqout.log"

    exit $?
    '''


class StartCTGTemplate(StaticITSATemplate):
    '''
    #!/usr/bin/ksh

    ctgini="ctg.ini"
    ctgsect={{ctgsection}}
    echo "Copying $ctgini"
    cp $ctgini /var/cicscli
    echo "Starting CTG client daemon."
    echo "Command is: cicscli -s=$ctgsect"
    cicscli -s=$ctgsect
    echo "Displaying started daemon."
    cicscli -l

    exit $?
    '''

class BackupScriptTemplate(StaticITSATemplate):
    '''
    #!/usr/bin/sh

    appdir={{appdir:-/data/env}}
    envid={{envid}}

    envdir=${appdir}/${envid}

    archive="$envid-backup.tar"

    echo "Backing up directory $envdir"

    tar cvf $archive $envdir

    if [ $? != 0 ]
    then
        echo "ERROR: couldn't backup directory $envdir"
        exit 1
    fi

    echo "Deleting $envdir"

    for f in `find $envdir ! \( -name "setenv.sh" -o -name "MomDrv.sh" -o -name "cgrep.sh" \)`
    do
        if [ -f $f ]
        then
            echo "deleting $f"
            rm -f $f
        fi
    done

    echo "Directory $envdir has been archived here: $archive"
    echo "All files that were in $envdir have been deleted except for:"
    echo "    - setenv.sh"
    echo "    - MomDrv.sh"
    echo "    - cgrep.sh"
    echo "Finished."

    exit $?

    '''

class UndoBackupScriptTemplate(StaticITSATemplate):
    '''
    #!/usr/bin/sh

    appdir={{appdir:-/data/env}}
    envid={{envid}}

    envdir=${appdir}/${envid}

    archive="$envid-backup.tar"

    echo "Copying file $archive to $appdir"
    cp $archive $appdir
    curdir=`pwd`
    echo "changing directory to $appdir"
    cd $appdir
    if [ -d $envid ]
    then
        echo "removing directory $envid and everything in it."
        rm -rf $envid
    fi
    echo "untarring $archive"
    tar xvf $archive
    echo "changing directory to $curdir"
    cd curdir
    echo "Finished."

    exit $?

    '''

