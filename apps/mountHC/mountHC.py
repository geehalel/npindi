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

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction

from indi.INDI import *
from indi.client.qt.indicommon import *
from indi.client.qt.drivermanager import DriverManager
from indi.client.qt.guimanager import GUIManager
from indi.client.qt.indilistener import INDIListener
from indi.client.qt.indistd import *
from indi.client.qt.inditelescope import Telescope

from ui_mountHC import *
# still have to wait for every props to be defined there: for can and has* functions
# not simple at all to explicitely wait for their associated props. So wait a while..
from PyQt5.QtCore import QTimer

class MainWindow(QMainWindow):
    _connection_delay = 1000
    _polling_delay = 1000
    def __init__(self):
        super().__init__()
        self.scope = None
        self.connectiontimer = QTimer()
        self.connectiontimer.setSingleShot(True)
        self.connectiontimer.setInterval(MainWindow._connection_delay)
        self.pollingtimer = QTimer()
        self.pollingtimer.setSingleShot(False)
        self.pollingtimer.setInterval(MainWindow._polling_delay)
        self.initUI()
    def initUI(self):
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
            statusTip="Exit the application", triggered=self.quit)
        self.aboutAct = QAction("&About", self,
                    statusTip="Show the application's About box",
                    triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                    statusTip="Show the Qt library's About box",
                    triggered=QApplication.instance().aboutQt)
        self.testMenu = self.menuBar().addMenu("&Settings")
        self.testMenu.addAction(self.exitAct)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)
        self.HC = mountHC(self)
        #self.centralFrame.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        #self.centralSpacer = QSpacerItem(self.width(), self.height(), QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(self.HC)
        #self.centrallayout.addStretch(1)
        #self.centrallayout.addSpacerItem(self.centralSpacer)
        self.gdi = None
        self.connectiontimer.timeout.connect(self.addTelescope)
        INDIListener.Instance().newTelescope.connect(self.addTimedTelescope)
        self.pollingtimer.timeout.connect(self.HC.update)
        self.setWindowTitle('Mount Hand Controller Demo')
        self.show()
    def closeEvent(self, event):
        self.quit()
    def quit(self):
        DriverManager.Instance().close()
        GUIManager.Instance().close()
        self.close()
    def about(self):
        QMessageBox.about(self, 'Telescope API Test',
                'This <b>API</b> example demonstrates how to integrate '
                'a Telescope Controller in your Qt application.')
    @QtCore.pyqtSlot(ISD.GDInterface)
    def addTimedTelescope(self, gdi):
        self.gdi = gdi
        self.connectiontimer.start()
    @QtCore.pyqtSlot()
    def addTelescope(self):
        if self.scope is not None:
            return
        INDIListener.Instance().newTelescope.disconnect(self.addTimedTelescope)
        INDIListener.Instance().deviceRemoved.connect(self.removeTelescope)
        self.scope = self.gdi
        self.HC.setTelescope(self.scope)
        self.pollingtimer.start()
    @QtCore.pyqtSlot(ISD.GDInterface)
    def removeTelescope(self, gdi):
        if self.scope is None:
            return
        if self.scope != gdi:
            return
        INDIListener.Instance().deviceRemoved.disconnect(self.removeTelescope)
        self.pollingtimer.stop()
        self.scope = None
        self.HC.removeTelescope()
        INDIListener.Instance().newTelescope.connect(self.addTimedTelescope)

import sys
app=QApplication(sys.argv)
mainWin=MainWindow()

DriverManager.Instance().show()
ag = DriverManager.Instance().getActionGroups()
for gkey, ggroup in ag.items():
    mainWin.menuBar().addSeparator()
    gmenu = mainWin.menuBar().addMenu(gkey)
    for a in ggroup.actions():
        gmenu.addAction(a)

rc=app.exec_()
sys.exit(rc)
