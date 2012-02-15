###########################################################################################
# MomHandler.py
#	Script to perform MOM installation and deployment
#
#	Mahesh Devendran, WebSphere Support, PIU Team
#	Copyright(c) 2010, Euroclear 
############################################################################################

from org.apache.log4j import *
import sys
from os import File
import re
import tempfile
from xml.dom.minidom import parse
import commands

global eoctfPlaceHolders
eoctfPlaceHolders = {}
global certPlaceHolders
certPlaceHolders = []

execfile("scripts" + File.separator + "util.py")
execfile("scripts" + File.separator + "CONSTANTS.py")

momHandlerLogger = Logger.getLogger("MomHandler.py")

##############################################
# createPlaceHolders
# create place holders list
##############################################
def createPlaceHolders():
        logDebug(">>>createPlaceHolders", momHandlerLogger)
	eocTFFile = h2hprops[KYOUTPUTDIR] + File.separator + h2hprops.get(KYTARGETCONFIGDIR) + File.separator + EOCTFFILE
	if not os.path.exists(eocTFFile):	
		return
        else:
                logInfo("Creating EocTF placeholders.", momHandlerLogger)
		
	fh = open(eocTFFile,"r")
	for line in fh.read().split():
		t = line.strip()
		if t.find("#") >= 0:
			placeHolder = t[t.find("#"):t.rfind("#")+1]
			if not placeHolder in eoctfPlaceHolders:
				eoctfPlaceHolders[placeHolder[placeHolder.find('#')+1:placeHolder.rfind('#')]] = placeHolder
	fh.close()

	for property in eoctfPlaceHolders.keys():
		if property in h2hprops:
			value = h2hprops.get(property)
			if value.find("#") >= 0:
				for line in value.split():
					if line.find("#") >= 0:
						placeHolder = line[line.find("#"):line.rfind("#")+1]
						if not placeHolder in eoctfPlaceHolders:
							name = placeHolder[placeHolder.find('#')+1:placeHolder.rfind('#')]
							eoctfPlaceHolders[name] = placeHolder
							certPlaceHolders.append(name)
	logDebug("<<<createPlaceHolders", momHandlerLogger)

##############################################
# updateWithExistingCerts
# update with existing certs
##############################################
def updateWithExistingCerts():
        logDebug(">>>updateWithExistingCerts", momHandlerLogger)
	baseDir = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYCCIVERSION_SOFTLINK)
	logInfo("basedir = %s" % baseDir, momHandlerLogger)
	
	if not os.path.exists(baseDir):
		logError("No existing installation to get MAD and GUID certificate details", momHandlerLogger)
		sys.exit(1)
		
	currentEOCTFFIle = baseDir + File.separator + h2hprops.get(KYTARGETCONFIGDIR) + File.separator + EOCTFFILE
	newEOCTFFile = h2hprops.get(KYPACKAGE_LOCATION) + File.separator + h2hprops.get(KYTARGETCONFIGDIR) + File.separator + EOCTFFILE
	removeCM(newEOCTFFile)
	
	srcEocTFXML = parse(currentEOCTFFIle)
	dstEocTFXML = parse(newEOCTFFile)
	
	srcClientEndPointEl = srcEocTFXML.getElementsByTagName("ClientEndPoint")
	dstClientEndPointEl = dstEocTFXML.getElementsByTagName("ClientEndPoint")
	i=0
	for node in dstClientEndPointEl:
		parentNode = node.parentNode
		parentNode.removeChild(node)		
		parentNode.appendChild(srcClientEndPointEl[i].cloneNode(True))
		i = i + 1

	dstEocFile = open(currentEOCTFFIle,"w")
	dstEocTFXML.writexml(dstEocFile)
	dstEocFile.close()
	logDebug("<<<updateWithExistingCerts", momHandlerLogger)

##############################################
# replaceMomPlaceHolders
# replace mom placeholders
##############################################
def replaceMomPlaceHolders(configFile):
        logDebug(">>>replaceMomPlaceHolders", momHandlerLogger)
	configTmpFile = h2hprops.get(KYOUTPUTDIR) + File.separator + h2hprops.get(KYTARGETCONFIGDIR) + File.separator + H2HTMPFILE
	logDebug("configFile is %s" % configFile, momHandlerLogger)
	logDebug("configTmpFile is %s" % configTmpFile, momHandlerLogger)
	processedData = open(configTmpFile,"w+")
	data = open(configFile).read()
	usePrevCert = 'N'
	baseDir = h2hprops.get(KYTARGETDIRPATTERN) + "/" + h2hprops.get(KYCCIVERSION_SOFTLINK) + "/"
			
	for var in eoctfPlaceHolders:
                logDebug("var: %s " % var, momHandlerLogger)
		newVar = None
		if var in [KYPARAM_BIN_PATH, KYPARAM_CONFIG_PATH, KYPARAM_MAP_PATH]:
			if var == KYPARAM_BIN_PATH:
				newVar = baseDir + h2hprops.get(KYTARGETSODIR) + "/"
			if var == KYPARAM_CONFIG_PATH:
				newVar = baseDir + h2hprops.get(KYTARGETCONFIGDIR) + "/"
			if var == KYPARAM_MAP_PATH:
				newVar = baseDir + h2hprops.get(KYTARGETMAPSDIR) + "/"
		else:
			if usePrevCert == 'N':
				if var in certPlaceHolders:
					if var.find("\\") >= 0:
						fileName = getFileNameFromURL(h2hprops.get(var))
						newVar = baseDir + h2hprops.get(KYTARGETCERTDIR) + "/" + fileName
				else:
					newVar = h2hprops.get(var)
					logDebug("newVar: %s " % newVar, momHandlerLogger)
					if newVar.find("#") >= 0:
						for line in newVar.split():
							if line.find("#") >= 0:
								placeHolder = line[line.find("#"):line.rfind("#")+1]
								property = placeHolder[placeHolder.find('#')+1:placeHolder.rfind('#')]
								value = h2hprops.get(property)
								if value == None or value.strip() == "":
									logError("**** property %s not available in property file ****" % property, momHandlerLogger)
									sys.exit(1)
									
								if value.find("\\") >= 0:
									fileName = getFileNameFromURL(value)
									value = baseDir + h2hprops.get(KYTARGETCERTDIR) + "/" + fileName								
								newVar = newVar.replace(placeHolder,value)		
			else:
				if var not in certPlaceHolders:
					newVar = h2hprops.get(var)			

		if newVar != None:
			logDebug("replacing variable #%s# with %s " % (var,newVar), momHandlerLogger)
			logInfo("replacing variable %s " % var, momHandlerLogger)
			replacedData = data.replace('#' + var + '#', newVar)
			data = replacedData

	processedData.write(data)		
	processedData.close()
	copyfile(configTmpFile, configFile)
	os.remove(configTmpFile)
	logDebug("<<<replaceMomPlaceHolders", momHandlerLogger)
	
##############################################
# processEocTF
# process EocTF config 
##############################################
def processEocTF():
        logDebug(">>>processEocTF", momHandlerLogger)	
	eocTFFile = h2hprops[KYOUTPUTDIR] + File.separator + h2hprops.get(KYTARGETCONFIGDIR) + File.separator + EOCTFFILE
	if exists(eocTFFile):
                logInfo("Processing EocTF.xml...", momHandlerLogger)
		replaceMomPlaceHolders(eocTFFile)
                copyCerts()
        logDebug("<<<processEocTF", momHandlerLogger)

##############################################
# processEbMomConfig
# process EbMomConfig config 
##############################################
def processEbMomConfig():
        logDebug(">>>processEbMomConfig", momHandlerLogger)
	ebMomConfigFile = h2hprops[KYOUTPUTDIR] + File.separator + h2hprops.get(KYTARGETCONFIGDIR) + File.separator + EBMOMCONFIGFILE
	if exists(ebMomConfigFile):
                logInfo("Processing EbMomConfig.xml...", momHandlerLogger)
		replaceMomPlaceHolders(ebMomConfigFile)
	logDebug("<<<processEbMomConfig", momHandlerLogger)

##############################################
# copyCerts
# copy certs
##############################################
def copyCerts():
        logDebug(">>>copyCerts", momHandlerLogger)
        targetDir = h2hprops.get(KYOUTPUTDIR) + File.separator + h2hprops.get(KYTARGETCERTDIR)

        if not os.path.exists(targetDir):
                logInfo("Creating certs directory: %s " % targetDir, momHandlerLogger)
                os.makedirs(targetDir)
        
        logInfo("Copying certificate files for Mom config", momHandlerLogger)
	srcFile = h2hprops.get(KYMADKEYSTOREFILE)
	targetFile = h2hprops.get(KYOUTPUTDIR) + File.separator + h2hprops.get(KYTARGETCERTDIR) + File.separator + getFileNameFromURL(srcFile)
	logInfo("copying %s to %s " % (srcFile, targetFile), momHandlerLogger)
	copyfile(srcFile, targetFile)

	srcFile = h2hprops.get(KYMADCACERTFILE)
	targetFile = h2hprops.get(KYOUTPUTDIR) + File.separator + h2hprops.get(KYTARGETCERTDIR) + File.separator + getFileNameFromURL(srcFile)
	logInfo("copying %s to %s " % (srcFile, targetFile), momHandlerLogger)
	copyfile(srcFile, targetFile)

	srcFile = h2hprops.get(KYGUIDKEYSTOREFILE)
	targetFile = h2hprops.get(KYOUTPUTDIR) + File.separator + h2hprops.get(KYTARGETCERTDIR) + File.separator + getFileNameFromURL(srcFile)
	logInfo("copying %s to %s " % (srcFile, targetFile), momHandlerLogger)
	copyfile(srcFile, targetFile)

	srcFile = h2hprops.get(KYGUIDCACERTFILE)
	targetFile = h2hprops.get(KYOUTPUTDIR) + File.separator + h2hprops.get(KYTARGETCERTDIR) + File.separator + getFileNameFromURL(srcFile)
	logInfo("copying %s to %s " % (srcFile, targetFile), momHandlerLogger)
	copyfile(srcFile, targetFile)
	logDebug("<<<copyCerts", momHandlerLogger)
	return True
	
##############################################
# processMomConfig
# copy mom config
##############################################
def processMomConfig(app):
        logDebug(">>>processMomConfig", momHandlerLogger)
	if app == False:
		return
		
	if not h2hprops.get(KYEOCTFPROPERTYCHECK):
		return
		
	createPlaceHolders()
	for props in eoctfPlaceHolders:
		if props in h2hprops:
			if not isPropertyAvailable(h2hprops.get(props)):
				logError("Value for EocTF property %s for EOCTF configuration not available in the properties file" % props, momHandlerLogger)
				return
	
	processEocTF()
	processEbMomConfig()
	logDebug("<<<processMomConfig", momHandlerLogger)

def installMomFWK():
        logDebug(">>>installMomFWK", momHandlerLogger)
	momScript = None
	if os.path.exists(MOMINSTALLLOCLC):
		momScript = 'pbrun ' + MOMINSTALLLOCLC + File.separator + 'install.bsh '
	elif os.path.exists(MOMINSTALLLOCUC):
		momScript = 'pbrun ' + MOMINSTALLLOCUC + File.separator + 'install.bsh '
	else:
		logError("*** Mom install location %s or %s not available on this host ****" % (MOMINSTALLLOCLC, MOMINSTALLLOCUC), momHandlerLogger)
		sys.exit(1)
				
	cmdToRun = momScript + h2hprops.get(KYPACKAGE_LOCATION) + File.separator + MOMFWKDIR + File.separator + h2hprops.get(KYMOMTARFILENAME)
	logInfo("installing Mom : %s" % cmdToRun, momHandlerLogger)
	(exitstatus,result)=commands.getstatusoutput(cmdToRun)
	logInfo("Result of mom installation %s" % result, momHandlerLogger)
	if exitstatus != 0:
		logError("Mom installation failed" , momHandlerLogger)
		sys.exit(1)
	logDebug("<<<installMomFWK", momHandlerLogger)

def processMomFWK(app):
        logDebug(">>>processMomFWK", momHandlerLogger)
        logInfo("Copying MOM Framework files...", momHandlerLogger)
	if app == False:
		return
	
	targetDir = targetFile = h2hprops.get(KYOUTPUTDIR) + File.separator + MOMFWKDIR
	if not os.path.exists(targetDir):
                logDebug("creating directory: %s" % targetDir, momHandlerLogger)
                os.makedirs(targetDir)
	#copyfile(h2hprops.get(KYMOMINSTALLSCRIPT), targetDir + File.separator + getFileNameFromURL(h2hprops.get(KYMOMINSTALLSCRIPT)))
	h2hprops[KYMOMTARFILENAME] = getFileNameFromURL(h2hprops.get(KYMOMTARFILE))
	copyfile(h2hprops.get(KYMOMTARFILE), targetDir + File.separator + h2hprops.get(KYMOMTARFILENAME))
        copyCerts()
        logDebug("<<<processMomFWK", momHandlerLogger)

##############################################
# updateSetEnv
# update SetEnv script
##############################################
def updateSetEnv(setEnvSrcFile, setEnvDstFile):
        logDebug(">>>updateSetEnv", momHandlerLogger)
	logDebug("setEnvSrcFile is %s" % setEnvSrcFile)
	logDebug("setEnvDstFile is %s" % setEnvDstFile)
	processedData = open(setEnvDstFile,"w+")
	setEnvSrcFileHandle = open(setEnvSrcFile)
	data = setEnvSrcFileHandle.read()

	var = ENVIDVAR
	value = h2hprops.get(KYENVID)
	logDebug("replacing variable %s with %s " % (var,value))
	replacedData = data.replace(var, value)
	data = replacedData

	var = APPLICATIONVAR
	value = CCIAPPLICATION
	logDebug("replacing variable %s with %s " % (var,value))
	replacedData = data.replace(var, value)
	data = replacedData

	var = TFFAMILYVAR
	value = h2hprops.get(KYTF_FAMILY)
	logDebug("replacing variable %s with %s " % (var,value))
	replacedData = data.replace(var, value)
	data = replacedData

	for line in SETENVAPACHELINES:
		if data.find(line) >= 0:
			tmp = data.split(line)
			replacedData = tmp[0].rstrip("\n") + tmp[1]
			data = replacedData
	
	processedData.write(replacedData)		
	processedData.close()
	setEnvSrcFileHandle.close()
        logDebug("<<<updateSetEnv", momHandlerLogger)

##############################################
# createSetEnv
# create SetEnv script
##############################################
def createSetEnv():
        logDebug(">>>createSetEnv", momHandlerLogger)
	fwkChanged = False
	dstSetEnv = File.separator.join(
							[h2hprops.get(KYTARGETDIRPATTERN), 
							h2hprops.get(KYCCIVERSION_SOFTLINK), 
							h2hprops.get(KYTARGETCONFIGDIR), 
							SETENVFILE]
							)
	# dont create new one if one exists for the mom version.
	if os.path.exists(dstSetEnv):
		fh = open(dstSetEnv,"r")
		data = fh.read()
		fh.close()
		for line in data.split():
			if line.find(KYTF_FAMILY) > -1:
				family=line.split("=")[1].strip()
				if family.find("#")> -1:
					family = family.split("#")[0]
				if family == h2hprops.get(KYTF_FAMILY):
					logInfo("setenv.sh file exists with the requested FWK version, not creating a new one", momHandlerLogger)
					return
				else:
					fwkChanged = True
					logInfo("setenv.sh file exists with FWK version %s, updating with the FWK version %s requested" % (family, h2hprops.get(KYTF_FAMILY)), momHandlerLogger)
					replacedData = data.replace(family,h2hprops.get(KYTF_FAMILY))
					os.remove(dstSetEnv)
					fh = open(dstSetEnv,"w")
					fh.write(replacedData)
					fh.close()
					return
	
	srcSetEnv = TFDIR + h2hprops.get(KYTF_FAMILY) + APPSETENVFILE
	if not os.path.exists(srcSetEnv):
		if not os.path.exists(TFDIR + h2hprops.get(KYTF_FAMILY)):
			logError("*** No mom fwk %s deployment available for this deployment ***" % TFDIR + h2hprops.get(KYTF_FAMILY), momHandlerLogger)
		else:
			logError("*** Missing setenv.sh in MOM FWK %s install ***" % TFDIR + h2hprops.get(KYTF_FAMILY), momHandlerLogger)
		sys.exit(1)
		
	updateSetEnv(srcSetEnv, dstSetEnv)

	cmdToRun=EXECPERMISSION + dstSetEnv
	logDebug('Applying permission on setenv.sh -> %s' % cmdToRun, momHandlerLogger)
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
	logInfo("Result of applying permission to setenv.sh : %s "% result, momHandlerLogger)
	
	scriptsDir = File.separator.join(
							[h2hprops.get(KYTARGETDIRPATTERN), 
							h2hprops.get(KYCCIVERSION_SOFTLINK), 
							h2hprops.get(KYTARGETSCRIPTSDIR)]
							)							
	os.chdir( scriptsDir )
	cmdToRun = LNCMD + " " + dstSetEnv + ' ' + SETENVFILE 
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)

	momLogDir = VARLOG + File.separator + h2hprops.get(KYENVID) + File.separator + CCIAPPLICATION + File.separator + h2hprops.get(KYCCI_VERSION)
	logInfo("creating Mom Log directory %s" % momLogDir, momHandlerLogger)
	if not os.path.exists(momLogDir):
		os.makedirs(momLogDir)

	logDebug("<<<createSetEnv", momHandlerLogger)
	return fwkChanged

##############################################
# startMom
# start Mom drivers
##############################################
def startMom():
        logDebug(">>>startMom", momHandlerLogger)
	if not isMomRunning():
		logInfo("starting mom drivers....", momHandlerLogger)
		scriptFile = File.separator.join(
								[h2hprops.get(KYTARGETDIRPATTERN), 
								h2hprops.get(KYCCIVERSION_SOFTLINK), 
								h2hprops.get(KYTARGETSCRIPTSDIR), 
								MOMCONTOL_SCRIPT]
								)		
		if os.path.exists(scriptFile):
			cmdToRun = scriptFile + " start" 
			logInfo("starting Mom : %s" % cmdToRun, momHandlerLogger)
			(exitstatus,result)=commands.getstatusoutput(cmdToRun)
			logInfo("Result of starting Mom : "+result, momHandlerLogger)
			if exitstatus > 0:
				logError("*****Mom drivers failed to start, deployment continued...****", momHandlerLogger)
				logError("*****fix the issue and rerun the deployment or start drivers manually ****", momHandlerLogger)
			else:
				time.sleep(10)
				if isMomRunning():
					logInfo("Mom drivers started", momHandlerLogger)
				else:
					logWarn("Mom drivers did not start properly, check this manually", momHandlerLogger)
	else:
		logWarn("Mom drivers are already running", momHandlerLogger)
	logDebug("<<<startMom", momHandlerLogger)

def createEbmomdrvdSHFIle():
        logDebug(">>>createEbmomdrvdSHFIle", momHandlerLogger)
	tfMomFile = TFDIR + h2hprops.get(KYTF_FAMILY) + "/scripts/ebmomdrvd.sh"
	if not os.path.exists(tfMomFile):
		logInfo("script %s not found, creating it..." % tfMomFile, momHandlerLogger)
		srcFile = TFDIR + h2hprops.get(KYTF_FAMILY) + '/scripts/tf/ebmomdrvd.sh'
		logInfo("source file %s to copy from" % srcFile, momHandlerLogger)
		if os.path.exists(srcFile):
			copyfile(srcFile, tfMomFile)
			cmdToRun = "ls -l " + srcFile
			(exitstatus,result)=commands.getstatusoutput(cmdToRun)
			logInfo("Mom status check results : "+result, momHandlerLogger)
			if exitstatus == 0:
				username = result.split()[2]
				group = result.split()[3]

				cmdToRun = "chown " + username + ":" + group + " " + tfMomFile
				logInfo("running %s" % cmdToRun, momHandlerLogger)
				(exitstatus,result) = commands.getstatusoutput(cmdToRun)
				
				cmdToRun = "chmod +x " + tfMomFile
				logInfo("running %s" % cmdToRun, momHandlerLogger)
				(exitstatus,result) = commands.getstatusoutput(cmdToRun)
	logDebug("<<<createEbmomdrvdSHFIle", momHandlerLogger)
		
##############################################
# isMomRunning
# is Mom running
##############################################
def isMomRunning():
        logDebug(">>>isMomRunning", momHandlerLogger)
	logInfo("checking if mom is running...", momHandlerLogger)
	scriptFile = File.separator.join(
							[h2hprops.get(KYTARGETDIRPATTERN), 
							h2hprops.get(KYCCIVERSION_SOFTLINK), 
							h2hprops.get(KYTARGETSCRIPTSDIR), 
							MOMCONTOL_SCRIPT]
							)
	if os.path.exists(scriptFile):
		cmdToRun = scriptFile + " status" 
		logInfo("Obtaining Mom status : %s" % cmdToRun, momHandlerLogger)
		(exitstatus,result)=commands.getstatusoutput(cmdToRun)
		logInfo("result of obtaining mom status : "+result, momHandlerLogger)
		if exitstatus == 0:
			logWarn("Mom drivers are running", momHandlerLogger)
			return True
		else:
			logWarn("Error in obtaining mom drivers status", momHandlerLogger)
			cmdToRun = "find /var/log/" + h2hprops.get(KYENVID) + "/CCI/" + " -name *.pid"
			logInfo("Checking for pid files : %s" % cmdToRun, momHandlerLogger)
			(exitstatus,result)=commands.getstatusoutput(cmdToRun)
			if exitstatus > 0:
				logError("Error in checking pid files, %s" % result, momHandlerLogger)
				logInfo("do you like to continue (y|Y|n|N):", momHandlerLogger)		
				char = getUserAcceptance("yYnN")
				if char != "y":
					sys.exit(1)
			else:
				if result.strip().find(".pid") > -1:
					logError("**** pid files are present and mom drivers are not running ***", momHandlerLogger)
					logInfo("do you like to continue (y|Y|n|N):", momHandlerLogger)		
					char = getUserAcceptance("yYnN")
					if char != "y":
                        			sys.exit(1)
                        logDebug("<<<isMomRunning", momHandlerLogger)
			return False

##############################################
# stopMom
# stop mom drivers
##############################################
def stopMom():
        logDebug(">>>stopMom", momHandlerLogger)
	if isMomRunning():
		logInfo("stopping mom drivers....", momHandlerLogger)
		scriptFile = File.separator.join(
								[h2hprops.get(KYTARGETDIRPATTERN), 
								h2hprops.get(KYCCIVERSION_SOFTLINK), 
								h2hprops.get(KYTARGETSCRIPTSDIR), 
								MOMCONTOL_SCRIPT]
								)
		if os.path.exists(scriptFile):
			cmdToRun = scriptFile + " stop" 
			logInfo("Stopping Mom : %s" % cmdToRun, momHandlerLogger)
			(exitstatus,result)=commands.getstatusoutput(cmdToRun)
			logInfo("result of stopping Mom : "+result, momHandlerLogger)
			if exitstatus > 0:
				logError("Stop mom drivers manually and run the deployment script again" % (exitstatus, result), momHandlerLogger)
	else:
		logWarn("Mom drivers are not stopped, since it is already stopped.", momHandlerLogger)
	logDebug("<<<stopMom", momHandlerLogger)

##############################################
# runEsaTOCCrypto
# run ESATOC Crypto
##############################################
def runEsaTOCCrypto():
  logDebug(">>>runEsaTOCCrypto", momHandlerLogger)
  if h2hprops.get(KYUSE_PREV_EOCTF_CERTS) != "Y":
    import getpass
    madGUIDPIN = getpass.getpass(prompt=PINPROMPT)
    baseDir = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYCCIVERSION_SOFTLINK)
    setenvDir = baseDir + File.separator + h2hprops.get(KYTARGETSCRIPTSDIR)

    esaScript="\n".join([
                        "#!/bin/sh",
                        ". " + setenvDir + "/setenv.sh",
                        h2hprops.get(KYMADESASCRIPT).replace("<PIN>",madGUIDPIN).strip("\""),
                        h2hprops.get(KYGUIDESASCRIPT).replace("<PIN>",madGUIDPIN).strip("\"")
                        ]) + "\n"
    scriptFile = setenvDir + File.separator + ESA_SCRIPT
    data = open(scriptFile,"w")
    data.write(esaScript)
    data.close()

    logInfo("Running script %s (PIN NOT DISPLAYED)" % h2hprops.get(KYMADESASCRIPT), momHandlerLogger)
    logInfo("Running script %s (PIN NOT DISPLAYED)" % h2hprops.get(KYGUIDESASCRIPT), momHandlerLogger)
    cmdToRun=XPERMS + scriptFile
    logDebug('Applying permission on esa.sh -> %s' % cmdToRun, momHandlerLogger)
    (exitstatus, result) = commands.getstatusoutput(cmdToRun)
    logInfo("Result of applying permission to esa.sh : %s " % result, momHandlerLogger)
    tmpFile=setenvDir + File.separator + H2HTMPFILE
    scriptToRun = scriptFile + " 2>" + tmpFile
    logInfo("Running EsaToCrypto : %s" % scriptToRun, momHandlerLogger)
    (exitstatus,result)=commands.getstatusoutput(scriptToRun)
    if exitstatus > 0:
    	logError("ESA script failed - check this after the script completes and run manually", momHandlerLogger)
    fh = open(tmpFile,"r")
    result = fh.read()
    fh.close()
    os.remove(tmpFile)
    logInfo("exitstatus is %s, result is %s" % (exitstatus,result),  momHandlerLogger)
    os.remove(scriptFile)
  logDebug("<<<runEsaTOCCrypto", momHandlerLogger)
#    
