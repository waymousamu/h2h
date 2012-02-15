###########################################################################################
#	util.py
#	Utility script 
#
#	Mahesh Devendran, WebSphere Support, PIU Team
#	Copyright(c) 2010, Euroclear 
############################################################################################

from org.apache.log4j import *
import sys
import re
import os
from datetime import date
import time
import string
from sys import path
import tarfile
import commands
from os import File

execfile("properties" + File.separator + "piuh2h.properties")
execfile("scripts" + File.separator + "CONSTANTS.py")
execfile("scripts" + File.separator + "PIULogger.py")

utilLogger = getLogger("util.py")

def getUserAcceptance(acceptedValues):
        logDebug(">>>acceptedValues", utilLogger)
	char = sys.stdin.read(1).lower()
	if char in acceptedValues.lower():
		# clear the buffer as stdin.flush 
		throwaway = sys.stdin.readline()
		logDebug("<<<acceptedValues", utilLogger)
		return char
	else:
		if char != '\n':
			print "%s is not acceptable, Enter a accepted value - %s :" % (char,acceptedValues)
		logDebug("<<<acceptedValues", utilLogger)
		return getUserAcceptance(acceptedValues)
			
##############################################
# getVar
# get variable
##############################################
def getVar(var):
        logDebug(">>>getVar", utilLogger)
	if var:
                logDebug("var: %s" % var, utilLogger)
                logDebug("<<<getVar", utilLogger)
		return var
	else:
                logDebug("var: NONE", utilLogger)
                logDebug("<<<getVar", utilLogger)
		return ""
		
##############################################
# displayDeploymentSummary
# display deployment summary
##############################################
def displayDeploymentSummary():
        logDebug(">>>displayDeploymentSummary", utilLogger)
	if utilLogger.getEffectiveLevel() == Level.INFO:
		deploymentStr = [
									"\tEnvironment        :" + h2hprops.get(KYENVID), 
									"\tProject            :" + h2hprops.get(KYPROJECT), 
									"\tCCI Version        :" + getVar(h2hprops.get(KYCCI_VERSION)),
									"\tMOM Version        :" + getVar(h2hprops.get(KYMOM_VERSION)), 
									"\tChecklist Version  :" + getVar(h2hprops.get(KYMQCHECKLIST_VERSION))
									]
		logInfo("\n\n*************************************************\n" +
						"\n\tDeployment Properties \n\n\t---------------------\n" +	
						"\n".join(deploymentStr) +
						"\n\n*************************************************\n", utilLogger)
	logDebug("<<<displayDeploymentSummary", utilLogger)

##############################################
# getChkListVersion
# get checklist versions
##############################################
def getChkListVersion():
        logDebug(">>>getChkListVersion", utilLogger)
	chklistfiles = h2hprops.get(KYMQCHKLISTFILES).split(",")
	allVersions = None
	for chklist in chklistfiles:		
		cciVersion = chklist.strip("\"").strip(".xls").split("v",1)[1].split()[0]
		logDebug("cciVersion: %s" % cciVersion, utilLogger)
		fileParts = chklist.strip('\"').strip(".xls").split()
		logDebug("fileParts: %s" % fileParts, utilLogger)
		version = cciVersion + "_" + fileParts[len(fileParts) - 1]
		logDebug("version: %s" % version, utilLogger)
		if allVersions == None:
			allVersions = version
		else:
			allVersions = allVersions + "," + version
	logDebug("MQVersions are %s" % allVersions, utilLogger)
	h2hprops[KYMQCHECKLIST_VERSION] = allVersions
	logDebug("<<<getChkListVersion", utilLogger)

##############################################
# isPropertyAvailable
# is the property valid
##############################################
def isValidProperty(propertyName, propertyValue):
        logDebug(">>>isValidProperty", utilLogger)
        logDebug("propertyName: %s " % propertyName, utilLogger)
	validationString = propertyMap.get(propertyName)
	if validationString == None:
		logWarn("Property %s not recognised" % propertyName, utilLogger)
		logDebug("<<<isValidProperty", utilLogger)
		return True
	acceptedValues = validationString.split(":")[2].strip()
	if acceptedValues != "ANY":
		values = acceptedValues.split("|")		
		if propertyName == KYTARGETHOSTNAMES:
			newValue = propertyValue.split(",")			
			for v in newValue:
				if not v in values:
					logError("PropertyName %s PropertyValue %s not recognised" % (propertyName, propertyValue), utilLogger)
					logError("Valid Values : %s " % acceptedValues, utilLogger)
					logDebug("<<<isValidProperty", utilLogger)
					return False
		else:
			if not propertyValue.strip() in values:
				logError("PropertyName %s PropertyValue %s not recognised" % (propertyName, propertyValue), utilLogger)
				logError("Valid Values : %s " % acceptedValues, utilLogger)
				logDebug("<<<isValidProperty", utilLogger)
				return False
	logDebug("<<<isValidProperty", utilLogger)
	return True

##############################################
# backupPropertiesFile
# backup properties file
##############################################
def backupPropertiesFile(processedPropertyFile):
        logDebug(">>>backupPropertiesFile", utilLogger)
	copyfile(h2hprops.get(KYPROPERTIESFILE), processedPropertyFile)
	#os.remove(h2hprops.get(KYPROPERTIESFILE))
	logDebug("<<<backupPropertiesFile", utilLogger)

##############################################
# replaceVars
# replace variables
##############################################
def replaceVars(property):
        logDebug(">>>replaceVars", utilLogger)
	value = h2hprops.get(property)
	logDebug("value: %s " % value, utilLogger)
	if value.find("!!") > -1:
			var = value.split("!!")
			if not isPropertyAvailable(h2hprops.get(var[1])):
				logError("value for %s not available to set the property %s " % (var[1], property), utilLogger)
			value = value.replace("!!" + var[1] + "!!", h2hprops.get(var[1]))
			h2hprops[property] = value	
			replaceVars(property)
			logDebug("<<<replaceVars", utilLogger)
	else:
                logDebug("<<<replaceVars", utilLogger)
		return

##########################################
# validateEnvid
# is envid valid
# envid - environment id 
#########################################
def validateEnvid(envid):
        logDebug(">>>validateEnvid", utilLogger)
	validEnvIDs = propertyMap.get(KYENVID).split(":")[2].strip()
	if not envid in validEnvIDs.split("|"):
		print "***** INVALID ENVID PASSED or MISSING ENVID *****\nSupported Environments are : %s " % validEnvIDs
		sys.exit(1)
	logDebug("<<<validateEnvid", utilLogger)

##########################################
# validateProject
# is project valid
#########################################
def validateProject(project):
        logDebug(">>>validateProject", utilLogger)
	validProjects = propertyMap.get(KYPROJECT).split(":")[2].strip()
	if not project in validProjects.split("|"):
		print "***** INVALID PROJECT PASSED OR MISSING PROJECT VALUE*****\nSupported projects are : %s " % validProjects
		sys.exit(1)
	logDebug("<<<validateProject", utilLogger)

##########################################
# createPropertyMap
# create property map for validations
#########################################
def createPropertyMap():
        logDebug(">>>createPropertyMap", utilLogger)
	validationPropsFile = "properties" + File.separator + "validation.properties"
	vph=open(validationPropsFile,"r")
	for line in vph:
		if len(line.strip()) > 1 and re.match("^#",line[0]) == None:
			tup = line.strip().split("=")
			if tup[0].strip() not in propertyMap:
				propertyMap[tup[0].strip()] =  tup[1].strip().rstrip("\"").rstrip("\'")
	logDebug("<<<createPropertyMap", utilLogger)

##############################################
# isPropertyAvailable
# is the property valid
##############################################
def isPropertyAvailable(property, basePath=None):
        logDebug(">>>isPropertyAvailable", utilLogger)
        logDebug("Property: %s" %property, utilLogger)
	if property == None or property =="":
                logDebug("<<<isPropertyAvailable", utilLogger)
		return False
	if basePath != None and not os.path.exists(basePath + File.separator + property):
                logDebug("<<<isPropertyAvailable", utilLogger)
		return False
	logDebug("<<<isPropertyAvailable", utilLogger)
	return True

##############################################
# loadProperties
# load properties from properties file
##############################################
def loadProperties(propsFile):
        logDebug(">>>loadProperties", utilLogger)
	logInfo("Loading properties file %s" % (propsFile), utilLogger)
	h2hprops[KYPROPERTIESFILE]=propsFile
	multiLineProperty = False
	propertyFile = None
	try:
		propertyFile = open(propsFile)
	except IOError:
		errorMesg = "IO Error (not found/corrupt file/disk issue/etc) \n*** while opening file %s" % propsFile
		logError(errorMesg, utilLogger)
		sys.exit(1)
		
	for props in propertyFile:
		if len(props.strip()) > 1 and re.match("^#",props[0]) == None:
			if props.find('[[') > -1: # Multiline value
				multiLineProperty = True
				multiLineName = props.rstrip("\n").split("=")[0].strip()
				multiLineValue = ""
				continue
			if multiLineProperty:
				if multiLineName in EOCTFPROPERTIES:
					value = props
				else:
					value = props.strip()
				if props.find(']]') > -1:
					multiLineProperty = False
					if isValidProperty(multiLineName,multiLineValue):
						h2hprops[multiLineName] = multiLineValue
						logDebug("(multiLineName = multiLineValue) loaded = (%s = %s)" % (multiLineName,multiLineValue), utilLogger)
					else:
						sys.exit(1)
				else:
					multiLineValue = multiLineValue + value
			else:
				property=props.rstrip("\n").split("=")
				name = property[0].strip()
				value = property[1].rsplit("#")[0].strip()
				if value.find("!!") > -1:
					h2hprops[name] = value
				else:					
					if isValidProperty(name,value):
						h2hprops[name] = value
						logDebug("(name = value) loaded = (%s = %s)" % (name,value), utilLogger)
					else:
						logError("%s with value %s is not a valid property" %(name,value), utilLogger)
						sys.exit(1)
	targetBackupDir = h2hprops.get(KYTARGETBACKUPDIR)
	if targetBackupDir == None or targetBackupDir.strip() == "":
		targetBackupDir = h2hprops.get(KYTARGETDIRPATTERN)+ "/" + TARGETBACKUPDIR
		h2hprops[KYTARGETBACKUPDIR] = targetBackupDir
	h2hprops[KYPROPERTYFILE] = propsFile
	propertyFile.close()
	
	for props in h2hprops:
		replaceVars(props)
	logDebug("<<<loadProperties", utilLogger)
		
def _samefile(src, dst):
  logDebug(">>>_samefile", utilLogger)
  if hasattr(os.path,'samefile'):
    try:
      logDebug("<<<_samefile", utilLogger)
      return os.path.samefile(src, dst)
    except OSError:
      logDebug("<<<_samefile", utilLogger)
      return False
  logDebug("<<<_samefile", utilLogger)
  return (os.path.normcase(os.path.abspath(src)) ==
          os.path.normcase(os.path.abspath(dst)))

##############################################
# copyfile
# copy file
##############################################
def copyfile(src, dst):
        logDebug(">>>copyfile", utilLogger)
	logDebug("copying %s to %s" % (src,dst), utilLogger)
	if _samefile(src, dst):
		raise Error, "`%s` and `%s` are the same file" % (src, dst)
	fsrc = None
	fdst = None
	try:
		fsrc = open(src, 'rb')
		fdst = open(dst, 'wb')
		while 1:
			buf = fsrc.read(FILEREADBYTES)
			if not buf:
				break
			fdst.write(buf)
	finally:
		if fdst:
			fdst.close()
		if fsrc:
			fsrc.close()
	logDebug("<<<copyfile", utilLogger)

##############################################
# copyDir
# copy directory
##############################################
def copyDir(srcDir,dstDir):
        logDebug(">>>copyDir", utilLogger)
	if os.path.exists(srcDir):
		for file in os.listdir(srcDir):
			srcFile = srcDir + File.separator + file
			dstFile = dstDir + File.separator + file
			if os.path.isdir(srcFile):
				if not os.path.exists(dstFile):
					os.makedirs(dstFile)
				copyDir(srcFile, dstFile)
			else:
				copyfile(srcFile,dstFile)
	logDebug("<<<copyDir", utilLogger)

##############################################
# getFileNameFromURL
# get file name from URL
##############################################
def getFileNameFromURL(urlString):
        logDebug(">>>getFileNameFromURL", utilLogger)
	urlParts = urlString.split("\\")
	if len(urlParts) > 1:
                logDebug("<<<getFileNameFromURL", utilLogger)
		return urlParts[len(urlParts) - 1]
	else:
                logDebug("<<<getFileNameFromURL", utilLogger)
		return urlString

##############################################
# createDeployTar
# create deploy TAR
##############################################
def createDeployTar(packageParts, tarFileName):
        logDebug(">>>createDeployTar", utilLogger)
	if os.path.exists(tarFileName):
		oldTarFile = tarFileName.strip(TARGZEXT) + "_" + str(date.today()) + "_" + time.strftime("%H-%M-%S", time.gmtime()) + TARGZEXT
		os.rename(tarFileName, oldTarFile)
		
	tar = tarfile.TarFile.open(name=tarFileName, mode='w:gz')
	for item in packageParts:
		tar.add(item)
	tar.close()
	logDebug("<<<createDeployTar", utilLogger)

##############################################
# unTarPackage
# untar package
##############################################
def unTarPackage(tarFile, targetLocation):
        logDebug(">>>unTarPackage", utilLogger)
	curWorkDir = os.sys.currentWorkingDir
	os.chdir(targetLocation)
	cmdToRun = GUNZIPCMD + " " + tarFile
	logInfo("untaring package : %s " % cmdToRun, utilLogger)
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
	logInfo("exit status is %s, result is %s" % (exitstatus,result), utilLogger)

	cmdToRun = UNTARCMD + " " + tarFile.strip(".gz")
	logInfo("untaring package : %s " % cmdToRun, utilLogger)
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
	logInfo("exit status is %s, result is %s" % (exitstatus,result), utilLogger)

	os.chdir(curWorkDir)
	logDebug("<<<unTarPackage", utilLogger)

def removeCM(srcFile):
        logDebug(">>>removeCM", utilLogger)
	logDebug("removing ^M chars from the file %s" % srcFile, utilLogger)

	cmdToRun = "tr -d \"\\015\\032\" < " + srcFile + " > t"
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
	logInfo("Result : %s "% result, utilLogger)

	cmdToRun = "mv t " + srcFile
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
	logInfo("Result : %s "% result, utilLogger)
	logDebug("<<<removeCM", utilLogger)
	
##############################################
# getBackupFile
# get backup file
##############################################
def getBackupFile(backupDir, backupCount):
        logDebug(">>>getBackupFile", utilLogger)
	backedUpFiles = []
	backupFilePrefix = backupDir + File.separator + h2hprops.get(KYCCI_VERSION) 
	for file in os.listdir(backupDir):
		if file.find(h2hprops.get(KYCCI_VERSION) + "_") > -1 and file.find(TARGZEXT) > -1:
			backedUpFiles.append(backupDir + File.separator + file)
	backedUpCount = len(backedUpFiles)	
	if backedUpCount >= backupCount:		
		for file in backedUpFiles[backupCount - 1:backedUpCount]:
			os.remove(file)
	logDebug("<<<getBackupFile", utilLogger)
	return backupFilePrefix + "_" + str(date.today()) + "_" + time.strftime("%H-%M-%S", time.gmtime()) + TAREXT

def performDeploymentBackup(backupFile):
        logDebug(">>>performDeploymentBackup", utilLogger)
	curWorkDir = os.sys.currentWorkingDir
	os.chdir(h2hprops.get(KYTARGETDIRPATTERN))
	
	cmdToRun = TARCMD + " " + backupFile + " " + h2hprops.get(KYCCI_VERSION)
	logInfo("Running -> %s" % cmdToRun, utilLogger)
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
	logInfo("exitStatus is %s" % exitstatus, utilLogger)
	logInfo("result is %s" % result, utilLogger)
	
	cmdToRun = GZIPCMD + " " + backupFile
	logInfo("Running -> %s" % cmdToRun, utilLogger)
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
	logInfo("exitStatus is %s" % exitstatus, utilLogger)
	logInfo("result is %s" % result, utilLogger)
	
	os.chdir(curWorkDir)
        logDebug("<<<performDeploymentBackup", utilLogger)
				
##############################################
# backupDeployedRelease
# backup deployed release
##############################################
def backupDeployedRelease():
        logDebug(">>>backupDeployedRelease", utilLogger)
	logInfo("performing backing up of existing H2H deployment...", utilLogger)
	backupDir = h2hprops.get(KYTARGETBACKUPDIR) + File.separator + h2hprops.get(KYCCI_VERSION) 
	
	if not os.path.exists(backupDir):
		os.makedirs(backupDir)
		logDebug("<<<backupDeployedRelease", utilLogger)
		return
	
	if isPropertyAvailable(h2hprops.get(KYTARGETBACKUPNOS)):
		backupCount = h2hprops.get(KYTARGETBACKUPNOS)
	else:
		backupCount = MINBACKUPS
	backupFile = getBackupFile(backupDir, backupCount)
	performDeploymentBackup(backupFile)
	logDebug("<<<backupDeployedRelease", utilLogger)
	
def performPostDeploymentBackup():
        logDebug(">>>performPostDeploymentBackup", utilLogger)
	logInfo("performing post deployent backup...", utilLogger)
	backupDir = h2hprops.get(KYTARGETBACKUPDIR) + File.separator + h2hprops.get(KYCCI_VERSION) 
	backupFile = backupDir + File.separator + h2hprops.get(KYCCI_VERSION) + "_" + str(date.today()) + "_" + time.strftime("%H-%M-%S", time.gmtime()) + "_" + POSTDEPLOYMENTBACKUPFILE	
	if os.path.exists(backupFile):
		# I dont expect this to happen, provided when someone wants to re-run immediately on any deployment issues
		os.remove(backupFile)
	performDeploymentBackup(backupFile)
	logDebug("<<<performPostDeploymentBackup", utilLogger)


