###########################################################################################
# PIULogger.py
# create logger for classes
#
#	Mahesh Devendran, WebSphere Support, PIU Team
#	Copyright(c) 2010, Euroclear 
############################################################################################

from org.apache.log4j import *
import sys
from java.util import Properties

log4JPropertiesFile = None

##############################################
# initLogger
# initialize logger
##############################################
def initLogger(prefix, project, debug):
	log4JPropertiesFile = "properties" + File.separator + "log4j.properties"
	if not os.path.exists(log4JPropertiesFile):	
		print "******* log4J properties file %s not available *******" % log4JPropertiesFile 		
		sys.exit(1)
	propertyFile = open(log4JPropertiesFile, "r")	
	props = Properties()
	props.load(propertyFile)
	propertyFile.close()	
	if debug:
		props.setProperty("log4j.rootCategory", "DEBUG, console, file")
	logFileName = LOGDIRNAME + File.separator + prefix + "_" + project + "_" + h2hprops.get(KYUNIQUEPACKAGEID) + ".log"
	props.setProperty("log4j.appender.file.File", logFileName)		
	PropertyConfigurator.configure(props)

##############################################
# getLogger
# get logger for the class
##############################################
def getLogger(className):	
	return Logger.getLogger(className)

##############################################
# logError
# log error message
##############################################
def logError(mesg, logger = getLogger("Logger.py")):
	logger.error(mesg)
	
##############################################
# logWarn
# log warnning message
##############################################
def logWarn(mesg, logger = getLogger("Logger.py")):
	logger.warn(mesg)

##############################################
# logInfo
# log info message
##############################################
def logInfo(mesg, logger = getLogger("Logger.py")):
	if mesg != None and mesg != "":
		logger.info(mesg)
	
##############################################
# logDebug
# log debug message
##############################################
def logDebug(mesg, logger = getLogger("Logger.py")):
	logger.debug(mesg)


	
