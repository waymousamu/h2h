###########################################################################################
# PackagingManager.py
# create package for PIDCR
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
execfile("scripts" + File.separator + "CCIBuild.py")
execfile("scripts" + File.separator + "MQScriptGen.py")
execfile("scripts" + File.separator + "MomHandler.py")

packagingManagerLogger = Logger.getLogger("PackagingManager.py")

##############################################
# mkTmpDirs
# create temporary directories for packaging
##############################################

def mkTmpDir():
        logDebug(">>>mkTmpDir", packagingManagerLogger)
	logDebug("Retrieving target dirs on source machine", packagingManagerLogger)
        dirParts = [h2hprops.get(KYENVID), h2hprops.get(KYCCI_VERSION), h2hprops[KYPROJECT], h2hprops.get(KYUNIQUEPACKAGEID)]
	h2hprops[KYPKGDIR] = "-".join(dirParts) 
	dirStr = h2hprops.get(KYPIUH2HDIR) + File.separator + PACKAGEDIR + File.separator + h2hprops.get(KYENVID) +  File.separator + h2hprops.get(KYPKGDIR)
	h2hprops[KYOUTPUTDIR] = dirStr
	logDebug("KYOUTPUTDIR: %s " % h2hprops[KYOUTPUTDIR], packagingManagerLogger)
	h2hprops[KYTARFILENAME] = dirStr + TARGZEXT
	logDebug("KYTARFILENAME: %s " % h2hprops[KYTARFILENAME], packagingManagerLogger)
	os.makedirs(h2hprops[KYOUTPUTDIR])
	logInfo("Create packaging directory: %s" % h2hprops[KYOUTPUTDIR], packagingManagerLogger)
        
def mkTmpDirs():
        logDebug(">>>mkTmpDirs", packagingManagerLogger)
	logInfo("creating temporary directories for packaging...", packagingManagerLogger)
	logDebug("Retrieving target dirs on source machine", packagingManagerLogger)

        dirParts = [h2hprops.get(KYENVID), h2hprops.get(KYCCI_VERSION), h2hprops[KYPROJECT], h2hprops.get(KYUNIQUEPACKAGEID)]
	h2hprops[KYPKGDIR] = "-".join(dirParts) 
	dirStr = h2hprops.get(KYPIUH2HDIR) + File.separator + PACKAGEDIR + File.separator + h2hprops.get(KYENVID) +  File.separator + h2hprops.get(KYPKGDIR)
	h2hprops[KYOUTPUTDIR] = dirStr
	logDebug("dirStr="+dirStr, packagingManagerLogger)
	h2hprops[KYTARFILENAME] = dirStr + TARGZEXT
	logDebug("dirStr="+dirStr, packagingManagerLogger)
	
	if os.path.exists(dirStr):
		newDir = "-".join([dirStr,str(date.today()),time.strftime("%H-%M-%S", time.gmtime())])
		os.rename(dirStr, newDir)
	if isPropertyAvailable(h2hprops.get(KYTARGETCONFIGDIR)):
		os.makedirs(dirStr + File.separator + h2hprops.get(KYTARGETCONFIGDIR))
		logDebug("created directory " + dirStr + File.separator + h2hprops.get(KYTARGETCONFIGDIR), packagingManagerLogger)

	if isPropertyAvailable(h2hprops.get(KYTARGETSCRIPTSDIR)):		
		os.makedirs(dirStr + File.separator + h2hprops.get(KYTARGETSCRIPTSDIR))
		logDebug("created directory " + dirStr + File.separator + h2hprops.get(KYTARGETSCRIPTSDIR), packagingManagerLogger)

	if isPropertyAvailable(h2hprops.get(KYTARGETBINDIR)):		
		os.makedirs(dirStr + File.separator + h2hprops.get(KYTARGETBINDIR))
		logDebug("created directory " + dirStr + File.separator + h2hprops.get(KYTARGETBINDIR), packagingManagerLogger)

	if isPropertyAvailable(h2hprops.get(KYTARGETSODIR)):		
		os.makedirs(dirStr + File.separator + h2hprops.get(KYTARGETSODIR))
		logDebug("created directory " + dirStr + File.separator + h2hprops.get(KYTARGETSODIR), packagingManagerLogger)

	if isPropertyAvailable(h2hprops.get(KYTARGETJVALDIR)):		
		os.makedirs(dirStr + File.separator + h2hprops.get(KYTARGETJVALDIR))
		logDebug("created directory " + dirStr + File.separator + h2hprops.get(KYTARGETJVALDIR), packagingManagerLogger)

	if isPropertyAvailable(h2hprops.get(KYTARGETMAPSDIR)):		
		os.makedirs(dirStr + File.separator + h2hprops.get(KYTARGETMAPSDIR))
		logDebug("created directory " + dirStr + File.separator + h2hprops.get(KYTARGETMAPSDIR), packagingManagerLogger)

	if isPropertyAvailable(h2hprops.get(KYTARGETCERTDIR)):		
		os.makedirs(dirStr + File.separator + h2hprops.get(KYTARGETCERTDIR))
		logDebug("created directory " + dirStr + File.separator + h2hprops.get(KYTARGETCERTDIR), packagingManagerLogger)

	os.makedirs(dirStr + File.separator + PROPERTIESFOLDERNAME)
	logDebug("created directory " + dirStr + File.separator + PROPERTIESFOLDERNAME, packagingManagerLogger)

	os.makedirs(dirStr + File.separator + MOMFWKDIR)
	logDebug("created directory " + dirStr + File.separator + MOMFWKDIR, packagingManagerLogger)

	logInfo("completed creating directories for deployment", packagingManagerLogger)
	logDebug("<<<mkTmpDirs", packagingManagerLogger)

##############################################
# createDeployScript
# create deployment script for the target host
##############################################
def createDeployScript():
        logDebug(">>>createDeployScript", packagingManagerLogger)
	deployH2HFile = open(os.sys.currentWorkingDir + File.separator + DEPLOYH2HFILE,"w+")
	deployH2HFile.write(DEPLOYSCRIPTHDR)
	deployH2HFile.close()
        logDebug("<<<createDeployScript", packagingManagerLogger)
	
##############################################
# createTargetPropertyFile
# create property file for deployment on target host
##############################################
def createTargetPropertyFile():
        logDebug(">>>createTargetPropertyFile", packagingManagerLogger)
	logInfo("Updating deployment property file", utilLogger)
	propertiesFolder = h2hprops.get(KYOUTPUTDIR) + File.separator + PROPERTIESFOLDERNAME
	if not os.path.exists(propertiesFolder):
                logDebug("creating properties directory: %s " % propertiesFolder, packagingManagerLogger)
                os.makedirs(propertiesFolder)
	updatedData = open(propertiesFolder + File.separator + h2hprops.get(KYENVID) + "_" + DEPLOYPROPERTYFILE,"w+")
	logDebug("DEPLOYPROPERTIES: %s" % DEPLOYPROPERTIES, utilLogger)
	logDebug("KYDEPLOYPROPERTIES: %s" % h2hprops.get(KYDEPLOYPROPERTIES), utilLogger)
	for key in DEPLOYPROPERTIES:	
		if key in h2hprops.get(KYDEPLOYPROPERTIES):
			if key == KYMQSCSCRIPTS:
				mqScriptFiles = h2hprops.get(KYMQSCSCRIPTS)
				if mqScriptFiles != None:
					logDebug("writing property %s value %s to deployment properties" % (key,mqScriptFiles), utilLogger) 
					updatedData.write("%s=%s\n" % (KYMQSCSCRIPTS, mqScriptFiles))
			elif key == KYMQCHECKLIST_VERSION:
					logDebug("writing property %s value %s to deployment properties" % (key,mqScriptFiles), utilLogger) 
					updatedData.write("%s=%s\n" % (KYMQCHECKLIST_VERSION, h2hprops.get(KYMQCHECKLIST_VERSION)))
			elif key == KYSETENV_SH:
                                setenvlines = h2hprops.get(KYSETENV_SH)
                                logDebug("writing property %s value %s to deployment properties" % (key,setenvlines), utilLogger) 
				updatedData.write("%s=[[\n%s\n]]\n" % (KYSETENV_SH, setenvlines))
			elif key == KYR_APP_RG1_SH:
                                lines = h2hprops.get(KYR_APP_RG1_SH)
                                logDebug("writing property %s value %s to deployment properties" % (key,lines), utilLogger) 
				updatedData.write("%s=[[\n%s\n]]\n" % (KYR_APP_RG1_SH, lines))
			elif key == KYSCRIPTS_SETENV_SH:
                                lines = h2hprops.get(KYSCRIPTS_SETENV_SH)
                                logDebug("writing property %s value %s to deployment properties" % (key,lines), utilLogger) 
				updatedData.write("%s=[[\n%s\n]]\n" % (KYSCRIPTS_SETENV_SH, lines))
			elif key == KYEBMOMDRVD_SH:
                                lines = h2hprops.get(KYEBMOMDRVD_SH)
                                logDebug("writing property %s value %s to deployment properties" % (key,lines), utilLogger) 
				updatedData.write("%s=[[\n%s\n]]\n" % (KYEBMOMDRVD_SH, lines))
			elif key == KYCHECKDIR:
                                lines = h2hprops.get(KYCHECKDIR)
                                logDebug("writing property %s value %s to deployment properties" % (key,lines), utilLogger) 
				updatedData.write("%s=[[\n%s\n]]\n" % (KYCHECKDIR, lines))
			elif isPropertyAvailable(h2hprops.get(key)):
				logDebug("writing property %s value %s to deployment properties" % (key,h2hprops.get(key)), utilLogger) 				
				updatedData.write("%s=%s\n" % (str(key), h2hprops.get(key)))
	updatedData.close()
	logInfo("completed deployment property file", utilLogger)
        logDebug("<<<createTargetPropertyFile", packagingManagerLogger)

##############################################
# createH2HPackageTARFile
# create package tar file for deployment
##############################################
def createH2HPackageTARFile():
        logDebug(">>>createH2HPackageTARFile", packagingManagerLogger)
	logInfo("creating h2h package tar file...", utilLogger)
	curWorkDir = h2hprops.get(KYPIUH2HDIR)
	packageDir = h2hprops.get(KYPIUH2HDIR) + File.separator + PACKAGEDIR + File.separator + h2hprops.get(KYENVID)
	os.chdir(packageDir)
	packageParts = []
	for component in os.listdir(h2hprops.get(KYPKGDIR)):
		packageParts.append(h2hprops.get(KYPKGDIR) + File.separator + component)
	tarFileName = h2hprops[KYTARFILENAME]
	logDebug("tarFileName: %s " % tarFileName, packagingManagerLogger)
	createDeployTar(packageParts, tarFileName)
	os.chdir(curWorkDir)
	logInfo("created tar file %s" % tarFileName, utilLogger)
	logDebug("<<<createH2HPackageTARFile", packagingManagerLogger)

##############################################
# createPackage
# create deployment package
##############################################
def executePackaging(propertyFile, envid, options):
        logDebug(">>>executePackaging", packagingManagerLogger)
	logInfo("performing deployment packaging...", packagingManagerLogger)
	logDebug("PROCESSEDFOLDER: %s " % PROCESSEDFOLDER, packagingManagerLogger)
	if not os.path.exists(PROCESSEDFOLDER):
		os.makedirs(PROCESSEDFOLDER)

	loadProperties(propertyFile)
	logDebug("h2hprops: %s " % h2hprops, packagingManagerLogger)
	logDebug("h2hprops.KYSETENV_SH: %s " % h2hprops.get(KYSETENV_SH), packagingManagerLogger)
	setenvLines = h2hprops.get(KYSETENV_SH).split(",")
	setenvLineList = []
	for line in setenvLines:
                i = setenvLines.index(line)
                setenvLines[i] = setenvLines[i].rstrip('"')
                setenvLines[i] = setenvLines[i].lstrip('"')
                logDebug("line: %s " % setenvLines[i], packagingManagerLogger)
                setenvLineList.append(setenvLines[i])
        logDebug("setenvLineList: %s " % setenvLineList, packagingManagerLogger)
	packagingChecks(options)
	displayDeploymentSummary()
	
        logDebug(options.mqCheckList, packagingManagerLogger)
        logDebug(options.momDeploy, packagingManagerLogger)

        mkTmpDir()

	if (options.momDeploy):
		processCCIBuild(options.momDeploy)
		processMomConfig(options.momDeploy)

	if (options.mqCheckList):
		processMQCheckLists(options.mqCheckList)

	if (options.fwkDeploy):
                processMomFWK(options.fwkDeploy)

	createDeployScript()
	createTargetPropertyFile()
	createH2HPackageTARFile()		
	processedFile = PROCESSEDFOLDER + File.separator + envid + "_" + PACKAGEPROPERTYFILE + "-" + h2hprops.get(KYUNIQUEPACKAGEID)
	backupPropertiesFile(processedFile)
	logInfo("***** deployment packaging completed! ****", packagingManagerLogger)
	print "\n\n**** deployment packaging completed! Check log for any issues ****"
	logDebug("<<<executePackaging", packagingManagerLogger)		

