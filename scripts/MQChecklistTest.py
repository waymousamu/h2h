import unittest
from MQChecklist import MQChecklist,RunMQScriptError

class MQCheckListTest(unittest.TestCase):

    def setUp(self):
        self.mqchecklist = MQChecklist()
        self.distloc = None

    def tearDown(self):
        self.mqchecklist = None

    def testMQScriptFileNotAvailable(self):
        """Check that the code to find the MQScript file fails if the file does not exist"""
        self.distloc = "bogus.txt"
        self.assertRaises(IOError, self.mqchecklist.setValidMQScript, self.distloc)

    def testMQScriptAvailable(self):
        """Check that the code to find the MQScript file passes if the file exists"""
        self.distloc = "C:\\H2H_test\\packages\\mp16\\mp16-4.3-2010-08-03_16-52-49-BST_waymouts\\MP16_CCI - version 4.3 - TFE for SP - MQ checklist v00.01.txt"
        self.mqchecklist.setValidMQScript(self.distloc)
        assert self.mqchecklist.isValidMQScript == (True), 'mqScript file does not exist'

    def testMQScriptFails(self):
        """Check that the code to handle MQScript failures works"""
        self.distloc = "C:\\H2H_test\\packages\\mp16\\mp16-4.3-2010-08-03_16-52-49-BST_waymouts\\MP16_CCI - version 4.3 - TFE for SP - MQ checklist v00.01.txt"
        self.mqchecklist.setValidMQScript(self.distloc)
        self.assertRaises(RunMQScriptError, self.mqchecklist.runMQScript, self.distloc)

    def testMQScriptSuceeds(self):
        """Check that the code to handle MQScript sucess works"""
        self.distloc = "C:\\H2H_test\\packages\\mp16\\mp16-4.3-2010-08-03_16-52-49-BST_waymouts\\MP16_CCI - version 4.3 - TFE for SP - MQ checklist v00.01.txt"
        self.mqchecklist.setValidMQScript(self.distloc)
        assert self.mqchecklist.runMQScript(self.distloc) == (0), 'mqScript file does not run'

if __name__ == "__main__":
            unittest.main()

