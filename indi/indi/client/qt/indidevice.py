from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextEdit, QTabWidget, QSplitter, QDialog

from indi.client.qt.clientmanager import ClientManager
try:
    from indi.client.qt.guimanager import GUIManager
except:
    pass

class INDI_D(QDialog):
    def __init__(self, in_manager, in_idv, in_cm):
        super().__init__(None)
        self.guiManager = in_manager
        self.dv = in_idv
        self.clientManager = in_cm
        self.deviceVBox = QSplitter()
        self.deviceBox.setOrientation(Qt.Vertical)
        self.groupContainer = QTabWidget()
        self.msgST_w = QTextEdit()
        self.msgST_w.setReadOnly(True)
        self.deviceVBox.addWidget(self.groupContainer)
        self.deviceBox.addWidget(self.msgST_w)
    def buildProperty(self, prop):
        pass
    def removeProperty(self, prop):
        pass
    def updateSwitchGUI(self, svp):
        pass
    def updateTextGUI(self, tvp):
        pass
    def updateNumberGUI(self, nvp):
        pass
    def updateLightGUI(self, lvp):
        pass
    def updateBLOBGUI(self, bp):
        pass
    def updateMessageLog(self, idv, messageID):
        pass
    def getGroup(self, groupName):
        pass
    def clearMessageLog(self):
        pass
