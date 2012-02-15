from org.apache.log4j import *
import sys

# @TODO have log file name one per environment
# class PIUPropConfigurator extends PropertyConfigurator {
#	static void configPiuLogProperty( String propsFile, String logFileName ) {
#		-- log file name must be changedfor the file appended
#		-- call the original configure method with the new properties.
#	 }
# }
log4JPropertiesFile = None

def initLogger(prefix, debug=False):
	log4JPropertiesFile = "properties" + File.separator + "log4j.properties"
	propertyFile = open(log4JPropertiesFile, "r")
	data = propertyFile.read()
	propertyFile.close()
	log4JPropertiesFile = "properties" + File.separator + prefix + "_" + "log4j.properties"
	propertyFile = open(log4JPropertiesFile, "w")
	if debug:
		replacedData = data.replace(INFO,DEBUG)
		data = replacedData	
	logFileName = prefix + "_" + str(date.today()) + "_" + time.strftime("%H-%M-%S", time.gmtime()) + "_piuh2h.log"
	propertyFile.write(data.replace("piuh2h.log", logFileName))		
	propertyFile.close()
	PropertyConfigurator.configure(log4JPropertiesFile)

def getLogger(className):
#	root = Logger.getRootLogger();
#	if not root.getAllAppenders().hasMoreElements():
#		initLogger(prefix, debug)
		
	return Logger.getLogger(className)

def logError(mesg, logger = getLogger("Logger.py")):
	logger.error(mesg)
	
def logWarn(mesg, logger = getLogger("Logger.py")):
	logger.warn(mesg)

def logInfo(mesg, logger = getLogger("Logger.py")):
	logger.info(mesg)
	
def logDebug(mesg, logger = getLogger("Logger.py")):
	logger.debug(mesg)

def entryMethod(methodName, mesg, logger):
	logInfo("<" + methodName + ": " + mesg, logger)
	
def exitMethod(methodName, mesg, logger):
	logInfo(">" + methodName + ": " + mesg, logger)	

	
