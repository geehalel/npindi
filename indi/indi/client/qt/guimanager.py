# Copyright 2018 geehalel@gmail.com
#
# This file is part of npindi.
#
#    npindi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    npindi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with npindi.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtCore
from PyQt5.QtWidgets import QPushButton, QTabWidget, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtGui import QCloseEvent, QHideEvent, QShowEvent, QIcon

from indi.client.qt.deviceinfo import DeviceInfo
from indi.client.qt.indidevice import INDI_D
from indi.client.qt.indicommon import QLoggingCategory
import time

class GUIManager(QWidget):
    __instance = None
    def __new__(cls, parent):
        if GUIManager.__instance is None:
            GUIManager.__instance = QWidget.__new__(cls)
        return GUIManager.__instance
    def __init__(self, parent):
        if GUIManager.__instance is not None: pass
        super().__init__(parent=parent, flags=QtCore.Qt.Window)
        self.mainLayout = QVBoxLayout(self)
        #self.mainLayout.setMargin(10)
        self.mainLayout.setContentsMargins(10, 10, 10, 10)
        self.mainLayout.setSpacing(10)
        self.mainTabWidget = QTabWidget(self)
        self.mainLayout.addWidget(self.mainTabWidget)
        self.setWindowIcon(QIcon.fromTheme('kstars_indi'))
        self.setWindowTitle('PyQt INDI Control Panel')
        #self.setAttribute(QtCore.Qt.WA_ShowModal, False)
        self.clearB = QPushButton('Clear')
        self.closeB = QPushButton('Close')
        buttonLayout = QHBoxLayout()
        buttonLayout.insertStretch(0, 0)
        buttonLayout.addWidget(self.clearB, 0, QtCore.Qt.AlignRight)
        buttonLayout.addWidget(self.closeB, 0, QtCore.Qt.AlignRight)
        self.mainLayout.addLayout(buttonLayout)
        self.closeB.clicked.connect(self.close)
        self.clearB.clicked.connect(self.clearLog)
        self.clients = list()
        self.guidevices = list()
    @classmethod
    def Instance(cls):
        if GUIManager.__instance is None:
            GUIManager.__instance = GUIManager(parent=None)
        return GUIManager.__instance
    def getDevices(self):
        return self.devices
    def size(self):
        return len(self.guidevices)
    @QtCore.pyqtSlot(QtCore.Qt.ApplicationState)
    def changeAlwaysOnTop(self, state):
        if self.isVisible():
            if state == QtCore.Qt.ApplicationActive:
                self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(self.windowFlags & ~QtCore.Qt.WindowStaysOnTopHint)
            self.show()
    def closeEvent(self, event):
        pass
    def hideEvent(self, event):
        pass
    def showEvent(self, event):
        pass
    def updateStatus(self, toggle_behavior):
        if len(self.guidevices) == 0:
            return
        #if self.isVisible() and self.isActiveWindow() and toggle_behavior:
        if self.isVisible() and toggle_behavior:    
            self.hide()
        else:
            self.raise_()
            self.activateWindow()
            self.showNormal()
    def findGUIDevice(self, deviceName):
        for gdv in self.guidevices:
            if gdv.getBaseDevice().getDeviceName() == deviceName:
                return gdv
        return None
    @QtCore.pyqtSlot()
    def clearLog(self):
        dev = self.findGUIDevice(self.mainTabWidget.tabText(self.mainTabWidget.currentIndex()).replace('&',''))
        #QLoggingCategory.qCDebug(QLoggingCategory.NPINDI, 'clearLog for dev '+str(dev))
        if dev:
            dev.clearMessageLog()
    def addClient(self, cm):
        self.clients.append(cm)
        cm.newINDIDevice.connect(self.buildDevice)
        cm.removeINDIDevice.connect(self.removeDevice)
    def removeClient(self, cm):
        self.clients.remove(cm)
        for gdv in self.guidevices:
            if gdv.getClientManager() == cm:
                for i in range(self.mainTabWidget.count()):
                    if self.mainTabWidget.tabText(i).replace('&','') == gdv.getBaseDevice().getDeviceName():
                        self.mainTabWidget.removeTab(i)
                        break
                self.guidevices.remove(gdv)
                del(gdv)
        if len(self.clients) == 0:
            self.hide()
    @QtCore.pyqtSlot(DeviceInfo)
    def removeDevice(self, di):
        deviceName = di.getBaseDevice().getDeviceName()
        dp = self.findGUIDevice(deviceName)
        if dp is None: return
        cm = di.getDriverInfo().getClientManager()
        if cm:
            cm.disconnect(dp)
        if self.mainTabWidget.count() != len(self.guidevices):
            time.sleep(0.1)
        for i in range(self.mainTabWidget.count()):
            if self.mainTabWidget.tabText(i).replace('&','') == deviceName:
                self.mainTabWidget.removeTab(i)
                break
        dp.removeWidgets()
        self.guidevices.remove(dp)
        del(dp)
        if len(self.guidevices) == 0:
            pass
    @QtCore.pyqtSlot(DeviceInfo)
    def buildDevice(self, di):
        cm = di.getDriverInfo().getClientManager()
        if cm is None:
            Qt.Qcritical('ClientManager is None in build device!')
            return
        gdm = INDI_D( self, di.getBaseDevice(), cm)
        cm.newINDIProperty.connect(gdm.buildProperty)
        cm.removeINDIProperty.connect(gdm.removeProperty)
        cm.newINDISwitch.connect(gdm.updateSwitchGUI)
        cm.newINDIText.connect(gdm.updateTextGUI)
        cm.newINDINumber.connect(gdm.updateNumberGUI)
        cm.newINDILight.connect(gdm.updateLightGUI)
        cm.newINDIBLOB.connect(gdm.updateBLOBGUI)
        cm.newINDIMessage.connect(gdm.updateMessageLog)
        self.mainTabWidget.addTab(gdm.getDeviceBox(), di.getBaseDevice().getDeviceName())
        self.guidevices.append(gdm)
        self.updateStatus(False)
