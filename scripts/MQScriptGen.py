###########################################################################################
#	MQScriptGen.py
#	Generate MQ script from checklist, logic retained from EMX basic version. 
# Uses xlrd third party package to retrieve data from excel
#
#	Mahesh Devendran, WebSphere Support, PIU Team
#	Copyright(c) 2010, Euroclear 
############################################################################################

from org.apache.log4j import *

from datetime import date
import re
from templates.h2hdeploy_templates import *
import xlrd
from os.path import *
import os
import time

execfile("scripts" + File.separator + "util.py")
mqScriptGenLogger = Logger.getLogger("MQScriptGen.py")


RXBUILDSORT = re.compile(r'\d+|[a-zA-Z]')

def _safe_val(val, valtype):
    if valtype == XL_CELL_NUMBER:
        return unicode(int(val))
    elif valtype == XL_CELL_BOOLEAN:
        return unicode(bool(val)).lower()
    elif valtype == XL_CELL_ERROR:
        return CELL_ERROR_MSG
    elif valtype == XL_CELL_TEXT:
        if val.lower() == 'none':
            val = ''
        else:
            val = val[:61]
    return unicode(val)

def write_string(sin, fout):
    closeit = False
    if not hasattr(fout, 'write'):
        fout = open(fout, 'wb')
        closeit = True
#    logDebug('Writing string to file: %s.' % fout.name, mqScriptGenLogger)
    try:
        fout.write(sin)
    finally:
        if closeit:
            fout.close()

def multireplacen(text, mapping, start='', end=''):
    logDebug("Performing multiple pattern substitution...", mqScriptGenLogger)
    keys = mapping.keys()
    keys.sort()
    keys.reverse()
    pattern = '|'.join(re.escape('%s%s%s' % (start, key, end)) for key in keys)
    rx = re.compile(pattern)
    i, j = len(start), len(end)
    def callback(match):
        key = match.group(0)
        repl = mapping[key[i:len(key)-j]]
        logDebug("Replacing '%s' with '%s'" % (key, repl), mqScriptGenLogger)
        return repl
    return rx.subn(callback, text)

def rewrite_file(tmpl, mapping, fout=None):
    logDebug('Performing placeholder pattern replacements by rewriting the file: %s' % tmpl, mqScriptGenLogger)
    fout = fout or tmpl
    t = open(tmpl, 'rb')
    s = t.read()
    t.close()
    if '\0' in s:
        logWarn("%s seems to be a binary file. Ignoring it.", tmpl, mqScriptGenLogger)
        return
    s, n = multireplacen(s, mapping)
    if n:
        write_string(s, fout)
        if n ==1:
            logDebug("One placeholder replacement was performed.", mqScriptGenLogger)
        else:
            logDebug("%s placeholder replacements was performed." % n, mqScriptGenLogger)
    else:
        logError("The specified pattern or patterns were not found in file '%s'. It was not rewritten." % tmpl, mqScriptGenLogger)

##############################################
# generateMQScript
# Generate MQ script from excel checklist
##############################################
def generateMQScript(mqchecklist, mqscriptFile):
    logDebug(">>>generateMQScript", mqScriptGenLogger)
    logInfo("Generating MQ script from the excel checklist...", mqScriptGenLogger) 
    fdout = open(mqscriptFile, 'wb')
    logDebug("Retrieving information from the excel checklist...", mqScriptGenLogger)
    book = xlrd.open_workbook(mqchecklist)
    try:
        for sheetname in MQCHKLST_SHEET_NAMES:
            logDebug("Reading worksheet: " + sheetname, mqScriptGenLogger)
            StaticITSATemplate.comment(fdout, MQCOMMENTS[sheetname], width=60, marker='*')
            varmap = MQTEMPLATEVARS[sheetname]
            logDebug(varmap, mqScriptGenLogger)
            sheet = book.sheet_by_name(sheetname)
            logDebug(sheet, mqScriptGenLogger)
            for rowidx in xrange(1, sheet.nrows):
                data = {}
                action = sheet.cell_value(rowidx, MQCHKLST_CMDIDX).lower()
                logDebug(action, mqScriptGenLogger)
                for colidx, var in varmap.iteritems():
                    logDebug(var, mqScriptGenLogger)
                    #val = ""
                    #if var == "persistence":
                    #    if sheet.cell_value(rowidx, colidx) == "P":
                    #        val = "YES"
                    #    elif sheet.cell_value(rowidx, colidx) == "NP":
                    #        val = "NO"
                    #else:
                    val =  sheet.cell_value(rowidx, colidx)
                    logDebug(val, mqScriptGenLogger)
                    valtype =  sheet.cell_type(rowidx, colidx)
                    logDebug(valtype, mqScriptGenLogger)
                    data[var] =_safe_val(val, valtype)
                    logDebug("%s -> %s" % (var, data[var]), mqScriptGenLogger)
#                logDebug("Writing MQ command to file: " + mqscriptFile, mqScriptGenLogger)
                for template in MQCMD[(sheetname, action)]:
                    template.write(fdout, **data)
    finally:
        fdout.close()

    logInfo("Completed generating MQ script from template", mqScriptGenLogger)
    logDebug("Performing placeholders replacements", mqScriptGenLogger)
    varsheet = book.sheet_by_name(MQCHKLST_VARS)
    data = {}
    logDebug("Reading checklist Variables...", mqScriptGenLogger)
    for rowidx in xrange(1, varsheet.nrows):
        key = varsheet.cell_value(rowidx, MQCHKLST_VARSKEYIDX)
        if key == None or key == "":
            logDebug("no more keys in checklist", mqScriptGenLogger)
            break
        val = varsheet.cell_value(rowidx, MQCHKLST_VARSVALIDX)
        logDebug("key '%s' val '%s'" % (key, val), mqScriptGenLogger)
        if key == "<ENVSPTFE>":
            #Check the value of the PARAM_QENV property
            logDebug("h2hprops[KYPARAM_QENV] has value '%s'" % h2hprops[KYPARAM_QENV], mqScriptGenLogger)
            #If the value of the PARAM_QENV property is not equal to the value in the checklist spreadsheet
            if h2hprops[KYPARAM_QENV] != val:
                #Replace the PARAM_QENV with the value from the spreadsheet
                logDebug("Overriding '%s' with value '%s'" % (h2hprops[KYPARAM_QENV], val), mqScriptGenLogger)
        	h2hprops[KYPARAM_QENV] = val
        	#Check the value of the PARAM_QENV property again just for fun
        	logDebug("h2hprops[KYPARAM_QENV] now has value '%s'" % h2hprops[KYPARAM_QENV], mqScriptGenLogger)
        if val == None or val == "":
            logError("Variable value for %s not available from Variables Sheet in the .xls" % key, mqScriptGenLogger)
            sys.exit(1)
        if val:
            logDebug("Variable '%s' has value '%s'" % (key, val), mqScriptGenLogger)
            data[key] = val
    if data:
        rewrite_file(mqscriptFile, data)
    else:
        logDebug("Checklist has no variables defined.", mqScriptGenLogger)
        logDebug("Updates to the MQ script was not performed.", mqScriptGenLogger)
    logDebug("MQScript %s generation process completed" % (mqscriptFile), mqScriptGenLogger)
    logDebug("<<<generateMQScript", mqScriptGenLogger)

##############################################
# processMQCheckLists
# process MQ checklists
##############################################
def processMQCheckLists(requested):
        logDebug(">>>processMQCheckLists", mqScriptGenLogger)
	if not requested:
		return
		
	if not h2hprops.get(KYMQPROPERTYCHECK):
		return 
		
	logInfo("Processing MQ checklist files", mqScriptGenLogger)
	chklistfiles = h2hprops.get(KYMQCHKLISTFILES).split(",")
	chklistdir = h2hprops.get(KYPIUH2HDIR) + File.separator + DATADIR
	logDebug("check list directory is %s" % chklistdir, mqScriptGenLogger)
	h2hprops[KYMQSCSCRIPTS] = None
	mqScriptFiles = None
	#i = 1
	for chklist in chklistfiles:		
		mqchecklist = chklistdir + File.separator + chklist.strip('"')
		if not os.path.exists(mqchecklist):
			logError("Checklist file %s does not exist" % mqchecklist, mqScriptGenLogger)
			sys.exit(1)
			
		logDebug("processing MQ checklist %s" % mqchecklist, mqScriptGenLogger)
		logDebug("chklist %s" % chklist, mqScriptGenLogger)

		#cciVersion = chklist.strip("\"").strip(".xls").split("version")[1].split()[0]
		#logDebug("cciVersion %s" % cciVersion, mqScriptGenLogger)
		fileParts = chklist.strip('\"').strip(".xls")
		logDebug("fileParts %s" % fileParts, mqScriptGenLogger)
		#mqscFileName = cciVersion + "_" + fileParts[len(fileParts) - 1] + ".txt"
		mqscFileName = fileParts + ".txt"
		#i = i + 1
		logDebug("mqscFileName %s" % mqscFileName, mqScriptGenLogger)
		mqscriptFile = "_".join([h2hprops.get(KYOUTPUTDIR) + File.separator + mqscFileName])
		generateMQScript(mqchecklist, mqscriptFile)
		MQSCScripts=h2hprops.get(KYMQSCSCRIPTS)
		if MQSCScripts == None:
			h2hprops[KYMQSCSCRIPTS] = "\""+mqscFileName+"\""
			mqScriptFiles="[[\n\t\t\""+mqscFileName+"\""
		else:
			h2hprops[KYMQSCSCRIPTS] = MQSCScripts + ",\""+mqscFileName+"\""
			mqScriptFiles = mqScriptFiles + ",\n\t\t\""+mqscFileName+"\""
		logDebug(h2hprops.get(KYMQSCSCRIPTS), mqScriptGenLogger)
	h2hprops[KYMQSCSCRIPTS] = mqScriptFiles + "\n\t\t]]" 
        logDebug(">>>processMQCheckLists", mqScriptGenLogger)
