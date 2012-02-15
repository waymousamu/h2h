###########################################################################################
#	CCIBuild.py
#	Script to process CCI build##	Mahesh Devendran, WebSphere Support, PIU Team
#	Copyright(c) 2010, Euroclear 
############################################################################################
from org.apache.log4j import *
import os
import sys 
from os import File
import shutil

execfile("scripts" + File.separator + "util.py")

cciBuildLogger = Logger.getLogger("CCIBuild.py")

def replaceJVALPlaceHolders(jvalSrcFile, jvalDstFile):	
	logDebug("jvalSrcFile is %s" % jvalSrcFile)
	logDebug("jvalDstFile is %s" % jvalDstFile)
	processedData = open(jvalDstFile,"w+")
	jvalSrcFileHandle = open(jvalSrcFile)	
	data = jvalSrcFileHandle.read()	
	var = '#' + KYPARAM_JVAL_PATH + '#'	
	newVar = h2hprops.get(KYTARGETDIRPATTERN) + "/" + h2hprops.get(KYCCIVERSION_SOFTLINK) + "/" + h2hprops.get(KYTARGETJVALDIR)	
	logDebug("replacing variable %s with %s " % (var,newVar))	
	replacedData = data.replace(var, newVar)	
	processedData.write(replacedData)			
	processedData.close()	
	jvalSrcFileHandle.close()	
	os.remove(jvalSrcFile)

def copySODirs(srcDir):
        logDebug(">>>>copySODirs", cciBuildLogger)        
	soDirs = h2hprops.get(KYSODIRS).split(",")
	logDebug("soDirs: %s " % soDirs, cciBuildLogger)
	logDebug("outputdir: %s " % h2hprops.get(KYOUTPUTDIR), cciBuildLogger)
	logDebug("targetsodir: %s " % h2hprops.get(KYTARGETSODIR), cciBuildLogger)
	soDstDir = h2hprops.get(KYOUTPUTDIR) + File.separator + h2hprops.get(KYTARGETSODIR)
	for dir in soDirs:
		soDir = srcDir + File.separator + dir
		if os.path.exists(soDir):
                        logInfo("Copying SO directory %s:" % soDir, cciBuildLogger)
                        if not os.path.exists(soDstDir):
                                logDebug("making destination directory: %s " % soDstDir, cciBuildLogger)
                                os.makedirs(soDstDir)                                
                        logDebug("copying %s files from %s to %s" % (soDir, srcDir,soDstDir), cciBuildLogger)		
                        copyDir(soDir, soDstDir) 
	logDebug("<<<<copySODirs", cciBuildLogger)

def copyConfigDirs(srcDir):
        logDebug(">>>>copyConfigDirs", cciBuildLogger)
	if isPropertyAvailable(h2hprops.get(KYTARGETCONFIGDIR)) and isPropertyAvailable(h2hprops.get(KYCONFIGDIRS)):
		configDirs = h2hprops.get(KYCONFIGDIRS).split(",")		
		configDstDir = h2hprops.get(KYOUTPUTDIR) + File.separator + h2hprops.get(KYTARGETCONFIGDIR)		
		for dir in configDirs:			
			configDir = srcDir + File.separator + dir.strip('"')
			if os.path.exists(configDir):
                                logInfo("Copying CONFIG directory %s:" % configDir, cciBuildLogger)
                                if not os.path.exists(configDstDir):
                                        logDebug("making destination directory: %s " % configDstDir, cciBuildLogger)
                                        os.makedirs(configDstDir)
                                logDebug("copying %s files from %s to %s" % (configDir, srcDir,configDstDir), cciBuildLogger)			
                                copyDir(configDir, configDstDir)
	logDebug("<<<<copyConfigDirs", cciBuildLogger)

def copyMapsDirs(srcDir):
        logDebug(">>>>copyMapsDirs", cciBuildLogger)
	if isPropertyAvailable(h2hprops.get(KYTARGETMAPSDIR)) and isPropertyAvailable(h2hprops.get(KYMAPSDIRS)):		
		mapsDirs = h2hprops.get(KYMAPSDIRS).split(",")		
		mapsDstDir = h2hprops.get(KYOUTPUTDIR) + File.separator + h2hprops.get(KYTARGETMAPSDIR)		
		for dir in mapsDirs:			
			mapsDir = srcDir + File.separator + dir
			if os.path.exists(mapsDir):
                                logInfo("Copying MAPS directory %s:" % mapsDir, cciBuildLogger)
                                if not os.path.exists(mapsDstDir):
                                        logDebug("making destination directory: %s " % mapsDstDir, cciBuildLogger)
                                        os.makedirs(mapsDstDir)
                                logDebug("copying %s from %s to %s" % (mapsDir, srcDir,mapsDstDir), cciBuildLogger)			
                                copyDir(mapsDir, mapsDstDir)
	logDebug("<<<<copyMapsDirs", cciBuildLogger)

def copyJVAL(jvalDir):
        logDebug(">>>>copyJVAL", cciBuildLogger)
	jvalFile = jvalDir + File.separator + JVAL_FILE	
	if os.path.exists(jvalFile):
                jvalDstDir = h2hprops.get(KYOUTPUTDIR) + File.separator + h2hprops.get(KYTARGETJVALDIR)
		jvalDstFile = h2hprops.get(KYOUTPUTDIR) + File.separator + h2hprops.get(KYTARGETJVALDIR) + File.separator + JVAL_FILE
		if not os.path.exists(jvalDstDir):
                        logDebug("making destination directory: %s " % jvalDstDir, cciBuildLogger)
                        os.makedirs(jvalDstDir)
                logInfo("Copying jval.tar from %s" % jvalFile, cciBuildLogger)	
                copyfile(jvalFile, jvalDstFile)				
	logDebug("<<<<copyJVAL", cciBuildLogger)

def copyMomControlScript():
        logDebug(">>>>copyMomControlScript", cciBuildLogger)
        
        logDebug("KYMOMSCRIPTSRC: %s " % h2hprops.get(KYMOMSCRIPTSRC), cciBuildLogger)
        logDebug("KYTARGETSCRIPTSDIR: %s " % h2hprops.get(KYTARGETSCRIPTSDIR), cciBuildLogger)
                 
	if isPropertyAvailable(h2hprops.get(KYMOMSCRIPTSRC)) and os.path.exists(h2hprops.get(KYMOMSCRIPTSRC)) and isPropertyAvailable(h2hprops.get(KYTARGETSCRIPTSDIR)):
                 logDebug("copying %s " % h2hprops.get(KYMOMSCRIPTSRC), cciBuildLogger)
                 dstFile = h2hprops.get(KYOUTPUTDIR) + File.separator + h2hprops.get(KYTARGETSCRIPTSDIR) + File.separator + getFileNameFromURL(h2hprops.get(KYMOMSCRIPTSRC))
                 
                 if os.path.exists(h2hprops.get(KYMOMSCRIPTSRC)):
                         logInfo("Copying MOM Control Scripts.", cciBuildLogger)
                         logDebug("dstFile=%s" % dstFile, cciBuildLogger)
                         copyfile(h2hprops.get(KYMOMSCRIPTSRC), dstFile)
                         
        logDebug("<<<<copyMomControlScript", cciBuildLogger)

def processJVALPropertyFile():
        logDebug(">>>>processJVALPropertyFile", cciBuildLogger)
	jvalPropFile = h2hprops[KYOUTPUTDIR] + File.separator + h2hprops.get(KYTARGETCONFIGDIR) + File.separator + JVAL_PROP_FILE		
	if os.path.exists(jvalPropFile):			
		logInfo("Processing jval.prop.", cciBuildLogger)			
		jvalDstFile = h2hprops[KYOUTPUTDIR] + File.separator + h2hprops.get(KYTARGETMAPSDIR) + File.separator + JVAL_PROP_FILE			
		replaceJVALPlaceHolders(jvalPropFile, jvalDstFile)
	logDebug("<<<<processJVALPropertyFile", cciBuildLogger)

def processJVAL(srcDir):
        logDebug(">>>>processJVAL", cciBuildLogger)
	for item in os.listdir(srcDir):		
		if os.path.isdir(srcDir + File.separator + item) and item == h2hprops.get(KYJVALFOLDER):			
			copyJVAL(srcDir + File.separator + item)
	logDebug("<<<<processJVAL", cciBuildLogger)
				
def processCCIBuild(app):
        logDebug(">>>>processCCIBuild", cciBuildLogger)
	if app == True:
		cciAction = True
	else:
		cciAction = False
		
	if not cciAction:
		return
		
	logInfo("Retrieving build dirs", cciBuildLogger)	
	buildDir = h2hprops.get(KYBUILDLOC)	
	builds = sorted(getVar(h2hprops.get(KYBUILDS)).split(","))			
	
	for build in builds:		
		srcDir = buildDir + File.separator + build.strip()		
		# if directories are mentioned and it is not present, then it is treated as an error.		
		logDebug("processing build dir %s " % srcDir, cciBuildLogger)		
		if os.path.exists(srcDir):			
			if h2hprops.get(KYSOPROPERTYCHECK):				
				copySODirs(srcDir)			
			if h2hprops.get(KYCONFIGPROPERTYCHECK):				
				copyConfigDirs(srcDir)			
			if h2hprops.get(KYMAPSPROPERTYCHECK):				
				copyMapsDirs(srcDir)			
				processJVAL(srcDir)		
			else:			
				logError("Source directory missing :", cciBuildLogger)	
	#copyMomControlScript()	
	processJVALPropertyFile()
	logDebug("<<<<processCCIBuild", cciBuildLogger)					
