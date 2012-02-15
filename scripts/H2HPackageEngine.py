###########################################################################################
#	H2HPackageEngine.py
#	H2H/WTX Deployment engine for packaging and creating deployment release
#
#	Mahesh Devendran, WebSphere Support, PIU Team
#	Copyright(c) 2010, Euroclear 
############################################################################################

import os
import os.path
import sys
import re
from os import File
from sys import path
from optparse import OptionParser
from org.apache.log4j import *
from datetime import date
import time
from util import createPropertyMap
from util import validateEnvid
from util import validateProject

global h2hprops, propertyMap
h2hprops = {}
propertyMap = {}

execfile("scripts" + File.separator + "PackagingManager.py")
execfile("scripts" + File.separator + "PIULogger.py")
execfile("scripts" + File.separator + "CONSTANTS.py")

			

##########################################
# getPropertyFile
# retrieve property file
#########################################
def getPropertyFile(propertyFile, defaultPropertyFile, envid):
	if propertyFile == None:
		propertyFile = PROPERTIESFOLDER + File.separator + envid + "_" + defaultPropertyFile

	if propertyFile != None and not os.path.exists(propertyFile):
		print "\n******** properties file %s does not exist *********\n" % propertyFile
		sys.exit()

	return propertyFile
	
##########################################
# getEnvID
# get envid from property file
#########################################
def getEnvID(propertyFile):
	propertyFileHandle = open(propertyFile)
	for props in propertyFileHandle:
		found = props.strip().find(KYENVID)
		if props != None and found != -1:
			if found == 0:
				envid = props.rstrip("\n").split("=")[1].strip()
				envid = envid.strip("#")
				h2hprops[KYENVID] = envid
				propertyFileHandle.close()
				return envid
	print "\n***** Missing environment ID in the properties file *****\n"
	sys.exit(1)

##########################################
# deleteOldLogFiles
# Housekeep log files
##########################################
def deleteOldLogFiles(daysOld, envid):
	logPath=os.sys.currentWorkingDir + File.separator + LOGDIRNAME
	difference = time.time() - int(daysOld) * 86400
	startsWith = envid
	for file in os.listdir(logPath):
		if os.path.isfile(file) and file.find(startsWith) == 0:
			if os.stat(file).st_mtime < difference:
				print "Removing file %s which is older by %s in seconds" % (file, str(os.stat(file).st_mtime))
				os.remove(os.path.join(logPath, file))
	print "\n*** Completed housekeeping logfiles ***\n"

def checkAction(options):
	if options.mqCheckList != None or options.packagingCheck != None or options.momDeploy != None:
		if options.momDeploy != None:
			for action in options.momDeploy.split(":"):
				if not action.lower() in "so:maps:config:fwk":
					print "\n*** unknown action %s ***\n" % action 
					printHelp(argParser)
					sys.exit(1)					
		return
	print "\n****incorrect or missing action****\n"
	print "\n****packaging action required in the command line****\n"
	printHelp(argParser)
	sys.exit(1)	
	
def printHelp(argParser):
	argParser.print_help()
	print "\nExample(s):\n"
	print "for MQ checklist only, run \n\th2hpackage.bat -e <envid> -q"
	print "for mom fwk only, run \n\th2hpackage -e <envid> -f"
	print "for mom application only, run \n\th2hpackage -e <envid> -c"
	print "for mom application with fwk, run \n\th2hpackage -e <envid> -cf"
	print "for mom application with MQ Checklist, run \n\th2hpackage -e <envid> -cq"
	print "for full deployment, run \n\th2hpackage -e <envid> -cqf"

if __name__=='__main__':
	argParser = OptionParser(usage="usage: h2hpackage [options]")
	argParser.add_option("-e", "--envid", action="store", dest="envid", default = None, help="environment id - Mandatory argument")
	argParser.add_option("-q", "--mqCheckList", action="store_true", dest="mqCheckList", default=False, help="package for MQ Checklist only")
	argParser.add_option("-c", "--momDeploy", action="store_true", dest="momDeploy", default=False, help="package for mom deployment")
	argParser.add_option("-f", "--fwkDeploy", action="store_true", dest="fwkDeploy", default=False, help="package for framework")
	argParser.add_option("-d", "--debug", action="store_true", default=False, dest="debug", help="run in debug")
	argParser.add_option("-p", "--project", action="store", default = None, dest="project", help="define project to use: SP|ESES")
	
	(options,args) = argParser.parse_args(sys.argv)

	if options.envid == None or options.project == None or options.mqCheckList == False and options.momDeploy == False and options.fwkDeploy == False:
		printHelp(argParser)
		sys.exit()

	envid = options.envid.lower()
	project = options.project.upper()
	propertyFile = getPropertyFile('config/request/' + envid + '_' + project + '_h2hpackage.properties', PACKAGEPROPERTYFILE, envid)
	
	createPropertyMap()
	validateEnvid(envid)
	#if options.daysOlder != None and int(options.daysOlder) > 0:
	#	deleteOldLogFiles(options.daysOlder, envid)
	#	sys.exit(1)

	#checkAction(options)
        packcom = ""
        if (options.momDeploy):
		packcom = packcom + "c"

	if (options.mqCheckList):
		packcom = packcom + "q"

	if (options.fwkDeploy):
                packcom = packcom + "f"
	
	h2hprops[KYUNIQUEPACKAGEID] = packcom + "-" + str(date.today()) + "_" + time.strftime("%H-%M-%S-%Z", time.localtime()) + "_" + os.environ["USERNAME"]
	logPrefix = envid
	initLogger(logPrefix, project, options.debug)	
	h2hprops[KYPIUH2HDIR] = os.sys.currentWorkingDir
	h2hprops[KYENVID] = envid
	h2hprops[KYPARAM_QENV] = envid.upper()
	h2hprops[KYPROJECT] = project
	print h2hprops
	executePackaging(propertyFile, envid, options)
	

