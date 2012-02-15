###########################################################################################
# DeploymentChecks.py
# Perform the following checks
# 1. property checks
# 2. packaging checks
# 3. deployment prechecks
# 4. deployment post checks
#
#	Mahesh Devendran, WebSphere Support, PIU Team
#	Copyright(c) 2010, Euroclear 
############################################################################################


execfile("properties" + File.separator + "piuh2h.properties")
execfile("scripts" + File.separator + "CONSTANTS.py")

deploymentChecksLogger = Logger.getLogger("DeploymentChecks.py")

##########################################
# mandatoryPropertiesCheck
# mandatory properties check
# action - deployment or packaging action
#########################################
def mandatoryPropertiesCheck(action):
        logDebug(">>>mandatoryPropertiesCheck", deploymentChecksLogger)
	# if mandatory properties are in the properties file, return true else return false
	deployProperties = []
	for property in propertyMap:
		if not (property in PACKAGINGPROPERTIES and action == RUNDEPLOYMENT):
			validationString = propertyMap.get(property)
			validationStringParts = validationString.split(":")
			if validationStringParts[0].strip() == "true":
				value = h2hprops.get(property.strip())
				if value == None or value.strip() == "":
					logError("Mandatory property %s not set in %s file" % (property, h2hprops.get(KYPROPERTIESFILE)), utilLogger)
					logDebug("<<<mandatoryPropertiesCheck", deploymentChecksLogger)
					return False
		if action == RUNPACKAGE and property in DEPLOYPROPERTIES:
			deployProperties.append(property)
	# if dependent properties are not available return false
		if property in h2hprops:
			propertyValue = h2hprops.get(property)
			if propertyValue != None and propertyValue.strip() != "":
				dependencies = validationStringParts[1].strip().split(",")
				for dependentProperty in dependencies:
					if dependentProperty != "NONE":
						foundProperty = None
						if dependentProperty.find("|") > -1:
							for orp in dependentProperty.split("|"):
								if orp.strip() in h2hprops:
									if isPropertyAvailable(h2hprops.get(orp.strip())):
										foundProperty = orp.strip()
										break

						logMessage = ""
						if foundProperty != None:
							value = h2hprops.get(foundProperty)
							logMessage="Dependent property %s for property %s not set in %s file" % (foundProperty, property, h2hprops.get(KYPROPERTIESFILE))
						else:							
							value = h2hprops.get(dependentProperty.strip())
							logMessage="Dependent property %s for property %s not set in %s file" % (dependentProperty, property, h2hprops.get(KYPROPERTIESFILE))
							
						if value == None or value.strip() == "":
							logError(logMessage, utilLogger)
							logDebug("<<<mandatoryPropertiesCheck", deploymentChecksLogger)
							return False
							
	if action == RUNPACKAGE:
		h2hprops[KYDEPLOYPROPERTIES] = deployProperties
	h2hprops[KYACTION] = action
	logDebug("<<<mandatoryPropertiesCheck", deploymentChecksLogger)
	return True
	
##########################################
# checkIgnoreFolders
# check for folders to be ignored
# srcDir - source dir to be checked
#########################################
def checkIgnoreFolders(srcDir):	
	ignoreFolders = getVar(h2hprops.get(KYIGNOREFOLDERS)).split(",")
	mapsFolders = getVar(h2hprops.get(KYMAPSDIRS)).split(",")
	soFolders = getVar(h2hprops.get(KYSODIRS)).split(",")
	configFolders = getVar(h2hprops.get(KYCONFIGDIRS)).split(",")
	jvalFolder = getVar(h2hprops.get(KYJVALFOLDER)).strip()
	unknownFoldersCount=0
	for item in os.listdir(srcDir):
		if not ( item in ignoreFolders or item in soFolders or item in mapsFolders or item in configFolders or item in jvalFolder):
			logWarn("**** Unknown dir/file %s in the build directory %s - Process this manually or add it to IGNOREFOLDERS property!!!" % (item,srcDir), deploymentChecksLogger)
			unknownFoldersCount = unknownFoldersCount + 1
	return unknownFoldersCount
	
##########################################
# actionCheck
# check properties for action
# propertyGroup - properties for the action
#########################################
def actionCheck(propertyGroup):
        logDebug(">>>actionCheck", deploymentChecksLogger)
        logDebug("propertyGroup: %s" % propertyGroup, deploymentChecksLogger)
	for property in propertyGroup:
		if property not in h2hprops or h2hprops.get(property) == "":
			logWarn("\t***property %s is not set in the properties file" % property, deploymentChecksLogger)
			logDebug("<<<actionCheck return: False", deploymentChecksLogger)
			return False
	logDebug("<<<actionCheck return: True", deploymentChecksLogger)
	return True

##########################################
# dirCheck
# check for directory existence
# keyDirs - dirs to be checked
#########################################
def dirCheck(keyDirs):
	allDirFound = True
	dirs = getVar(h2hprops.get(keyDirs))
	if not dirs == "":
		for keyDir in dirs.split(","):
			dirFound=False
			builds = sorted(h2hprops.get(KYBUILDS).split(","))		
			unknownFoldersCount = 0
			for build in builds:
				srcDir = h2hprops.get(KYBUILDLOC) + File.separator + build.strip() + File.separator + keyDir				
				if os.path.exists(srcDir):
					dirFound = True
			if not dirFound:
				logError("Directory %s does not exist" % keyDir, deploymentChecksLogger)
				allDirFound = False
	return allDirFound		

##########################################
# mqDirCheck
# check for MQ directory existence
#########################################
def mqDirCheck():
	chklistdir = h2hprops.get(KYMQCHKLISTDIR)
	if chklistdir==None or chklistdir == "" or not os.path.exists(chklistdir):
		chklistdir = h2hprops.get(KYPIUH2HDIR) + File.separator + DATADIR
		h2hprops[KYMQCHKLISTDIR] = chklistdir

##########################################
# jvalPropFileCheck
# check for jval properties
#########################################
def jvalPropFileCheck():
	jvalPropCheck = False
	if h2hprops.get(KYCONFIGPROPERTYCHECK):
		buildDir = h2hprops.get(KYBUILDLOC)
		builds = sorted(getVar(h2hprops.get(KYBUILDS)).split(","))			
		for build in builds:
			srcDir = buildDir + File.separator + build.strip()
			configDirs = h2hprops.get(KYCONFIGDIRS).split(",")
			for dir in configDirs:
				jvalPropFile = srcDir + File.separator + dir.strip('"') + File.separator + JVAL_PROP_FILE
				if os.path.exists(jvalPropFile):
					jvalPropCheck = True
					return jvalPropCheck
	return jvalPropCheck

##########################################
# mqChecklistFilesCheck
# check for mq checklist files
#########################################
def mqChecklistFilesCheck():
	chklistfiles = getVar(h2hprops.get(KYMQCHKLISTFILES)).split(",")
	chklistdir = h2hprops.get(KYMQCHKLISTDIR).strip()
	for chklist in chklistfiles:		
		mqchecklist = chklistdir + File.separator + chklist.strip('"')
		if not os.path.exists(mqchecklist):
			logError("Checklist file %s does not exist" % mqchecklist, mqScriptGenLogger)
			sys.exit(1)
	return True

		
##########################################
# checkESAScript
# check for ESA Script
#########################################
def checkESAScript():
        logDebug(">>>checkESAScript", deploymentChecksLogger)
	if h2hprops.get(KYGUIDESASCRIPT).find("<PIN>") < 0:
		logError("Property %s with value %s must have <PIN> keyword." % (KYGUIDESASCRIPT, h2hprops.get(KYGUIDESASCRIPT)), deploymentChecksLogger)
                logDebug("<<<checkESAScript return: False", deploymentChecksLogger)
		return False                
	if h2hprops.get(KYMADESASCRIPT).find("<PIN>") < 0:
		logError("Property %s with value %s must have <PIN> keyword." % (KYMADESASCRIPT, h2hprops.get(KYMADESASCRIPT)), deploymentChecksLogger)
                logDebug("<<<checkESAScript return: False", deploymentChecksLogger)
		return False
	logDebug("<<<checkESAScript return: True", deploymentChecksLogger)
	return True

def checkMomFwk():
        logDebug(">>checkmomFwk")
	if isPropertyAvailable(h2hprops.get(KYMOMTARFILE)):
                logDebug("Property KYMOMTARFILE available.", deploymentChecksLogger)
		if os.path.exists(h2hprops.get(KYMOMTARFILE)):
                        logDebug("Files KYMOMTARFILE exists.",deploymentChecksLogger)
                        logDebug("<<checkmomFwk: return True")
			return True
		else:
                        logError("Tar file cannot be found! %s " % h2hprops.get(KYMOMTARFILE),deploymentChecksLogger)
	logDebug("<<checkmomFwk: return False")			
	return False

def requestAndPackageCheck(options, mqPropertyCheck, mapsPropertyCheck, soPropertiesCheck, eoctfPropertiesCheck, soDirCheck, configDirCheck, mapsDirCheck, momFWKCheck, certsPropertiesCheck):
        logDebug(">>>requestAndPackageCheck", deploymentChecksLogger)
        logDebug("mqPropertyCheck: %s" % mqPropertyCheck, deploymentChecksLogger)
	if not certsPropertiesCheck:
		logError("Property checks for MAD/GUID certs failed, check previous error messages", deploymentChecksLogger)		
		sys.exit(1)
		
	if not (mqPropertyCheck or mapsPropertyCheck or soPropertiesCheck or eoctfPropertiesCheck):
		logError("*** Insufficient properties in the properties file for performing deployment ***", deploymentChecksLogger)	
		sys.exit(1)
	
	if not (soDirCheck or configDirCheck or mapsDirCheck):
		logError("*** Directory names configured does not exit ***", deploymentChecksLogger)
		sys.exit(1)

	if mqPropertyCheck:
		getChkListVersion()
	else:
		h2hprops[KYMQCHECKLIST_VERSION] = ""

	#if options.momDeploy != None and "fwk" in options.momDeploy.lower() and not momFWKCheck:
	#	logError("MOM FWK properties not available/set in properties file", deploymentChecksLogger)
	#	sys.exit(1)

	#if options.momDeploy != None and "config" in options.momDeploy and options.mqCheckList == None:
	#	if not isPropertyAvailable(h2hprops.get(KYPARAM_QENV)):
	#		logError("Property %s not available in property file for this request" % KYPARAM_QENV, deploymentChecksLogger)
	#		sys.exit(1)
	logDebug("<<<requestAndPackageCheck", deploymentChecksLogger)
	
##########################################
# packagingChecks
# packaging checks
#########################################
def packagingChecks(options):
        logDebug(">>>packagingChecks", deploymentChecksLogger)

        logDebug("options: %s" % options, deploymentChecksLogger)
        options_dict = vars(options)
        logDebug("options_dict: %s" % options_dict, deploymentChecksLogger)

        basicPropertyCheck = "NA"
        mqPropertyCheck = "NA"
        mapsPropertyCheck = "NA"
        soPropertiesCheck = "NA"
        configPropertiesCheck = "NA"
        momFWKCheck = "NA"
        eoctfPropertiesCheck = "NA"
        jvalPropCheck = "NA"
        soDirCheck = "NA"
        configDirCheck = "NA"
        mapsDirCheck = "NA"
        unknownFoldersCount = "NA"
        certsPropertiesCheck = "NA"
        
	if not mandatoryPropertiesCheck(RUNPACKAGE):
		sys.exit(1)
	
	logDebug("Performing packaging and property file analysis.......", deploymentChecksLogger)
	logDebug("performing min required property check", deploymentChecksLogger)
	basicPropertyCheck = actionCheck(BASICPROPERTIES)	
	if not basicPropertyCheck:
		logError("*** Min required information for packaging missing in the properties file ***", deploymentChecksLogger)
		sys.exit(1)
	logDebug("completed min required property check", deploymentChecksLogger)

	if options_dict.get('mqCheckList'):
                logDebug("performing MQ required property check", deploymentChecksLogger)
                mqDirCheck()
                mqPropertyCheck = actionCheck(MQPROPERTIES)
                logDebug("mqPropertyCheck: %s" % mqPropertyCheck, deploymentChecksLogger)
                if mqPropertyCheck:
                        logDebug("Running mqCheckListFilesCheck.", deploymentChecksLogger)
                        mqPropertyCheck = mqChecklistFilesCheck()
                        logDebug("mqPropertyCheck: %s" % mqPropertyCheck, deploymentChecksLogger)	
		
                h2hprops[KYMQPROPERTYCHECK] = mqPropertyCheck
                logDebug("completed MQ required property check", deploymentChecksLogger)

        if options_dict.get('momDeploy'):
                logDebug("performing MAPS required property check", deploymentChecksLogger)
                mapsPropertyCheck = actionCheck(MAPSPROPERTIES)
                h2hprops[KYMAPSPROPERTYCHECK] = mapsPropertyCheck
                logDebug("completed MAPS required property check", deploymentChecksLogger)

                logDebug("performing SO required property check", deploymentChecksLogger)
                soPropertiesCheck = actionCheck(SOPROPERTIES)
                h2hprops[KYSOPROPERTYCHECK] = soPropertiesCheck
                logDebug("completed SO required property check", deploymentChecksLogger)

                logDebug("performing CONFIG required property check", deploymentChecksLogger)
                configPropertiesCheck = actionCheck(CONFIGPROPERTIES)
                h2hprops[KYCONFIGPROPERTYCHECK] = configPropertiesCheck
                logDebug("completed CONFIG required property check", deploymentChecksLogger)

                soDirCheck = False
                if soPropertiesCheck:
                        soDirCheck = dirCheck(KYSODIRS)
	
                configDirCheck = dirCheck(KYCONFIGDIRS)
                mapsDirCheck = dirCheck(KYMAPSDIRS)
                jvalPropCheck = jvalPropFileCheck()
                h2hprops[KYJVALPROPFILECHECK] = jvalPropCheck

                unknownFoldersCount = 0
                if basicPropertyCheck and (mapsPropertyCheck or soPropertiesCheck or eoctfPropertiesCheck or configPropertiesCheck):
                        buildDir = h2hprops.get(KYBUILDLOC)
                        builds = sorted(h2hprops.get(KYBUILDS).split(","))		
                        for build in builds:
                                srcDir = buildDir + File.separator + build.strip()
                                logDebug("checking build dir %s " % srcDir, deploymentChecksLogger)
                                if os.path.exists(srcDir):
                                        unknownFoldersCount = checkIgnoreFolders(srcDir) + unknownFoldersCount

                logDebug("performing EOCTF required property check", deploymentChecksLogger)
                eoctfPropertiesCheck = False
                if configPropertiesCheck and actionCheck(EOCTFPROPERTIES):
                        eoctfPropertiesCheck = True
                h2hprops[KYEOCTFPROPERTYCHECK] = eoctfPropertiesCheck
                logDebug("completed EOCTF required property check", deploymentChecksLogger)

                if eoctfPropertiesCheck:
                        certsPropertiesCheck = actionCheck(CERTSPROPERTIES) and checkESAScript()				
                else:
			logError("*** Insufficient EocTF Certs properties in the properties file for performing deployment ***", deploymentChecksLogger)	
			sys.exit(1)
		h2hprops[KYCERTSPROPERTYCHECK] = certsPropertiesCheck
		logDebug("completed EOCTF CERTS required property check", deploymentChecksLogger)

        if options_dict.get('fwkDeploy'):
                logDebug("performing CONFIG required property check", deploymentChecksLogger)
                configPropertiesCheck = actionCheck(CONFIGPROPERTIES)
                h2hprops[KYCONFIGPROPERTYCHECK] = configPropertiesCheck
                logDebug("completed CONFIG required property check", deploymentChecksLogger)
                
                logDebug("performing EOCTF required property check", deploymentChecksLogger)
                eoctfPropertiesCheck = False
                if configPropertiesCheck and actionCheck(EOCTFPROPERTIES):
                        eoctfPropertiesCheck = True
                h2hprops[KYEOCTFPROPERTYCHECK] = eoctfPropertiesCheck
                logDebug("completed EOCTF required property check", deploymentChecksLogger)

                momFWKCheck = checkMomFwk()

                if not momFWKCheck:
                        logError("*** Insufficient MOM properties in the properties file for performing deployment ***", deploymentChecksLogger)	
			sys.exit(1)

                if eoctfPropertiesCheck:
                        logDebug("started EOCTF CERTS required property check", deploymentChecksLogger)                        
                        certsPropertiesCheck = actionCheck(CERTSPROPERTIES) and checkESAScript()
                        logDebug("certsPropertiesCheck: %s" % certsPropertiesCheck, deploymentChecksLogger)
                        h2hprops[KYCERTSPROPERTYCHECK] = certsPropertiesCheck
                        logDebug("completed EOCTF CERTS required property check", deploymentChecksLogger)
                else:
			logError("*** Insufficient EocTF Certs properties in the properties file for performing deployment ***", deploymentChecksLogger)	
			sys.exit(1)		
		
	
	logInfo("\n-------------------------------\nPackaging and property file analysis summary\n*****************************\n" +
	"\nMin required information available                 :%s" % str(basicPropertyCheck) +
	"\nMQ deployment information available                :%s" % str(mqPropertyCheck) +
	"\nMAPS deployment information available              :%s" % str(mapsPropertyCheck) +
	"\nSO deployment information available                :%s" % str(soPropertiesCheck) +
	"\nCONFIG deployment information available            :%s" % str(configPropertiesCheck) +
	"\nMOM FWK deployment information available           :%s" % str(momFWKCheck) +
	"\nEOCTF deployment information available             :%s" % str(eoctfPropertiesCheck) +
	"\njval.prop file available                           :%s" % str(jvalPropCheck) +
	"\nSO directories available in build                  :%s" % str(soDirCheck) +
	"\nCONFIG directories available in build              :%s" % str(configDirCheck) +
	"\nMAPS directories available in build                :%s" % str(mapsDirCheck) +
	"\nUnknown dir/file count in the source directory     :%s" % str(unknownFoldersCount) +
        "\nCertificates properties check                      :%s" % str(certsPropertiesCheck) +
	"\n*****************************\n*** Packaging prechecks completed ***\n-------------------------------", deploymentChecksLogger)

	requestAndPackageCheck(options, mqPropertyCheck, mapsPropertyCheck, 
		soPropertiesCheck, eoctfPropertiesCheck, soDirCheck, configDirCheck, mapsDirCheck, momFWKCheck, certsPropertiesCheck)
	logDebug("<<<packagingChecks", deploymentChecksLogger)
		
##########################################
# checkTargetHost
# check for target host
#########################################
def checkTargetHost():
	import socket
	if not socket.gethostname() in h2hprops.get(KYTARGETHOSTNAMES).split(","):
		logError("H2H Deployment cant be performed on this host, supported host(s) : %s" % h2hprops.get(KYTARGETHOSTNAMES), deploymentChecksLogger)
		sys.exit(1)

##########################################
# checkFS
# check file system
#########################################
def checkFS():
	fileSystemCheck=True
	logDebug("Checking FS -> %s" % (DFKCMD + " " + h2hprops.get(KYTARGETDIRPATTERN)), deploymentChecksLogger)
	(exitstatus, result) = commands.getstatusoutput(DFKCMD + " " + h2hprops.get(KYTARGETDIRPATTERN))
	if exitstatus > 0:
		if result == None or result == "":
			result = "File system %s not available/mounted" % h2hprops.get(KYTARGETDIRPATTERN)
		logError("Error in checking FS %s\n%s" % (h2hprops.get(KYTARGETDIRPATTERN), result), deploymentChecksLogger)
		fileSystemCheck=False
	else:
		logDebug("Result of checking FS %s\n%s" % (h2hprops.get(KYTARGETDIRPATTERN), result), deploymentChecksLogger)

	logdirFS = h2hprops.get(KYTARGETH2HLOGDIR).split(File.separator + h2hprops.get(KYCCI_VERSION))[0]
	if isPropertyAvailable(logdirFS):
		logDebug("Checking FS -> %s" % (DFKCMD + " " + logdirFS), deploymentChecksLogger)
		(exitstatus, result) = commands.getstatusoutput(DFKCMD + " " + logdirFS)
		if exitstatus > 0:
			if result == None or result == "":
				result = "File system %s not available/mounted" % logdirFS
			logError("Error in checking FS %s\n%s" % (logdirFS, result), deploymentChecksLogger)
			fileSystemCheck=False
		else:
			logDebug("Result of checking FS %s\n%s" % (logdirFS, result), deploymentChecksLogger)
	else:
		logError("H2H log directory not available in the properties file", deploymentChecksLogger)
		fileSystemCheck=False

	return fileSystemCheck
		
##########################################
# checkHACMP
# check HACMP
#########################################
def checkHACMP(precheck):
	if os.path.exists(CLUSTERLOC):
		cmdToRun = "find " + CLUSTERLOC + " -name app.cfg -exec grep " + MOMCONTOL_SCRIPT + " {} \;"
		logInfo("Running script %s" % cmdToRun, deploymentChecksLogger)
		(exitstatus, result) = commands.getstatusoutput(cmdToRun)
		logInfo("Result is : %s "% result, deploymentChecksLogger)
		if  exitstatus == 0:
			if not precheck:
				cmdToRun = "ps -ef|grep clinfo|grep -v grep"
				logInfo("Running script %s" % cmdToRun, deploymentChecksLogger)
				(exitstatus, result) = commands.getstatusoutput(cmdToRun)
				logInfo("Result is : %s "% result, deploymentChecksLogger)
				if exitstatus == 0 and result.find("clinfo") > -1:					
					logWarn("HACMP Environment : Ensure you have brought the respective cluster RESOURCE GROUP offline to continue with deployment\n", deploymentChecksLogger)
					logInfo("do you like to continue (y|Y|n|N)[ONLY AFTER RESOURCE GROUP is offline]:", deploymentChecksLogger)
					char = getUserAcceptance("yYnN")
					if char != "y":
						sys.exit(1)
			return True
	return False

##########################################
# getCurrentH2HVersion
# get current h2h version
#########################################
def getCurrentH2HVersion():
	currentH2HVersion = None
	if os.path.exists(h2hprops.get(KYTARGETDIRPATTERN)):
		dirList = sorted(os.listdir(h2hprops.get(KYTARGETDIRPATTERN)))
		for file in dirList:
			try:
				t = float(file)
				currentH2HVersion = file
			except ValueError:
				continue
	return currentH2HVersion
	

##########################################
# checkQmgr
# check for qmgr
#########################################
def checkQmgr():
	cmdToRun = "dspmq"
	logInfo("Running script %s" % cmdToRun, deploymentChecksLogger)
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)					
	logDebug("Result is : %s "% result, deploymentChecksLogger)
	qmgrFound = False
	if exitstatus == 0:
		for line in result.split("\n"):
			if line.find(h2hprops.get(KYPARAM_QUEUE_MANAGER)) >= 0:
				if line.find("Ended") >= 0:
					logError("Qmgr %s is not running" % h2hprops.get(KYPARAM_QUEUE_MANAGER), deploymentChecksLogger)
					sys.exit(1)
				elif line.find("Running") >= 0:
					logInfo("Qmgr %s is available and in running state" % h2hprops.get(KYPARAM_QUEUE_MANAGER), deploymentChecksLogger)
					qmgrFound = True
		if qmgrFound == False:
			logError("Qmgr %s is not found on the host" % h2hprops.get(KYPARAM_QUEUE_MANAGER))
	else:
		logError("Error in retrieving qmgr information", deploymentChecksLogger)
	return qmgrFound					

##########################################
# getMQVersion
# get mq verion
#########################################
def getMQVersion():
	mqVersion = None
	cmdToRun = "dspmqver"
	logInfo("Running script %s" % cmdToRun, deploymentChecksLogger)
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)					
	logDebug("Result is : %s "% result, deploymentChecksLogger)
	if exitstatus == 0:
		for line in result.split("\n"):
			if line.find("Version") >= 0:
				mqVersion = line.split(":")[1].strip()
	h2hprops[KYMQ_VERSION] = mqVersion
	return mqVersion

def checkMomInstalled():
	if getVar(h2hprops.get(KYTF_FAMILY)) != "":
		if not os.path.exists(TFDIR + h2hprops.get(KYTF_FAMILY)):
			logError("Mom installtion %s not found" % TFDIR + h2hprops.get(KYTF_FAMILY), deploymentChecksLogger)
		return True
	else:
		return False

def checkWTX():
	if getVar(h2hprops.get(KYWTXLOC)) != "":
		if not os.path.exists(h2hprops.get(KYWTXLOC)):
			logError("WTX %s installation not found" % h2hprops.get(KYWTXLOC), deploymentChecksLogger)
		return True
	else:
		return False

def checkOwnerGroup():
	if getVar(h2hprops.get(KYH2HUSER)) != "":
		if os.path.exists(h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYCCIVERSION_SOFTLINK)):
			cmdToRun = "find " + h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYCCIVERSION_SOFTLINK) + " -user " + h2hprops.get(KYH2HUSER)
			logInfo("Running script %s" % cmdToRun, deploymentChecksLogger)
			(exitstatus, result) = commands.getstatusoutput(cmdToRun)					
			logDebug("Result is : %s "% result, deploymentChecksLogger)
			if exitstatus != 0:
				logError("H2H is not owned by %s user" % h2hprops.get(KYH2HUSER), deploymentChecksLogger)
				sys.exit(1)
			
		cmdToRun = "id " + h2hprops.get(KYH2HUSER)
		logInfo("Running script %s" % cmdToRun, deploymentChecksLogger)
		(exitstatus, result) = commands.getstatusoutput(cmdToRun)					
		logDebug("Result is : %s "% result, deploymentChecksLogger)
		if exitstatus == 0:
			if result.find(h2hprops.get(KYH2HGROUP)) == 0:
				logError("User %s is not part of the group %s" % (h2hprops.get(KYH2HUSER), h2hprops.get(KYH2HGROUP)), deploymentChecksLogger)
				sys.exit(1)
		return True
	else:
		return False

def getDeployedPIUH2HVersion():
	version = None	
	versionFile = File.separator.join([
						h2hprops.get(KYTARGETDIRPATTERN),
						h2hprops.get(KYTARGETRELEASEDIR),
						h2hprops.get(KYCCI_VERSION),
						VERSIONFILE])
	if os.path.exists(versionFile):
		version = open(versionFile).read()
	h2hprops[KYPIUH2H_VERSION]=version
	return version
	
def getCurrentPIUH2HVersion():
	version = None
	if os.path.exists(VERSIONFILE):
		version = open(VERSIONFILE).read()
	return version

def checkPaths(requested, checkType):
        logDebug(">>>checkPaths", deploymentChecksLogger)
	if not requested:
		return True
		
	jvalFile = h2hprops[KYPACKAGE_LOCATION] + File.separator + h2hprops.get(KYTARGETMAPSDIR) + File.separator + JVAL_PROP_FILE
	jvalFileTestResult = True
	if os.path.exists(jvalFile):
		data = open(jvalFile)
		for line in data:
			if re.match("^#", line) == None:
				if line.find(JVALMSGDIRPROP) > -1:
					path = line.split("=")[1]
					if not os.path.exists(path.strip()):
						jvalFileTestResult = False
						logError("**** %s path %s in %s does not exist or not correct" % (JVALMSGDIRPROP, path, jvalFile), deploymentChecksLogger)
				if line.find(JVALBICDEFPROP) > -1:
					path = line.split("=")[1]
					if not os.path.exists(path.strip()):
						jvalFileTestResult = False
						logError("**** %s path %s in %s does not exist or not correct" % (JVALBICDEFPROP, path, jvalFile), deploymentChecksLogger)
				if line.find(JVALCURRDEFPROP) > -1:
					path = line.split("=")[1]
					if not os.path.exists(path.strip()):
						jvalFileTestResult = False
						if checkType == 'precheck':
							logWarn("**** %s path %s in %s does not exist or not correct" % (JVALCURRDEFPROP, path, jvalFile), deploymentChecksLogger)
						else:
							logError("**** %s path %s in %s does not exist or not correct" % (JVALCURRDEFPROP, path, jvalFile), deploymentChecksLogger)
		data.close()
		
	eoctfPathTestResult = True	
	eoctfFile = h2hprops[KYPACKAGE_LOCATION] + File.separator + h2hprops.get(KYTARGETCONFIGDIR) + File.separator + EOCTFFILE
	
	if os.path.exists(eoctfFile):
		data = open(eoctfFile)
		for line in data:
			if line.find(h2hprops.get(KYTARGETDIRPATTERN)) > -1:
				path = line.split(">")[1]
				path = path.split("<")[0]
				if not os.path.exists(path.strip()):
					eoctfPathTestResult = False
					if checkType == 'precheck':
						logWarn("**** %s path %s in %s does not exist or not correct" % (JVALCURRDEFPROP, path, jvalFile), deploymentChecksLogger)
					else:
						logError("**** path %s in %s does not exist or not correct" %(path, eoctfFile), deploymentChecksLogger)
		data.close()	
	if checkType == 'precheck':
		logInfo("\t ---> If you are deploying the config for the first time, ignore the warnings displayed above", deploymentChecksLogger)
		logDebug("<<<checkPaths", deploymentChecksLogger)
		return True
        logDebug("<<<checkPaths", deploymentChecksLogger)
	return 	jvalFileTestResult and eoctfPathTestResult

def packageAndActionCheck(pathCheck, fileSystemChecks, qmgrAvailable, wtxInstalled, momInstalled, args):
#		-- check if the respective props are available
#		-- check if those files are present
#		-- check if the target details are met for this action
        logDebug(">>>packageAndActionCheck", deploymentChecksLogger)
	if not pathCheck:
		logInfo("Config path check failed, check EocTF.xml and jval.props", deploymentChecksLogger)
		sys.exit(1)
	else:
		logInfo("Config paths check failures not affecting this request, continuing...", deploymentChecksLogger)

	if not fileSystemChecks and (args.deployH2H or args.fullDeployment):
		logInfo("File system check failed, NOTE: If you choose to continue, the script will create them as directories", deploymentChecksLogger)
		logInfo("do you like to continue (y|Y|n|N):", deploymentChecksLogger)		
		char = getUserAcceptance("yYnN")
		if char != "y":
			sys.exit(1)
		elif char in "nN":
			logInfo("File system failures not affecting MQ deployment, continuing with deployment...", deploymentChecksLogger)
	
	if not qmgrAvailable and (args.deployMQ or args.fullDeployment):
		logError("Qmgr %s not available" % h2hprops.get(KYPARAM_QUEUE_MANAGER), deploymentChecksLogger)
		sys.exit(1)

	if args.deployMQ or args.fullDeployment:	
		mqPropertyCheck = actionCheck(['PARAM_QUEUE_MANAGER','MQSCSCRIPTS'])	
		if mqPropertyCheck:
			mqScriptFiles = h2hprops[KYMQSCSCRIPTS].split(",")
			for mqScript in sorted(mqScriptFiles):
					srcFile = h2hprops.get(KYPACKAGE_LOCATION) + File.separator + mqScript.strip("\"")
					if not os.path.exists(srcFile):
						logError("Checklist file %s not available in the package" % srcFile, deploymentChecksLogger)
						mqPropertyCheck = False		
			if isPropertyAvailable(h2hprops.get(KYSCYEXIT)):
				if not os.path.exists(h2hprops.get(KYSCYEXIT).strip("(")[0]):
					logError("Mom security exit file %s not available on this host" % h2hprops.get(KYSCYEXIT), deploymentChecksLogger)
					mqPropertyCheck = False
		if not mqPropertyCheck:
			logError("*** Package/Pre-requiste(s) does not meet this action request, see previous error messages in this log. ****", deploymentChecksLogger)
			sys.exit(1)
			
	if args.deployH2H or args.fullDeployment:
		deployH2HCheck = True
		baseDir = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYCCIVERSION_SOFTLINK)

		if not wtxInstalled:
			logError("WTX is not installed", deploymentChecksLogger)
			deployH2HCheck = False
			
		if not momInstalled:
			logError("Mom FWK is not installed", deploymentChecksLogger)
			if args.fullDeployment or args.installMOMFwk:
				if not isPropertyAvailable(h2hprops.get(KYMOMTARFILENAME)):					
					deployH2HCheck = False
				else:
					if not os.path.exists(h2hprops.get(KYPACKAGE_LOCATION) + File.separator + MOMFWKDIR + File.separator + h2hprops.get(KYMOMTARFILENAME)):
						deployH2HCheck = False
					else:
						logInfo("Mom not installed and will be performed as part of this deployment", momHandlerLogger)
			else:
				deployH2HCheck = False				

		if isPropertyAvailable(h2hprops.get(KYTARGETCONFIGDIR)):
			srcDir = h2hprops[KYPACKAGE_LOCATION] + File.separator + h2hprops.get(KYTARGETCONFIGDIR)	
			dstDir = baseDir + File.separator + h2hprops.get(KYTARGETCONFIGDIR)
			if h2hprops.get(KYUSE_PREV_EOCTF_CERTS) == "Y":
				if os.path.exists(srcDir + File.separator + EOCTFFILE):
					if not os.path.exists(dstDir + File.separator + EOCTFFILE):
						logError("USE_PREV_EOCTF_CERTS=Y and %s is not available" % (dstDir + File.separator + EOCTFFILE), deploymentChecksLogger)
						deployH2HCheck = False
			else:
				if not os.path.exists(srcDir + File.separator + EOCTFFILE):
					logError("USE_PREV_EOCTF_CERTS=N and %s is not available" % (dstDir + File.separator + EOCTFFILE), deploymentChecksLogger)
					deployH2HCheck = False
				if not isPropertyAvailable(h2hprops.get(KYMADESASCRIPT)) or not isPropertyAvailable(h2hprops.get(KYGUIDESASCRIPT)):
					logError("Esa details (MADESASCRIPT, GUIDESASCRIPT) not available in property file for this deployment", deploymentChecksLogger)
					deployH2HCheck = False				

		if not deployH2HCheck:
			logError("*** Package/Pre-requiste(s) does not meet this action request, see previous error messages in this log. ****", deploymentChecksLogger)
			sys.exit(1)
	logDebug("<<<packageAndActionCheck", deploymentChecksLogger)

def performDeploymentPrechecks(args):
        logDebug(">>>performDeploymentPrechecks", deploymentChecksLogger)
	if not mandatoryPropertiesCheck(RUNDEPLOYMENT):
		sys.exit(1)

	checkTargetHost()		
	fileSystemChecks = checkFS()
	hacmpEnvironment = checkHACMP(args.precheck)
	currentH2HVersion = getCurrentH2HVersion()
	momInstalled = checkMomInstalled()
	wtxInstalled = checkWTX()
	ownerGroupCheck = checkOwnerGroup()		
	qmgrAvailable = checkQmgr()
	mqVersion = None
	if qmgrAvailable:		
		mqVersion = getMQVersion()
		securityExitStatus = getSecurityExitsStatus()
	deployedPIUH2HVersion = getDeployedPIUH2HVersion()
	currentPIUH2HVersion = getCurrentPIUH2HVersion()
	pathCheck = checkPaths(args.deployH2H, 'precheck')
	
	logInfo("\n-------------------------------\nDeployment precheck summary\n*****************************" +
	"\nTargetHost matching                                :True" +
	"\nFile System Check                                  :%s" % str(fileSystemChecks) +
	"\nHACMP Environment                                  :%s" % str(hacmpEnvironment) +
	"\nCurrent CCI H2H Version                            :%s" % str(currentH2HVersion) +
	"\nCCI H2H Version to be deployed                     :%s" % h2hprops.get(KYCCI_VERSION) +
	"\nEocTF.xml and jval.prop paths check                :%s" % str(pathCheck) +
	"\nQueue Manager                                      :%s" % h2hprops.get(KYPARAM_QUEUE_MANAGER) +
	"\nQueue Manager available                            :%s" % str(qmgrAvailable) +
	"\nMQ Version                                         :%s" % str(mqVersion) +
	"\nSecurity Exits defined                             :%s" % str(securityExitStatus) +
	"\nMom TF Family Installed                            :%s" % str(momInstalled) +
	"\nWTX Installed                                      :%s" % str(wtxInstalled) +
	"\nH2H Owner and Group check                          :%s" % str(ownerGroupCheck) +
	"\nDeployed PIUH2H Script Version                     :%s" % str(deployedPIUH2HVersion) +
	"\nCurrent PIUH2H Script Version                      :%s" % str(currentPIUH2HVersion) +
	"\n*****************************\n*** Deployment prechecks completed ***\n-------------------------------", deploymentChecksLogger)
			
	packageAndActionCheck(pathCheck, fileSystemChecks, qmgrAvailable, wtxInstalled, momInstalled, args)
	logDebug("<<<performDeploymentPrechecks", deploymentChecksLogger)

def checkMomDriversCount(momDriversRunning):
        logDebug(">>>checkMomDriversCount", deploymentChecksLogger)
	momCountOkCheck = False
	eocTFFile = File.separator.join(
							[h2hprops.get(KYTARGETDIRPATTERN), 
							h2hprops.get(KYCCIVERSION_SOFTLINK), 
							h2hprops.get(KYTARGETCONFIGDIR), 
							EOCTFFILE]
							)
	h2hprops[KYMOMRUNNING_COUNT]=0
	h2hprops[KYMOMCONFIG_COUNT]=0
	h2hprops[KYMOMORIGINATORS_COUNT]=0
	momPsCount = 0
	if momDriversRunning:
		logInfo("Running script %s" % LISTMOMPS, deploymentChecksLogger)
		(exitstatus, result) = commands.getstatusoutput(LISTMOMPS)
		logInfo("Result is : %s "% result, deploymentChecksLogger)
		if exitstatus != 0:
			logError("Mom drivers are not running", deploymentChecksLogger)
		else:
			logInfo("Running script %s" % MOMCOUNT, deploymentChecksLogger)
			(exitstatus, result) = commands.getstatusoutput(MOMCOUNT)
			logInfo("Result is : %s "% result, deploymentChecksLogger)
			momPsCount = result.strip().split(" ")[0].strip()
			h2hprops[KYMOMRUNNING_COUNT]=momPsCount
	
	cmdToRun = " grep \"Service Originator\" " + eocTFFile +"|grep -v SPCCIQueues|grep -v GUID|wc"
	logInfo("Running script %s" % cmdToRun, deploymentChecksLogger)
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
	logInfo("Result is : %s "% result, deploymentChecksLogger)
	momConfigCount = result.strip().split(" ")[0].strip()
	h2hprops[KYMOMCONFIG_COUNT]=momConfigCount
	
	scriptFile = File.separator.join(
							[h2hprops.get(KYTARGETDIRPATTERN), 
							h2hprops.get(KYCCIVERSION_SOFTLINK), 
							h2hprops.get(KYTARGETSCRIPTSDIR), 
							MOMCONTOL_SCRIPT]
							)
	cmdToRun = "grep mom_originators= " + scriptFile
	logInfo("Running script %s" % cmdToRun, deploymentChecksLogger)
	(exitstatus, result) = commands.getstatusoutput(cmdToRun)
	logInfo("Result is : %s "% result, deploymentChecksLogger)
	if exitstatus != 0:
		logError("Error in obtaining configured mom count from %s" % scriptFile, deploymentChecksLogger)
		return False
		
	momOriginators = result.split("=")[1].strip("\"")
	if momOriginators == "all":
		logError("Mom drivers running %s does not match with the configured drivers '%s'\n" % (momPsCount, momOriginators), deploymentChecksLogger)
	else:
		configuredMomCount = len(momOriginators.split(" "))
		h2hprops[KYMOMORIGINATORS_COUNT]=configuredMomCount
		if configuredMomCount == int(momPsCount):
			logInfo("Mom drivers running %s count is matching with the configured %s count" % (momPsCount, str(configuredMomCount)), deploymentChecksLogger)
			momCountOkCheck = True
		else:
			logError("Mom drivers running %s does not match with the configured drivers %s\n" % (momPsCount, str(configuredMomCount)), deploymentChecksLogger)
	if momPsCount == momConfigCount:
		logInfo("Mom drivers running %s count is matching with the configured %s count" % (momPsCount, str(momConfigCount)), deploymentChecksLogger)
		momCountOkCheck = True				
        logDebug("<<<checkMomDriversCount", deploymentChecksLogger)
	return momCountOkCheck

def checkMomQueues():
	pass
	
def deploymentPostChecks(args):
        logDebug(">>>deploymentPostChecks", deploymentChecksLogger)
	qmgrAvailable = checkQmgr()
	channelOKStatus = None
	momDriversRunning = None
	securityExitStatus = None
	
	if args.deployMQ or args.fullDeployment:
		if qmgrAvailable:
			channelOKStatus = h2hprops.get(KYCHSTATUS)
			securityExitStatus = getSecurityExitsStatus()
	else:
		channelOKStatus="Check not performed for this request"
		h2hprops[KYCHANNELRUNNING_COUNT]="Check not performed for this request"
		h2hprops[KYSENDERCHANNELS_COUNT]="Check not performed for this request"
		
	if args.fullDeployment or args.deployH2H:
		momDriversRunning = isMomRunning()
		checkMomDriversCount(momDriversRunning)
		if not momDriversRunning:
			checkMomQueues()
	else:
		momDriversRunning="Check not performed for this request"
		h2hprops[KYMOMRUNNING_COUNT]="Check not performed for this request"
		h2hprops[KYMOMCONFIG_COUNT]="Check not performed for this request"
		h2hprops[KYMOMORIGINATORS_COUNT]="Check not performed for this request"

	pathCheck = checkPaths(args.fullDeployment or args.deployH2H, 'postcheck')

	logInfo("\n-------------------------------\nPost deployment check summary\n*****************************" +
	"\nMQ Version                                    :%s" % h2hprops.get(KYMQ_VERSION) + 
	"\nQueue Manager                                 :%s" % h2hprops.get(KYPARAM_QUEUE_MANAGER) +
	"\nQueue Manager available                       :%s" % str(qmgrAvailable) +
	"\nChannels running status                       :%s" % str(channelOKStatus) +
	"\nSender Channels count                         :%s" % h2hprops.get(KYSENDERCHANNELS_COUNT) +
	"\nChannels running count                        :%s" % h2hprops.get(KYCHANNELRUNNING_COUNT) +
	"\nSecurity Exits defined                        :%s" % str(securityExitStatus) +
	"\nAMQError log errors                           :TODO - Next Release" +
	"\nCCI H2H version deployed                      :%s" % h2hprops.get(KYCCI_VERSION) +
	"\nMom TF Family                                 :%s" % h2hprops.get(KYTF_FAMILY) +
	"\nMom Drivers status                            :%s" % str(momDriversRunning) +
	"\nMom Drivers running                           :%s" % h2hprops.get(KYMOMRUNNING_COUNT) +
	"\nMom Drivers configured in EocTF               :%s" % h2hprops.get(KYMOMCONFIG_COUNT) +
	"\nMom Drivers configured in r_app_rg1.sh        :%s" % h2hprops.get(KYMOMORIGINATORS_COUNT) +
	"\nEocTF.xml and jval.prop paths check           :%s" % str(pathCheck) +
	"\nMissing Queues                                :TODO - Next Release" +
	"\nMom Error Log errors                          :TODO - Next Release" +
	"\nMAD password generated                        :TODO - Next Release" +
	"\nGUID password generated                       :TODO - Next Release" +
	"\nStandard security check(permissions,access)   :TODO - Next Release" +
	"\nHACMP Checks                                  :TODO - Next Release" +
	"\nDeployed PIUH2H Script Version                :%s" % h2hprops.get(KYPIUH2H_VERSION) +
	"\n*****************************\n*** Post deployment check completed ***\n-------------------------------", deploymentChecksLogger)
	
	if not (pathCheck or qmgrAvailable or channelOKStatus or momDriversRunning):
		logError("****Deployment failed****", deploymentChecksLogger)
	logDebug("<<<deploymentPostChecks", deploymentChecksLogger)
