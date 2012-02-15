###########################################################################################
# DeployManager.py
# Deployment manager for deploying the PIDCR
#
#	Mahesh Devendran, WebSphere Support, PIU Team
#	Copyright(c) 2010, Euroclear 
############################################################################################

from org.apache.log4j import *
import sys
from os import File

execfile("scripts" + File.separator + "CONSTANTS.py")
execfile("scripts" + File.separator + "util.py")
execfile("scripts" + File.separator + "DeploymentChecks.py")
execfile("scripts" + File.separator + "MomHandler.py")
execfile("scripts" + File.separator + "MQDriver.py")

deployManagerLogger = Logger.getLogger("DeployManager.py")

##############################################
# untarDeployPackage
# untar deployment package
##############################################
def untarDeployPackage(tarFile, envid):
  curWorkDir = os.sys.currentWorkingDir
  packageLocation = curWorkDir + File.separator + envid
  if not os.path.exists(packageLocation):
    os.makedirs(packageLocation)

  tarFileName = tarFile
  if tarFile.find(TARGZEXT) > -1:
    fileext = tarFile.split(TARGZEXT)
    if fileext[1] != "":
      tarFileName = fileext[0]
  else:
    if tarFile.find(TAREXT) < 0:
      logError("Tar file extension not supported, supported file extension - %s.<Unix Accountid> or %s or %s" %(TARGZEXT,TARGZEXT,TAREXT), deployManagerLogger)
      sys.exit(1)

  if tarFile.find(File.separator) < 0:
    tarFileName = os.sys.currentWorkingDir + File.separator + tarFileName

  os.chdir(packageLocation)
  tarFileParts = tarFileName.split(File.separator)
  tarDir = tarFileParts[len(tarFileParts) - 1]
  if tarFile.find(TAREXT) > -1:
        tarDir = tarDir.split(TAREXT)[0]
  if tarFile.find(TARGZEXT) > -1:
        tarDir = tarDir.split(TARGZEXT)[0]

  if tarFile.find(TARGZEXT) > -1:
    cmdToRun = GUNZIPCMD + " " + tarFile + "|" + UNTARCMD + " - "
    logInfo("untaring package : %s " % cmdToRun, deployManagerLogger)
    (exitstatus, result) = commands.getstatusoutput(cmdToRun)
    if exitstatus > 0:
    	logInfo("exit status is %s, result is %s" % (exitstatus,result), deployManagerLogger)
      	sys.exit(1)
  elif tarFile.find(TAREXT) > -1:
    cmdToRun = UNTARCMD + " " + tarFile
    logInfo("untaring package : %s " % cmdToRun, deployManagerLogger)
    (exitstatus, result) = commands.getstatusoutput(cmdToRun)
    if exitStatus > 0:
    	logInfo("exit status is %s, result is %s" % (exitstatus,result), deployManagerLogger)
      	sys.exit(1)
      
  os.chdir(curWorkDir)
  h2hprops[KYPACKAGE_LOCATION] = packageLocation + File.separator + tarDir

##############################################
# createH2HDirectories
# create H2H deployment directories
##############################################
def createH2HDirectories():
	baseDir = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYCCI_VERSION)
	logInfo("creating target directories %s" % baseDir, deployManagerLogger)
	if os.path.exists(baseDir):
		backupDeployedRelease()
				
	subDir = baseDir + File.separator + h2hprops.get(KYTARGETCONFIGDIR)
	if not os.path.exists(subDir):
		os.makedirs(subDir)
		logInfo("created directory " + subDir, deployManagerLogger)

	subDir = baseDir + File.separator + h2hprops.get(KYTARGETSCRIPTSDIR)
	if not os.path.exists(subDir):
		os.makedirs(subDir)
		logInfo("created directory " + subDir, deployManagerLogger)

	subDir = baseDir + File.separator + h2hprops.get(KYTARGETBINDIR)
	if not os.path.exists(subDir):
		os.makedirs(subDir)
		logInfo("created directory " + subDir, deployManagerLogger)

	subDir = baseDir + File.separator + h2hprops.get(KYTARGETSODIR)
	if not os.path.exists(subDir):
		os.makedirs(subDir)
		logInfo("created directory " + subDir, deployManagerLogger)

	subDir = baseDir + File.separator + h2hprops.get(KYTARGETJVALDIR)
	if not os.path.exists(subDir):
		os.makedirs(subDir)
		logInfo("created directory " + subDir, deployManagerLogger)

	subDir = baseDir + File.separator + h2hprops.get(KYTARGETMAPSDIR)
	if not os.path.exists(subDir):
		os.makedirs(subDir)
		logInfo("created directory " + subDir, deployManagerLogger)

	subDir = baseDir + File.separator + h2hprops.get(KYTARGETCERTDIR)
	if not os.path.exists(subDir):
		os.makedirs(subDir)
		logInfo("created directory " + subDir, deployManagerLogger)

	subDir = baseDir + File.separator + h2hprops.get(KYTARGETREGISTRYDIR)
	if not os.path.exists(subDir):
		os.makedirs(subDir)
		logInfo("created directory " + subDir, deployManagerLogger)

	if h2hprops.get(KYTARGETRELEASEDIR) == None:
		h2hprops[KYTARGETRELEASEDIR] = TARGETRELEASEDIR
	subDir = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYTARGETRELEASEDIR)
	if not os.path.exists(subDir):
		os.makedirs(subDir)
		logInfo("created directory " + subDir, deployManagerLogger)

	momLogDir = VARLOG + File.separator + h2hprops.get(KYENVID) + File.separator + CCIAPPLICATION + File.separator + h2hprops.get(KYCCI_VERSION)
	if not os.path.exists(momLogDir):
		os.makedirs(momLogDir)
		logInfo("created directory " + momLogDir, deployManagerLogger)

	softLinkFile = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYCCIVERSION_SOFTLINK)

	if os.path.exists(softLinkFile):
		os.remove(softLinkFile)
				
	curWorkDir = os.sys.currentWorkingDir
	os.chdir(h2hprops.get(KYTARGETDIRPATTERN))		

	cmdToRun = LNCMD + " " + baseDir + " " + h2hprops.get(KYCCIVERSION_SOFTLINK)
	logInfo("running %s" % cmdToRun, deployManagerLogger)
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
	os.chdir(curWorkDir)	
		
	if exitstatus > 0:
		logError("error %s in creating the softlink %s for %s" % (result, h2hprops.get(KYCCIVERSION_SOFTLINK), baseDir), deployManagerLogger)
		sys.exit(1)
	logInfo("completed creating directories for deployment", deployManagerLogger)

##############################################
# deployH2H
# perform PIDCR deployment
##############################################
def deployH2H():
	baseDir = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYCCIVERSION_SOFTLINK)

	if isPropertyAvailable(h2hprops.get(KYTARGETSODIR)):
		srcDir = h2hprops[KYPACKAGE_LOCATION] + File.separator + h2hprops.get(KYTARGETSODIR)	
		dstDir = baseDir + File.separator + h2hprops.get(KYTARGETSODIR)
		copyDir(srcDir, dstDir)

	if isPropertyAvailable(h2hprops.get(KYTARGETCONFIGDIR)):
		srcDir = h2hprops[KYPACKAGE_LOCATION] + File.separator + h2hprops.get(KYTARGETCONFIGDIR)	
		dstDir = baseDir + File.separator + h2hprops.get(KYTARGETCONFIGDIR)
		for item in os.listdir(srcDir):		
			if item != EOCTFFILE:
				copyfile(srcDir + File.separator + item, dstDir + File.separator + item)
			else:
				if not os.path.exists(dstDir + File.separator + EOCTFFILE):
					if os.path.exists(srcDir + File.separator + EOCTFFILE):
						copyfile(srcDir + File.separator + EOCTFFILE, dstDir + File.separator + EOCTFFILE)
						removeCM(dstDir + File.separator + EOCTFFILE)
					
	if isPropertyAvailable(h2hprops.get(KYTARGETMAPSDIR)):
		srcDir = h2hprops[KYPACKAGE_LOCATION] + File.separator + h2hprops.get(KYTARGETMAPSDIR)	
		dstDir = baseDir + File.separator + h2hprops.get(KYTARGETMAPSDIR)
		copyDir(srcDir, dstDir)

	if isPropertyAvailable(h2hprops.get(KYTARGETBINDIR)):
		srcDir = h2hprops[KYPACKAGE_LOCATION] + File.separator + h2hprops.get(KYTARGETBINDIR)	
		dstDir = baseDir + File.separator + h2hprops.get(KYTARGETBINDIR)
		copyDir(srcDir, dstDir)

	if isPropertyAvailable(h2hprops.get(KYTARGETSCRIPTSDIR)):
		srcDir = h2hprops[KYPACKAGE_LOCATION] + File.separator + h2hprops.get(KYTARGETSCRIPTSDIR)	
		if os.path.exists(srcDir + File.separator + MOMCONTOL_SCRIPT):
			dstDir = baseDir + File.separator + h2hprops.get(KYTARGETSCRIPTSDIR)
			copyDir(srcDir, dstDir)
			
			baseDir = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYCCIVERSION_SOFTLINK) 
			cmdToRun=EXECPERMISSION + baseDir + File.separator + h2hprops.get(KYTARGETSCRIPTSDIR) + File.separator + MOMCONTOL_SCRIPT
			logDebug('Applying permission on mom script -> %s' % cmdToRun, deployManagerLogger)
			(exitstatus, result) = commands.getstatusoutput(cmdToRun)
			logDebug("Result of applying permission to mom script : %s "% result, deployManagerLogger)
	else:
		logInfo("Mom script %s already present, not deploying." % MOMCONTROL_SCRIPT, deployManagerLogger)

	if isPropertyAvailable(h2hprops.get(KYTARGETJVALDIR)):
		srcDir = h2hprops[KYPACKAGE_LOCATION] + File.separator + h2hprops.get(KYTARGETJVALDIR)	
		dstDir = baseDir + File.separator + h2hprops.get(KYTARGETJVALDIR)
		copyDir(srcDir, dstDir)
		curWorkDir = os.sys.currentWorkingDir
		os.chdir(dstDir)		
		cmdToRun = UNTARCMD + " " + JVAL_FILE
		logInfo("untaring %s : %s " % (JVAL_FILE,cmdToRun), deployManagerLogger)
		(exitstatus, result) = commands.getstatusoutput(cmdToRun)
		logInfo("exit status is %s, result is %s" % (exitstatus,result), deployManagerLogger)
		os.chdir(curWorkDir)		

	if isPropertyAvailable(h2hprops.get(KYTARGETCERTDIR)):
		srcDir = h2hprops[KYPACKAGE_LOCATION] + File.separator + h2hprops.get(KYTARGETCERTDIR)	
		dstDir = baseDir + File.separator + h2hprops.get(KYTARGETCERTDIR)
		copyDir(srcDir, dstDir)
	
	versionFile = h2hprops.get(KYPIUH2HDIR) + File.separator + VERSIONFILE
	releaseDir = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYTARGETRELEASEDIR) + File.separator + h2hprops.get(KYCCI_VERSION) 
	if not os.path.exists(releaseDir):
		os.makedirs(releaseDir)
	releaseFile = releaseDir + File.separator + VERSIONFILE
	copyfile(versionFile, releaseFile)

def processMomSecurity(fwkChanged):
	baseDir = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYCCIVERSION_SOFTLINK)
	srcDir = h2hprops[KYPACKAGE_LOCATION] + File.separator + h2hprops.get(KYTARGETCONFIGDIR)	
	dstDir = baseDir + File.separator + h2hprops.get(KYTARGETCONFIGDIR)

	srcEocTFFile = 	srcDir + File.separator + EOCTFFILE
	dstEocTFFile = dstDir + File.separator + EOCTFFILE
	
	if h2hprops.get(KYUSE_PREV_EOCTF_CERTS) == "Y":
		if os.path.exists(srcEocTFFile):
			if os.path.exists(dstEocTFFile):
				updateWithExistingCerts()
			else:
				logWarn("*** %s not available to update cert details for this deployment request ***" % dstEocTFFile, deployManagerLogger)

	if h2hprops.get(KYUSE_PREV_EOCTF_CERTS) == "N" or fwkChanged:
		if os.path.exists(srcEocTFFile):		
			setAccessPermissions()	
			runEsaTOCCrypto()
			revokeAccessPermissions()	
		else:
			logWarn("*** %s not available to update cert details for this deployment ***" % srcEocTFFile, deployManagerLogger)

##############################################
# setAccessPermissions
# set access permissions for deployment
##############################################
def setAccessPermissions():
	logInfo("applying access permissions on certs and registry for running EsaTOCCrypto", deployManagerLogger)
	baseDir = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYCCIVERSION_SOFTLINK) 
	contextFS = baseDir + File.separator + h2hprops.get(KYTARGETCERTDIR)

	cmdToRun = "chmod -R u+rwx " + contextFS 
	logDebug("Applying permissions on cert files -> %s " % cmdToRun, deployManagerLogger)
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
	logInfo(result, deployManagerLogger)

		
	contextFS = baseDir + File.separator + h2hprops.get(KYTARGETREGISTRYDIR)	
	cmdToRun = "chmod -R u+rwx " + contextFS
	logDebug("Applying permissions on registry folder ->  %s" % cmdToRun, deployManagerLogger)
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
	logInfo(result, deployManagerLogger)
	
	logInfo("completed applying access permissions", deployManagerLogger)

##############################################
# revokeAccessPermissions
# set access permissions for deployment
##############################################
def revokeAccessPermissions():
	logInfo("applying permission restrictions on certs and registry after running EsaTOCCrypto", deployManagerLogger)
#	baseDir = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYCCIVERSION_SOFTLINK) 
#	contextFS = baseDir + File.separator + h2hprops.get(KYTARGETCERTDIR)

#	cmdToRun = CERTFILESPERMISSIONS + contextFS + File.separator + "*"
#	logDebug("Applying permission restriction on cert files -> %s " % cmdToRun, deployManagerLogger)
#	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
#	logInfo(result, deployManagerLogger)
#
#	cmdToRun = CERTFOLDERPERMISSIONS + contextFS
#	logDebug("Applying permission restriction on cert folder ->  %s" % cmdToRun, deployManagerLogger)
#	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
#	logInfo(result, deployManagerLogger)
#			
#	contextFS = baseDir + File.separator + h2hprops.get(KYTARGETREGISTRYDIR)
#	if len(os.listdir(contextFS + File.separator)) > 0:
#		cmdToRun = CERTFILESPERMISSIONS + contextFS + File.separator + "*" + File.separator + "*"
#		logDebug("Applying permission restriction on registry files  %s" % cmdToRun, deployManagerLogger)
#		(exitstatus, result) = commands.getstatusoutput(cmdToRun)
#		logInfo(result, deployManagerLogger)
#	
#	cmdToRun = CERTFOLDERPERMISSIONS + contextFS
#	logDebug("Applying permission restriction on registry folder ->  %s" % cmdToRun, deployManagerLogger)
#	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
#	logInfo(result, deployManagerLogger)
#	
	logInfo("completed applying access permissions", deployManagerLogger)

##############################################
# createTargetDirs
# create target directories
##############################################
def createTargetDirs(requested):
	if not requested:
		return
	createH2HDirectories()
	
##############################################
# performDeployment
# perform deployment
##############################################
def performDeployment(requested):
	if not requested:
		return
	createH2HDirectories()
	deployH2H()	
	createEbmomdrvdSHFIle()
	fwkChanged = createSetEnv()
	processMomSecurity(fwkChanged)
	startMom()	

##############################################
# performMQDeployment
# perform MQ deployment
##############################################
def performMQDeployment(requested):
	if not requested:
		return
	deployMQ()

##############################################
# performFullDeployment
# perform full deployment
##############################################
def performFullDeployment(requested):
	if not requested:
		return
	createH2HDirectories()
	deployH2H()	
	createEbmomdrvdSHFIle()
	fwkChanged = createSetEnv()
	processMomSecurity(fwkChanged)
	deployMQ()
	startMom()	

##############################################
# perforMOMFwkInstallation
# perform Mom FWK deployment
##############################################
def perforMOMFwkInstallation(requested):
	if not requested:
		return
	if not isPropertyAvailable(h2hprops.get(KYMOMTARFILENAME)):					
		logError("***** Package tarFile is not built for MOM FWK install *****", deployManagerLogger)
		sys.exit(1)
	if not os.path.exists(h2hprops.get(KYPACKAGE_LOCATION) + File.separator + MOMFWKDIR + File.separator + h2hprops.get(KYMOMTARFILENAME)):
		logError("***** Package tarFile is not built for MOM FWK install *****", deployManagerLogger)
		sys.exit(1)

	installMomFWK()
	
def _checkRequests(args):
	if (args.deployMQ or args.fullDeployment) and getVar(h2hprops.get(KYMQSCSCRIPTS)) == "":
		logError("**** No MQ scripts available to deploy for this build ****", deployManagerLogger)
		sys.exit(1)

##############################################
# executeDeployment
# execute deployment process
##############################################
def executeDeployment(propertyFile, args):
	processedFolder = h2hprops.get(KYPIUH2HDIR) + File.separator + PROCESSEDFOLDERNAME
	if not os.path.exists(processedFolder):
		os.makedirs(processedFolder)
	loadProperties(propertyFile)
	_checkRequests(args)
	performDeploymentPrechecks(args)
	displayDeploymentSummary()
	if args.precheck:
		return
		
	scriptDir = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYCCIVERSION_SOFTLINK) + File.separator + h2hprops.get(KYTARGETSCRIPTSDIR)
	if os.path.exists(scriptDir): #  and not args.deployMQ 
		stopMom()
	perforMOMFwkInstallation(args.installMOMFwk or args.fullDeployment)
	createTargetDirs(args.createTargetDirs)
	performDeployment(args.deployH2H)
	performMQDeployment(args.deployMQ)
	performFullDeployment(args.fullDeployment)		
	processedFile = processedFolder + File.separator + args.envid + "_" + args.project + "_" + PACKAGEPROPERTYFILE + "-" + str(date.today()) + "_" + time.strftime("%H-%M-%S", time.gmtime())
	backupPropertiesFile(processedFile)		
	deploymentPostChecks(args)
	performPostDeploymentBackup()
