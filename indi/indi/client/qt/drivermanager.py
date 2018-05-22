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

from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import QFrame, QTreeWidgetItem, QDialog, QVBoxLayout, QActionGroup, QAction
from PyQt5.QtWidgets import QDialogButtonBox, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic

import enum
import time
import inspect
import os

from indi.client.qt.indicommon import *
from indi.client.qt.driverinfo import DriverInfo
from indi.client.qt.clientmanager import ClientManager
from indi.client.qt.guimanager import GUIManager
from indi.client.qt.indilistener import INDIListener

class DriverManagerUI(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        uiFile = os.path.dirname(inspect.getfile(inspect.currentframe()))
        uiFile = os.path.join(uiFile, 'drivermanager.ui')
        self.dm_ui = uic.loadUi(uiFile, baseinstance=self)
        self.localTreeWidget.setSortingEnabled(False)
        self.localTreeWidget.setRootIsDecorated(True)

        self.clientTreeWidget.setSortingEnabled(False)

        self.runningPix = QIcon.fromTheme("system-run")
        self.stopPix    = QIcon.fromTheme("dialog-cancel")
        self.localMode  = QIcon.fromTheme("computer")
        self.serverMode = QIcon.fromTheme("network-server")

        self.connected    = QIcon.fromTheme("network-connect")
        self.disconnected = QIcon.fromTheme("network-disconnect")
    @QtCore.pyqtSlot(QTreeWidgetItem, int)
    def makePortEditable(self, selectedItem, column):
        if column == DriverManager.LocalColumns.LOCAL_PORT_COLUMN:
            selectedItem.setFlags(Qt.ItemIsSelectable |
                                  Qt.ItemIsEditable | Qt.ItemIsEnabled)
        self.localTreeWidget.editItem(selectedItem,
                                DriverManager.LocalColumns.LOCAL_PORT_COLUMN)

class DriverManager(QDialog):
    class LocalColums(enum.Enum):
        LOCAL_NAME_COLUMN = 0
        LOCAL_STATUS_COLUMN = 1
        LOCAL_MODE_COLUMN = 2
        LOCAL_VERSION_COLUMN = 3
        LOCAL_PORT_COLUMN = 4
    class HostColumns(enum.Enum):
        HOST_STATUS_COLUMN = 0
        HOST_NAME_COLUMN = 1
        HOST_PORT_COLUMN = 2
    __instance = None
    def __new__(cls, parent):
        if DriverManager.__instance is None:
            DriverManager.__instance = QDialog.__new__(cls)
        return DriverManager.__instance
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connectionMode = ServerMode.SERVER_CLIENT
        self.lastGroup = None
        self.driverSource = None
        self.driversList = list()
        self.servers = list()
        self.clients = list()
        self.driversStringList = list()
        self.currentPort = 7624 #TODO implement Options
        self.mainLayout = QVBoxLayout()
        self.ui = DriverManagerUI(self)
        self.mainLayout.addWidget(self.ui)
        self.setLayout(self.mainLayout)
        self.setWindowTitle('PyQt Device Manager')

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.mainLayout.addWidget(self.buttonBox)

        self.buttonBox.rejected.connect(self.close)
        self.ui.addB.clicked.connect(self.addINDIHost)
        self.ui.modifyB.clicked.connect(self.modifyINDIHost)
        self.ui.removeB.clicked.connect(self.removeINDIHost)
        self.ui.connectHostB.clicked.connect(self.activateHostConnection)
        self.ui.disconnectHostB.clicked.connect(self.activateHostDisconnection)
        self.ui.runServiceB.clicked.connect(self.activateRunService)
        self.ui.stopServiceB.clicked.connect(self.activateStopService)
        self.ui.localTreeWidget.itemClicked.connect(self.updateLocalTab)
        self.ui.clientTreeWidget.itemClicked.connect(self.updateClientTab)
        self.ui.localTreeWidget.expanded.connect(self.resizeDeviceColumn)

        # indi client options
        self.options = QDialog(parent=self)
        uiOptions = ui_Options(self.options)
        self.options.adjustSize()
        # action groups
        self.actionGroups = dict()
        self.ag_indi = QActionGroup(self)
        self.optionsAct = QAction('Options', self, statusTip='Set INDI Client options', triggered=self.toggleOptions)
        self.toggleDMAct = QAction('Driver Manager', self, statusTip='Show/hide Driver Manager', triggered=self.toggleDM)
        self.toggleCPAct = QAction('Control Panel', self, statusTip='Show/hide control panel', triggered=lambda _: GUIManager.Instance().updateStatus(True))
        self.ag_indi.addAction(self.optionsAct)
        self.ag_indi.addAction(self.toggleDMAct)
        self.ag_indi.addAction(self.toggleCPAct)
        self.actionGroups['INDI'] = self.ag_indi

        # Local server not implemented yet
        self.ui.ConfTabWidget.setTabEnabled(0, False)
        #For testing purpose
        hostItem=DriverInfo('localhost')
        hostItem.setHostParameters('localhost', '7624')
        hostItem.setDriverSource(DriverSource.HOST_SOURCE)
        hostItem.deviceStateChanged.connect(self.processDeviceStatus)
        self.driversList.append(hostItem)
        item = QTreeWidgetItem(self.ui.clientTreeWidget)
        item.setIcon(self.HostColumns.HOST_STATUS_COLUMN.value,
            self.ui.disconnected)
        item.setText(self.HostColumns.HOST_NAME_COLUMN.value,
            'localhost')
        item.setText(self.HostColumns.HOST_PORT_COLUMN.value,
            '7624')
        # end testing item
    @classmethod
    def Instance(cls):
        if DriverManager.__instance is None:
            DriverManager.__instance = DriverManager(parent=None)
        return DriverManager.__instance
    def getActionGroups(self):
        return self.actionGroups
    def toggleDM(self):
        if self.isVisible() : #and self.isActiveWindow():
            self.hide()
        else:
            self.raise_()
            self.activateWindow()
            self.showNormal()
    def toggleOptions(self):
        if self.options.isVisible() : #and self.isActiveWindow():
            self.options.hide()
        else:
            self.options.raise_()
            self.options.activateWindow()
            self.options.showNormal()
    def addINDIHost(self):
        hostConfDialog = QDialog()
        uiFile = os.path.dirname(inspect.getfile(inspect.currentframe()))
        uiFile = os.path.join(uiFile, 'indihostconf.ui')
        hostConf = uic.loadUi(uiFile, baseinstance=hostConfDialog)
        hostConfDialog.setWindowTitle('Add Host')
        portOk = False
        if hostConfDialog.exec_() == QDialog.Accepted:
            hostItem = DriverInfo(str(hostConf.nameIN.text()))
            try:
                port = int(hostConf.portnumber.text())
            except:
                ret = QMessageBox.critical(hostConfDialog, 'Error',\
                    'Error: the port number is invalid')
                return
            hostItem.setHostParameters(hostConf.hostname.text(), \
                hostConf.portnumber.text())
            for host in self.driversList:
                if hostItem.getName() == host.getName() and \
                    hostItem.getPort() == host.getPort():
                    ret = QMessageBox.critical(hostConfDialog, 'Error',\
                        'Host: {:s} Port: {:s} already exists'.format(\
                            hostItem.getName(), hostItem.getPort()))
                    return
            hostItem.setDriverSource(DriverSource.HOST_SOURCE)
            hostItem.deviceStateChanged.connect(self.processDeviceStatus)
            self.driversList.append(hostItem)
            item = QTreeWidgetItem(self.ui.clientTreeWidget)
            item.setIcon(self.HostColumns.HOST_STATUS_COLUMN.value,
                self.ui.disconnected)
            item.setText(self.HostColumns.HOST_NAME_COLUMN.value,
                hostConf.nameIN.text())
            item.setText(self.HostColumns.HOST_PORT_COLUMN.value,
                hostConf.portnumber.text())
        self.saveHosts()
        #print('Driver Manager: addIndiHost')
    def modifyINDIHost(self):
        hostConfDialog = QDialog()
        uiFile = os.path.dirname(inspect.getfile(inspect.currentframe()))
        uiFile = os.path.join(uiFile, 'indihostconf.ui')
        hostConf = uic.loadUi(uiFile, baseinstance=hostConfDialog)
        hostConfDialog.setWindowTitle('Modify Host')
        currentItem=self.ui.clientTreeWidget.currentItem()
        if currentItem is None: return
        for host in self.driversList:
            if currentItem.text(self.HostColumns.HOST_NAME_COLUMN.value) == host.getName() and \
                currentItem.text(self.HostColumns.HOST_PORT_COLUMN.value) == host.getPort():
                hostConf.nameIN.setText(host.getName())
                hostConf.hostname.setText(host.getHost())
                hostConf.portnumber.setText(host.getPort())
                if hostConfDialog.exec_() == QDialog.Accepted:
                    host.setName(hostConf.nameIN.text())
                    host.setHostParameters(hostConf.hostname.text(),\
                     hostConf.portnumber.text())
                    currentItem.setText(self.HostColumns.HOST_NAME_COLUMN.value,
                        hostConf.nameIN.text())
                    currentItem.setText(self.HostColumns.HOST_PORT_COLUMN.value,
                        hostConf.portnumber.text())
                    self.saveHosts()
                    return
        #print('Driver Manager: modifyIndiHost')
    def removeINDIHost(self):
        currentItem=self.ui.clientTreeWidget.currentItem()
        if currentItem is None: return
        for host in self.driversList:
            if currentItem.text(self.HostColumns.HOST_NAME_COLUMN.value) == host.getName() and \
                currentItem.text(self.HostColumns.HOST_PORT_COLUMN.value) == host.getPort():
                if host.getClientState():
                    ret = QMessageBox.critical(self, 'Error',\
                        'You need to disconnect the client before removing it')
                    return
                ret=QMessageBox.warning(self, 'Delete Confirmation',
                  'Are you sure you want to remove {:s} client?'.format(
                    self.ui.clientTreeWidget.currentItem().text(self.HostColumns.HOST_NAME_COLUMN.value)
                  ), QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
                if ret == QMessageBox.Save:
                    self.driversList.remove(host)
                    del(host)
                    # CHECK a simple delete of the item in c++ removes from tree?
                    currentIndex=self.ui.clientTreeWidget.indexOfTopLevelItem(currentItem)
                    self.ui.clientTreeWidget.takeTopLevelItem(currentIndex)
                    del(currentItem)
                    break
        self.saveHosts()
        #print('Driver Manager: removeIndiHost')
    def activateHostConnection(self):
        self.processRemoteTree(True)
        #print('Driver Manager: activateHostConnection')
    def activateHostDisconnection(self):
        self.processRemoteTree(False)
        #print('Driver Manager: activateHostDisconnection')
    def activateRunService(self):
        print('Driver Manager: activateRunService')
    def activateStopService(self):
        print('Driver Manager: activateRunService')
    def updateLocalTab(self):
        print('Driver Manager: updateLocalTab')
    def resizeDeviceColumn(self):
        self.ui.localTreeWidget.resizeColumnToContents(0)
        #print('Driver Manager: resizeDeviceColumn')
    def updateMenuActions(self):
        pass
    def processLocalTree(self,dState):
        pass
    def processClientTermination(self,client):
        pass
    def processServerTermination(self, server):
        pass
    def processRemoteTree(self, dState):
        currentItem=self.ui.clientTreeWidget.currentItem()
        if currentItem is None: return
        for dv in self.driversList:
            if dv.getDriverSource() != DriverSource.HOST_SOURCE:
                continue
            if currentItem.text(self.HostColumns.HOST_NAME_COLUMN.value) == dv.getName() and \
                currentItem.text(self.HostColumns.HOST_PORT_COLUMN.value) == dv.getPort():
                if dv.getClientState() == dState:
                    return
                if dState:
                    self.connectRemoteHost(dv)
                else:
                    self.disconnectRemoteHost(dv)
    def connectRemoteHost(self, dv):
        try:
            port = int(dv.getPort())
        except:
            ret = QMessageBox.critical(self, 'Error',\
                'Invalid host port {!d}'.format(dv.getPort()))
            return False
        clientManager = ClientManager()
        clientManager.appendManagedDriver(dv)
        clientManager.connectionFailure.connect(self.processClientTermination)
        clientManager.setServer(dv.getHost().encode('latin-1', 'ignore'), port)
        GUIManager.Instance().addClient(clientManager)
        INDIListener.Instance().addClient(clientManager)
        for i in range(INDI_MAX_TRIES):
            connectionToServer = clientManager.connectServer()
            if connectionToServer:
                break
            time.sleep(0.1)
        if connectionToServer:
            self.clients.append(clientManager)
            self.updateMenuActions()
        else:
            GUIManager.Instance().removeClient(clientManager)
            INDIListener.Instance().removeClient(clientManager)
            msgBox=QMessageBox(self)
            msgBox.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setWindowTitle('Error')
            msgBox.setText('Connection to INDI server at host {:s} with port {:s} failed.'.format(dv.getHost(), dv.getPort()))
            msgBox.setModal(False)
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.show()
            self.processDeviceStatus(dv)
            return False
        return True
    def disconnectRemoteHost(self, dv):
        clientManager = dv.getClientManager()
        if clientManager is not None:
            clientManager.removeManagedDriver(dv)
            clientManager.disconnectServer()
            GUIManager.Instance().removeClient(clientManager)
            INDIListener.Instance().removeClient(clientManager)
            self.clients.remove(clientManager)
            del(clientManager)
            self.updateMenuActions()
            return True
        return False
    def updateClientTab(self):
        item = self.ui.clientTreeWidget.currentItem()
        if not item:
            return
        hostname = item.text(self.HostColumns.HOST_NAME_COLUMN.value)
        hostport = item.text(self.HostColumns.HOST_PORT_COLUMN.value)
        for dv in self.driversList:
            if hostname == dv.getName() and hostport == dv.getPort():
                self.processDeviceStatus(dv)
                break
    def saveHosts(self):
        pass
    @QtCore.pyqtSlot(DriverInfo)
    def processDeviceStatus(self, dv):
        if not dv: return
        if dv.getDriverSource() == DriverSource.GENERATED_SOURCE: return
        if dv.getDriverSource() != DriverSource.HOST_SOURCE:
            return
        else:
            for item in self.ui.clientTreeWidget.findItems(dv.getName(), QtCore.Qt.MatchExactly, self.HostColumns.HOST_NAME_COLUMN.value):
                if dv.getClientState():
                    item.setIcon(self.HostColumns.HOST_STATUS_COLUMN.value, self.ui.connected)
                    self.ui.connectHostB.setEnabled(False)
                    self.ui.disconnectHostB.setEnabled(True)
                else:
                    item.setIcon(self.HostColumns.HOST_STATUS_COLUMN.value, self.ui.disconnected)
                    self.ui.connectHostB.setEnabled(True)
                    self.ui.disconnectHostB.setEnabled(False)
if __name__ == '__main__':
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QWidget, QPushButton, QApplication

    class TestWidget(QWidget):
        def __init__(self):
            super().__init__()
            self.initUI()
        def initUI(self):
            qbtn = QPushButton('Quit', self)
            qbtn.clicked.connect(self.quit)
            qbtn.resize(qbtn.sizeHint())
            #qbtn.move(50, 50)

            #self.setGeometry(300, 300, 250, 150)
            self.setWindowTitle('Test DriverManager')
            self.show()
        def quit(self):
            self.close()
            QApplication.instance().quit()

    import sys
    app=QApplication(sys.argv)
    test_widget=TestWidget()

    #dm_ui=DriverManagerUI()
    #dm_ui.show()
    dm=DriverManager(test_widget)
    dm.show()
    rc=app.exec_()
    #dm_ui.hide()
    dm.hide()
    sys.exit(rc)
