###########################################################################################
#	H2HRelease.py
#	H2H/WTX Deployment engine for packaging and creating deployment release
#
#	Mahesh Devendran, WebSphere Support, PIU Team
#	Copyright(c) 2010, Euroclear 
############################################################################################

import os
import os.path
import sys
from os import File
from sys import path
from optparse import OptionParser
from org.apache.log4j import *
from datetime import date
import time
import tarfile

execfile("scripts" + File.separator + "CONSTANTS.py")
execfile("scripts" + File.separator + "PIULogger.py")
initLogger("PIUH2HRelease")	
h2hReleaseLogger = Logger.getLogger("H2HRelease.py")
execfile("scripts" + File.separator + "util.py")

def createDeployPackageTARFile(releaseLocation):
	logInfo("PIUH2H Release %s\n******************************************\n" % (str(date.today())), h2hReleaseLogger)
	version = open(VERSIONFILE).read()
	packageParts = [
				LIBFOLDER,
				PROPERTIESFOLDERNAME + File.separator + LOG4JPROPERTIESFILE,
				PROPERTIESFOLDERNAME + File.separator + VALIDATIONPROPERTIESFILE,
				PROPERTIESFOLDERNAME + File.separator + PIUH2HPROPERTIESFILE,
				SCRIPTFOLDER,
				DEPLOYH2HFILE,
				RELEASEFILE,
				VERSIONFILE
				]
	if version == None:
		logError("Version details not found", h2hReleaseLogger)
		sys.exit(1)
	logInfo("Version : %s\n" % version, h2hReleaseLogger)				
	tarFileName = releaseLocation + File.separator + DEPLOYPACKAGENAME + "_" + version + TARGZEXT
	createDeployTar(packageParts, tarFileName)
	logInfo("created tar file %s" % tarFileName, h2hReleaseLogger)
	logInfo("\n******************************************\nCompleted PIUH2H Release\n", h2hReleaseLogger)
	logInfo("For release details see Release.txt", h2hReleaseLogger)
	logInfo("\n---------------------------------------------------------------------------------------", h2hReleaseLogger)

if __name__=='__main__':
	argParser = OptionParser(usage="usage: piuh2h [options]")
	argParser.add_option("-r", "--releaseLocation", 
												action="store", dest="releaseLocation", help="release location to create the piuh2h release")
	
	(options,args) = argParser.parse_args(sys.argv)

	if not args and not option:
		argParser.print_help()
		sys.exit()
	if options.releaseLocation == None:
		logWarn("*** release location not passed ***", h2hReleaseLogger)
		argParser.print_help()
	else:
		createDeployPackageTARFile(options.releaseLocation)
