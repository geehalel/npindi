from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import QTextEdit, QTabWidget, QSplitter, QDialog
from indi.indibase.basedevice import BaseDevice
from indi.client.qt.indicommon import *
from indi.client.qt.indigroup import INDI_G
from indi.INDI import *

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
    def removeWidgets(self):
        self.groupContainer.deleteLater()
        self.msgST_w.deleteLater()
        self.deviceVBox.deleteLater()
        self.deleteLater()
    def getDeviceBox(self):
        return self.deviceVBox
    def getClientManager(self):
        return self.clientManager
    def getBaseDevice(self):
        return self.dv
    def getGroups(self):
        return self.groupsList
    @QtCore.pyqtSlot(IVectorProperty)
    def buildProperty(self, prop):
        groupName = prop.getGroupName()
        if prop.getDeviceName() != self.dv.getDeviceName():
            return False
        pg = self.getGroup(groupName)
        if pg is None:
            pg = INDI_G(self, groupName)
            self.groupsList.append(pg)
            self.groupContainer.addTab(pg.getScrollArea(), groupName)
        return pg.addProperty(prop)
    @QtCore.pyqtSlot(IVectorProperty)
    def removeProperty(self, prop):
        if prop is None: return False
        groupName = prop.getGroupName()
        if prop.getDeviceName() != self.dv.getDeviceName():
            return False
        pg =self.getGroup(groupName)
        if pg is None:
            return False
        removeResult = pg.removeProperty(prop.getName())
        if pg.size() == 0 and removeResult:
            self.groupContainer.removeTab(self.groupsList.index(pg))
            pg.removeWidgets()
            self.groupsList.remove(pg)
            del(pg)
        return removeResult
    @QtCore.pyqtSlot(IVectorProperty)
    def updateSwitchGUI(self, svp):
        guiProp = None
        propName = svp.name
        if svp.device.getDeviceName() != self.dv.getDeviceName():
            return False
        for pg in self.groupsList:
            guiProp = pg.getProperty(propName)
            if guiProp is not None:
                break
        if guiProp  is None:
            return False
        guiProp.updateStateLED()
        if guiProp.getGUIType() == PGui.PG_MENU:
            guiProp.updateMenuGUI()
        else:
            for lp in guiProp.getElements():
                lp.syncSwitch()
        return True
    @QtCore.pyqtSlot(IVectorProperty)
    def updateTextGUI(self, tvp):
        guiProp = None
        propName = tvp.name
        if tvp.device.getDeviceName() != self.dv.getDeviceName():
            return False
        for pg in self.groupsList:
            guiProp = pg.getProperty(propName)
            if guiProp is not None:
                break
        if guiProp  is None:
            return False
        guiProp.updateStateLED()
        for lp in guiProp.getElements():
            lp.syncText()
        return True
    @QtCore.pyqtSlot(IVectorProperty)
    def updateNumberGUI(self, nvp):
        guiProp = None
        propName = nvp.name
        if nvp.device.getDeviceName() != self.dv.getDeviceName():
            return False
        for pg in self.groupsList:
            guiProp = pg.getProperty(propName)
            if guiProp is not None:
                break
        if guiProp  is None:
            return False
        guiProp.updateStateLED()
        for lp in guiProp.getElements():
            lp.syncNumber()
        return True
    @QtCore.pyqtSlot(IVectorProperty)
    def updateLightGUI(self, lvp):
        pass
    @QtCore.pyqtSlot(IVectorProperty)
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
        for pg in self.groupsList:
            if pg.getName() == groupName:
                return pg
        return None
    def clearMessageLog(self):
        self.msgST_w.clear()
