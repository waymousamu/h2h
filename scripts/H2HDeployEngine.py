###########################################################################################
#	H2HDeployEngine.py
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
from util import createPropertyMap
from util import validateEnvid
from util import validateProject

global h2hprops, propertyMap
h2hprops = {}
propertyMap = {}

execfile("scripts" + File.separator + "DeployManager.py")
execfile("scripts" + File.separator + "PIULogger.py")
execfile("scripts" + File.separator + "CONSTANTS.py")


def _isValidArg(arg):
	if arg == None or arg =="":
		return False
	return arg


##########################################
# getPropertyFile
# retrieve property file
#########################################
def getPropertyFile(propertyFile, envid, project):
	from util import removeCM
	if propertyFile == None or propertyFile == "":
		if h2hprops.get(KYPACKAGE_LOCATION) != None:
			propertyFile = h2hprops.get(KYPACKAGE_LOCATION) + File.separator + PROPERTIESFOLDERNAME + File.separator + envid + "_" + project + "_" + DEPLOYPROPERTYFILE
			removeCM(propertyFile)
			return propertyFile
		else:
			print "\n***Property file argument missing  or Tarfile not passed***\n"
			sys.exit(1)
	
	if propertyFile != None and not os.path.exists(propertyFile):
		print "\n***Property file %s does not exist***\n" % propertyFile
		sys.exit(1)
	removeCM(propertyFile)
	return propertyFile

##########################################
# processTarFile
# process PIDCR tar file
#########################################
def processTarFile(argParser, options):
	if options.tarFile == None:
		if options.runFromLocation != None and options.runFromLocation != "":
			tf = os.path.abspath(options.runFromLocation)
			if os.path.exists(tf):
				print "\n*** performing deployment from %s ****" % tf
				h2hprops[KYPACKAGE_LOCATION] = tf
				return
				
		if _isValidArg(options.fullDeployment) or _isValidArg(options.deployH2H) or (_isValidArg(options.deployMQ) and options.propertyFile == None):
			print "\n***TarFile is mandatory argument for the request***\n"

			printHelp(argParser)
			argParser = None
			args = None
			sys.exit()
	else:
		tf = os.path.abspath(options.tarFile)
		if not os.path.exists(tf):
			print "\n***** Tar file %s not present or not accessible\n" % options.tarFile
			sys.exit()		
		untarDeployPackage(tf, options.envid)	

def _checkAction(options):
	if options.fullDeployment or options.createTargetDirs or options.installMOMFwk or options.deployH2H or options.deployMQ or options.precheck or options.daysOlder:
		return True
	return False

def printHelp(argParser):
	argParser.print_help()
	print "\nExample(s):\n"
	print "for deployment precheck only, run \n\th2hdeploy.ksh -e <envid> -P <project> -t <tarFile> -i"
	print "for MQ checklist, run \n\th2hdeploy.ksh -e <envid> -P <project> -t <tarFile> -q"
	print "for mom fwk, run \n\th2hdeploy -e <envid> -P <project> -t <tarFile> -m"
	print "for creating target directories, run \n\th2hdeploy -e <envid> -P <project> -t <tarFile> -s"
	print "for deploying H2H(creates target directories if not present), run \n\th2hdeploy -e <envid> -P <project> -t <tarFile> -H"
	print "for MQ deployment, run \n\th2hdeploy -e <envid> -P <project> -t <tarFile> -q"
	print "for full dployment, run \n\th2hdeploy -e <envid> -P <project> -t <tarFile> -F"
	print "for deployment from a package location, run \n\th2hdeploy -e <envid> -P <project> -l <package dir> -F"

##########################################
# deleteOldLogFiles
# Housekeep log files
##########################################
def deleteOldLogFiles(daysOld, envid, project):
	logPath=os.sys.currentWorkingDir + File.separator + LOGDIRNAME
	difference = time.time() - int(daysOld) * 86400
	startsWith = envid + "_" + project
	for file in os.listdir(logPath):
		if os.path.isfile(file) and file.find(startsWith) == 0:
			if os.stat(file).st_mtime < difference:
				print "Removing file %s which is older by %s in seconds" % (file, str(os.stat(file).st_mtime))
				os.remove(os.path.join(logPath, file))
	print "*** Completed housekeeping logfiles ***\n"
	
if __name__=='__main__':
	argParser = OptionParser(usage="usage: h2hdeploy.ksh [options]")
	argParser.add_option("-p", "--propertyFile", action="store",	dest="propertyFile", help="deployment packaging property file")
	argParser.add_option("-e", "--envid", action="store", dest="envid", help="environment id for deployment - Mandatory argument")
	argParser.add_option("-P", "--project", action="store", dest="project", help="project - Mandatory argument")
	argParser.add_option("-t", "--tarFile", action="store", dest="tarFile", help="deployment tar file")
	argParser.add_option("-l", "--runFromLocation", action="store", dest="runFromLocation", help="perform deployment from source folder")
	argParser.add_option("-f", "--fullDeployment", action="store_true", dest="fullDeployment", help="perform full deployment")
	argParser.add_option("-s", "--createTargetDirs", action="store_true", dest="createTargetDirs", help="create direcrory structure for deployment")
	argParser.add_option("-m", "--installMOMFwk", action="store_true", dest="installMOMFwk", help="perform MOM framework installation")
	argParser.add_option("-H", "--deployH2H", action="store_true", dest="deployH2H", help="perform H2H deployment")
	argParser.add_option("-q", "--deployMQ", action="store_true", dest="deployMQ", help="perform MQSC deployment")
	argParser.add_option("-i", "--precheck", action="store_true", dest="precheck", help="perform pre checks")
	argParser.add_option("-r", "--daysOlder", action="store", dest="daysOlder", help="remove the logs older than <daysOlder> days for the environment and project e.g. 7")
	argParser.add_option("-d", "--debug", action="store_true", dest="debug", help="run in debug")

	(options,args) = argParser.parse_args(sys.argv)

	if not args and not option:
		printHelp(argParser)
		argParser = None
		args = None
		option = None
		sys.exit()
		
	if options.envid == None and options.project == None:
		print "\n***Envid and project are mandatory arguments***\n"
		printHelp(argParser)
		argParser = None
		args = None
		option = None
		sys.exit()
	
	h2hprops[KYPIUH2HDIR] = os.sys.currentWorkingDir
	createPropertyMap()
	validateEnvid(options.envid)
	validateProject(options.project)
	if not _checkAction(options):
		print "\n***Specify the action to perform <-f|-s|-m|-H|-q|-i|-r>***\n"
		printHelp(argParser)
		sys.exit(1)

	logPrefix = options.envid + "_" + options.project + "_" + str(date.today()) + "_" + time.strftime("%H-%M-%S", time.gmtime())
	initLogger(logPrefix, options.debug)

	if options.daysOlder != None and int(options.daysOlder) > 0:
		print "NOTE: Only housekeeping will be performed, All other requests are ignored"
		deleteOldLogFiles(options.daysOlder, options.envid, options.project)
		sys.exit(1)
		
	processTarFile(argParser, options)
	propertyFile = getPropertyFile(options.propertyFile, options.envid, options.project)
	
	executeDeployment(propertyFile, options)
	
	if not options.precheck:
		logInfo("\n\t******************************" +
			"\n\tReview the deployment performed! Items not supported for now" +
      "\n\t2. HACMP" +
      "\n\t***************************************************************", deployManagerLogger)


	argParser = None
	args = None
	option = None
	
