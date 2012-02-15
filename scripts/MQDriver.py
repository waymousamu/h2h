###########################################################################################
# MQDriver.py
#	Script to perform MQ Deployment
#
#	Mahesh Devendran, WebSphere Support, PIU Team
#	Copyright(c) 2010, Euroclear 
############################################################################################

import commands

execfile("scripts" + File.separator + "util.py")
execfile("scripts" + File.separator + "CONSTANTS.py")

mqDriverLogger = Logger.getLogger("MQDriver.py")

def backupFileAndRemove(fileName):
	backupFile = fileName + str(date.today()) + time.strftime("%H-%M-%S", time.gmtime())
	copyfile(fileName, backupFile)
	os.remove(fileName)

##############################################
# verifyMQScript
# verify MQ Script
##############################################
def verifyMQScript(mqScript):	
	logInfo("verifying MQ script %s " % mqScript, mqDriverLogger)
	scriptToRun = "runmqsc -v " + h2hprops.get(KYPARAM_QUEUE_MANAGER) + " < " + h2hprops.get(KYPACKAGE_LOCATION) + File.separator +  mqScript.strip("\"") 
	logDebug("Running -> %s" % scriptToRun, mqDriverLogger)
	(exitstatus, result) = commands.getstatusoutput(scriptToRun)
	logDebug(result, mqDriverLogger)
	logDebug("execution status is %s" % exitstatus, mqDriverLogger)
	if exitstatus > 0:
		logError(result, mqDriverLogger)
		return False
	logDir = h2hprops.get(KYPIUH2HDIR) + File.separator + LOGDIRNAME
	if not os.path.exists(logDir):
		os.makedirs(TMPLOGDIR)
		logDir = TMPLOGDIR
	resultFile = logDir + File.separator + mqScript.strip("\"") + ".result"
	if os.path.exists(resultFile):
		backupFileAndRemove(resultFile)
	resultFileHandle = open(resultFile,"w+")
	resultFileHandle.write(result)
	resultFileHandle.close()
	logInfo("execution results saved in %s" % resultFile, mqDriverLogger)
	if result.find("No commands have a syntax error") == -1:
		logError("*** script %s has syntax errors, review the result file %s!" % (mqScript, resultFile), mqDriverLogger)
		return False
	logInfo("completed MQ Script verifications", mqDriverLogger)
	return True

##############################################
# processMQScript
# process MQ Script
##############################################
def processMQScript(mqScript):
	logInfo("running MQ script %s" % mqScript, mqDriverLogger)
	scriptToRun = "runmqsc " + h2hprops.get(KYPARAM_QUEUE_MANAGER) + " < " + h2hprops.get(KYPACKAGE_LOCATION) + File.separator +  mqScript.strip("\"")
	logDebug("Running -> %s" % scriptToRun, mqDriverLogger)
	(exitstatus, result) = commands.getstatusoutput(scriptToRun)
	logDebug(result, mqDriverLogger)
	logDebug("execution status is %s" % exitstatus, mqDriverLogger)
	if exitstatus > 0:
		logError(result, mqDriverLogger)
		return False
	logDir = h2hprops.get(KYPIUH2HDIR) + File.separator + LOGDIRNAME
	if not os.path.exists(logDir):
		logDir = TMPLOGDIR
	resultFile = logDir + File.separator + mqScript.strip("\"") + ".result"
	if os.path.exists(resultFile):
		backupFileAndRemove(resultFile)
	resultFileHandle = open(resultFile,"w+")
	resultFileHandle.write(result)
	resultFileHandle.close()
	logInfo("execution results saved in %s" % resultFile, mqDriverLogger)
	countNotFoundObjects = result.count("not found")
	countDeleteLines = result.count("DELETE ")
	if result.find("No commands have a syntax error.") == -1:
		logDebug(result, mqDriverLogger)
		processedNumber = 0
	else:	
		processedNumberStr = result.rsplit("No commands have a syntax error.")
		processedNumber = 0
		if processedNumberStr != None and len(processedNumberStr) > 0:
			prcessedNumber = processedNumberStr[1].split(" ")[0]
	logDebug("Not Found statements=%s, Delete statements=%s, Statements not processed=%s" % 
														(str(countNotFoundObjects),str(countDeleteLines),processedNumber), mqDriverLogger)
	if countDeleteLines < countNotFoundObjects or processedNumber > countNotFoundObjects:
		logError("*** MQScript %s ran with errors, check %s" % (mqScript, resultFile), mqDriverLogger)
		return False
	logInfo("completed running MQ script %s" % mqScript, mqDriverLogger)
	return True

def getChannelsDefined():
	channelFilter = " |grep CHANNEL|grep -v DUM"
	channelListScript = "echo \"display channel(" + h2hprops.get(KYPARAM_QENV) + "*) type(sdr) type\" |runmqsc " + h2hprops.get(KYPARAM_QUEUE_MANAGER) + channelFilter 
	logDebug(channelListScript, mqDriverLogger)
	(exitstatus, channels) = commands.getstatusoutput(channelListScript)
	logDebug(channels, mqDriverLogger)
	logDebug("execution status is %s" % exitstatus, mqDriverLogger)
	if exitstatus > 0:
		logError(channels, mqDriverLogger)
		logError("execution status is %s" % exitstatus, mqDriverLogger)
		return None
	else:
		return channels

##############################################
# startChannels
# start sender channels
##############################################
def startChannels():
	logInfo("starting channels", mqDriverLogger)
	channels = getChannelsDefined()
	if channels != None:
		for chl in channels.split():
			if chl.find("CHLTYPE") < 0:
				logInfo("starting channel %s" % chl, mqDriverLogger)
				startChannelScript="echo \"START " + chl + "\" |runmqsc " + h2hprops.get(KYPARAM_QUEUE_MANAGER)
				logDebug(startChannelScript, mqDriverLogger)
				(exitstatus, startResult) = commands.getstatusoutput(startChannelScript)
				logDebug(startResult, mqDriverLogger)
				logDebug("execution status is %s" % exitstatus, mqDriverLogger)		
		logInfo("completed starting channels", mqDriverLogger)
	else:
		logWarn("unable to start channels", mqDriverLogger)
		
##############################################
# channelStatus
# channel status
##############################################
def channelStatus():
	logInfo("obtaining status of SDR channels", mqDriverLogger)
	channelOKStatus = True
	channelRunningCount = 0
	senderChannelCount = 0
	channels = getChannelsDefined()
	if channels != None:
		for chl in channels.split():
			if chl.find("CHLTYPE") < 0:
				senderChannelCount = senderChannelCount + 1
				logInfo("obtaining channel status for %s" % chl, mqDriverLogger)
				channelName = chl.strip().split("(")[1].strip(")")
				chsScript="echo \"display CHSTATUS(" + channelName + ") STATUS\" |runmqsc " + h2hprops.get(KYPARAM_QUEUE_MANAGER)
				logDebug(chsScript, mqDriverLogger)
				(exitstatus, chsResult) = commands.getstatusoutput(chsScript)
				logDebug(chsResult, mqDriverLogger)
				logDebug("execution status is %s" % exitstatus, mqDriverLogger)
				if chsResult != None and chsResult.find("Channel Status not found") != -1:
					logError("*** Channel %s not running" % chl, mqDriverLogger)
					channelOKStatus = False
				if exitstatus == 0:
					for chs in chsResult.split("\n"):
						if chs.find(CHANNELSTATUSTAG) > -1:
							for word in chs.split():
								if word.find(CHANNELSTATUSTAG) > -1:
									for itm in word.split():
										if itm.find("CHSTATUS") < 0:
											if itm.find(CHANNELSTATUSTAG) > -1:
												currState = itm.split("(")[1].split(")")[0]
												logInfo("Current state of channel %s is %s" % (chl, currState), mqDriverLogger)
												if currState != "RUNNING":
													logError("*** Channel %s is not running ***" % chl, mqDriverLogger)
													channelOKStatus = False
												else:
													logInfo("channel %s is running" % chl, mqDriverLogger)
													channelRunningCount = channelRunningCount + 1	      
				else:
					channelOKStatus = False
		logInfo("completed checking channel status", mqDriverLogger)
		h2hprops[KYSENDERCHANNELS_COUNT] = str(senderChannelCount)
		h2hprops[KYCHANNELRUNNING_COUNT] = str(channelRunningCount)
	else:
		logWarn("unable to get channel status", mqDriverLogger)
		channelOKStatus = False
	h2hprops[KYCHSTATUS] = channelOKStatus
	return channelOKStatus

##############################################
# stopChannels
# stop channels
##############################################
def stopChannels():
	logInfo("stopping channels", mqDriverLogger)
	channels = getChannelsDefined()
	for chl in channels.split():
		if chl.find("CHLTYPE") < 0:
			logInfo("stopping channel %s" % chl, mqDriverLogger)
			stopChannelScript="echo \"STOP " + chl + "\" |runmqsc " + h2hprops.get(KYPARAM_QUEUE_MANAGER) 
			logDebug(stopChannelScript, mqDriverLogger)
			(exitstatus, stopResult) = commands.getstatusoutput(startChannelScript)
			logDebug(stopResult, mqDriverLogger)
			logDebug("execution status is %s" % exitstatus, mqDriverLogger)
		
	logInfo("completed stopping channels", mqDriverLogger)

##############################################
# senderChannelCheck
# sender channel check
##############################################
def senderChannelCheck(mqScriptFile):
	data = open(mqScriptFile).read()
	if data.find("SDR") > -1:
		return True
	return False

def getAllChannels():
	channelFilter = " |grep CHANNEL|grep -v DUM|grep " + h2hprops.get(KYPARAM_QENV)
	channelListScript = "echo \"display channel(*) type\" |runmqsc " + h2hprops.get(KYPARAM_QUEUE_MANAGER) + channelFilter 
	logDebug(channelListScript, mqDriverLogger)
	(exitstatus, channels) = commands.getstatusoutput(channelListScript)
	logDebug(channels, mqDriverLogger)
	logDebug("execution status is %s" % exitstatus, mqDriverLogger)
	if exitstatus > 0:
		logError(channels, mqDriverLogger)
		logError("execution status is %s" % exitstatus, mqDriverLogger)
		return None
	else:
		return channels


def getChannelType(channelName, channels):
	for channel in channels.split("\n"):
		if channel.find(channelName) > -1:
			return channel.split()[1]

def getSecurityExitsStatus():
	channelsWithSecExits = {}
	securityExitsAvailable = False
	filter = "AMQ8414: Display Channel details."
	channelListScript = "echo \"display channel(*) type scyexit scydata\" |runmqsc " + h2hprops.get(KYPARAM_QUEUE_MANAGER) 
	logDebug(channelListScript, mqDriverLogger)
	(exitstatus, channels) = commands.getstatusoutput(channelListScript)
	logDebug(channels, mqDriverLogger)
	logDebug("execution status is %s" % exitstatus, mqDriverLogger)
	if exitstatus > 0:
		logError(channels, mqDriverLogger)
		logError("execution status is %s" % exitstatus, mqDriverLogger)
		return "Error in obtaining security exits details"
	else:		
		for line in channels.split(filter):
			if line.find("CHANNEL") > -1 and line.find("SYSTEM.") < 0 and line.find("DISPLAY") < 0 and line.find("DUM") < 0:
				if line.find("SCYEXIT( )") < 0 and line.find("SCYDATA( )") < 0:
					h2hprops[KYCURRSCYEXITS] = channels.split(filter)
					securityExitsAvailable = True			
	if not securityExitsAvailable:
		logInfo("No security exits defined", mqDriverLogger)		
	return securityExitsAvailable

def listSecurityExitsStatus():
	found = False
	if isPropertyAvailable(h2hprops.get(KYCURRSCYEXITS)):
		logInfo("---- Listing SCYEXIT and SCYDATA on the channels ----", mqDriverLogger)
		for line in h2hprops.get(KYCURRSCYEXITS):
			if line.find("CHANNEL") > -1 and line.find("SYSTEM.") < 0 and line.find("DISPLAY") < 0 and line.find("DUM") < 0:
				if line.find("SCYEXIT( )") < 0 and line.find("SCYDATA( )") < 0:
					chParts = line.split()
					logInfo("%s %s %s %s" % (chParts[0], chParts[1], chParts[2], chParts[3]), mqDriverLogger)
					found = True
					
	if not found:
		logInfo("No security exits defined, see deployment precheck summary for status", mqDriverLogger)		

def applySecurityExits():
	if not (isPropertyAvailable(h2hprops.get(KYSCYDATA)) and isPropertyAvailable(h2hprops.get(KYSCYEXIT))):
		return

	listSecurityExitsStatus()
	logInfo("do you like to apply security exits to channels (y|Y|n|N):", mqDriverLogger)		
	char = getUserAcceptance("yYnN")
	if char in "nN":
		return
	elif char in "yY":
		channelsList = getAllChannels()
		if not os.path.exists(SECTOKENDIR):
			os.makedirs(SECTOKENDIR)
		for scyData in h2hprops.get(KYSCYDATA).split(","):
			channel = scyData.split(":")[0].strip("\'").strip("\"")
			tokenName = scyData.split(":")[1].strip("\'").strip("\"")
			tokenData = scyData.split(":")[2].strip("\'").strip("\"")
			tokenFile = SECTOKENDIR + File.separator + tokenName
			if not os.path.exists(tokenFile):
				tf = open(tokenFile,"a")
				for line in tokenData.split("\\n"):
					tf.write(line+"\n")
				tf.close()			
			if channelsList == None or channelsList.strip() == "" or channel not in channelsList:
				logError("%s not available, security exit not applied" % channel, mqDriverLogger)
			else:			
				ctype = getChannelType(channel, channelsList)
				logInfo("applying security exit SCYEXIT(%s), SCYDATA(%s) on %s" % (h2hprops.get(KYSCYEXIT), tokenFile, channel), mqDriverLogger)
				cmdToRun = " echo \"alter channel(" + channel + ") " + ctype + " SCYEXIT(\'" + h2hprops.get(KYSCYEXIT) + "\') SCYDATA(\'"+ tokenFile + "\') \" |runmqsc "  + h2hprops.get(KYPARAM_QUEUE_MANAGER) 
				logDebug("Running %s " % cmdToRun, mqDriverLogger)
				(exitstatus, result) = commands.getstatusoutput(cmdToRun)
				logDebug("result of applying exits : "+result, mqDriverLogger)
				logDebug("execution status is %s" % exitstatus, mqDriverLogger)
				if exitstatus > 0:
					logError("error in applying security exits\n %s" % result, mqDriverLogger)
					logWarn("*** continuing deployment, apply security exits manually or rerun after fixing the issues ***", mqDriverLogger)
					
##############################################
# deployMQ
# deploy MQ
##############################################
def deployMQ():
	mqScriptFiles = h2hprops[KYMQSCSCRIPTS].split(",")
	allScriptsRanFine=True
	for mqScript in sorted(mqScriptFiles):
		if verifyMQScript(mqScript):
			releaseDir = h2hprops.get(KYTARGETDIRPATTERN) + File.separator + h2hprops.get(KYTARGETRELEASEDIR) + File.separator + h2hprops.get(KYCCI_VERSION) 
			if not os.path.exists(releaseDir):
				os.makedirs(releaseDir)
			srcFile = h2hprops.get(KYPACKAGE_LOCATION) + File.separator + mqScript.strip("\"")
			dstFile = releaseDir + File.separator + mqScript.strip("\"")
			copyfile(srcFile, dstFile)			
			if not processMQScript(mqScript):
					allScriptsRanFine = False
		else:
			logError("Error in processing MQ script %s " % mqScript, mqDriverLogger)
			sys.exit(1)
	applySecurityExits()
	if allScriptsRanFine and not channelStatus(): # and senderChannelsDefined:
		logInfo("starting channels...", mqDriverLogger)
		startChannels()
