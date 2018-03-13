from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import QTextEdit, QTabWidget, QSplitter, QDialog
from indi.indibase.basedevice import BaseDevice
from indi.client.qt.indicommon import *

class INDI_D(QDialog):
    def __init__(self, in_manager, in_idv, in_cm):
        super().__init__(None)
        self.guiManager = in_manager
        self.dv = in_idv
        self.clientManager = in_cm
        self.deviceVBox = QSplitter()
        self.deviceVBox.setOrientation(QtCore.Qt.Vertical)
        self.groupContainer = QTabWidget()
        self.msgST_w = QTextEdit()
        self.msgST_w.setReadOnly(True)
        self.deviceVBox.addWidget(self.groupContainer)
        self.deviceVBox.addWidget(self.msgST_w)
        self.groupsList = list()
    def getDeviceBox(self):
        return self.deviceVBox
    def getClientManager(self):
        return self.clientManager
    def getBaseDevice(self):
        return self.dv
    def getGroups(self):
        return self.groupsList
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
    @QtCore.pyqtSlot(BaseDevice, int)
    def updateMessageLog(self, idv, messageID):
        if idv != self.dv: return
        message = self.dv.message_queue(messageID)
        formatted = message
        if message[21:23] == '[E':
            formatted = '<span style="color:red">{!s}</span>'.format(message)
        elif message[21:23] == '[W':
            formatted = '<span style="color:orange">{!s}</span>'.format(message)
        elif message[21:23] == '[I':
            QLoggingCategory.qCDebug(QLoggingCategory.NPINDI, idv.getDeviceName()+message[21:])
            return
        self.msgST_w.ensureCursorVisible()
        self.msgST_w.insertHtml(formatted)
        self.msgST_w.insertPlainText('\n')
        c = self.msgST_w.textCursor()
        c.movePosition(Qt.QTextCursor.Start)
        self.msgST_w.setTextCursor(c)
        QLoggingCategory.qCInfo(QLoggingCategory.NPINDI, idv.getDeviceName()+': '+message[21:])

    def getGroup(self, groupName):
        pass
    def clearMessageLog(self):
        pass
