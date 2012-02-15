import commands
import subprocess
from org.apache.log4j import *

class MQChecklist():
    """MQChecklist: Class used to process MQScripts and MQChecklist spreadsheets."""
    
    def __init__(self, isValidMQScript=False):
        """Constructor: Sets a default value of False for the isValidMQScript instance variable."""
        self.isValidMQScript=isValidMQScript
        self.logger=Logger.getLogger("MQChecklist")
        PropertyConfigurator.configure("C:\\H2H_test\\properties\\log4j.properties")
        self.logger.debug(isValidMQScript)        

    def setValidMQScript(self, mqScriptFile):
        """setValidMQScript(mqScriptFile): Check for the existance of the MQScript file"""
        self.logger.debug("getting the MQScript file " + mqScriptFile)
        try:
            mqsf = open(mqScriptFile)
            self.isValidMQScript = True
            self.logger.debug(self.isValidMQScript)
        except IOError, e:
            self.logger.warn("setValidMQScript(): %s" % (e))
            raise

    def runMQScript(self, mqScriptFile):
        """runMQScript(mqScriptFile): Run the MQScript file"""
        try:
            if (self.isValidMQScript):
                self.logger.debug("Running the command...")
                #(exitstatus, result) = commands.getstatusoutput("cmd")
                exitstatus = subprocess.check_call(["ping.exe", "localhost"])
                self.logger.debug("exitstatus: %s" % (exitstatus))
                self.logger.debug("result: %s" % (result))
                if exitstatus > 0:
                    raise RunMQScriptError(result)
                else:
                    self.logger.debug("result: %s" % (result))
                    return 0
        except RunMQScriptError, e:
            self.logger.error("runMQScript(): %s" % (e))
            raise

class RunMQScriptError(Exception):
    """RunMQScriptError(Exception): MQScript Failed to run"""
    def __init__(self, val):
        self.val = val
    def __str__(self):
        return repr(self.val)

    

    

    



            
