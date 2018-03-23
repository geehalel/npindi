from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QMainWindow, QMessageBox, QAction, QGroupBox, QVBoxLayout, QTextEdit
from indi.client.qt.indicommon import *
from indi.client.qt.drivermanager import DriverManager
from indi.client.qt.indilistener import INDIListener
from indi.client.qt.indistd import *
from indi.client.qt.inditelescope import Telescope

# used for inspection in APIHandler
import inspect
class APIHandler(QtCore.QObject):
    def __init__(self, gd_device):
        super().__init__()
        self.gd_device = gd_device
        QLoggingCategory.qCDebug(QLoggingCategory.NPINDI,' API handler; new device '+ self.gd_device.getDeviceName())
        self.ui = None
    def buildUI(self):
        self.ui = QGroupBox(self.gd_device.getDeviceName())
        self.layout = QVBoxLayout(self.ui)
        self.logs = QTextEdit(self.ui)
        self.logs.setReadOnly(True)
        self.layout.addWidget(self.logs)
        for m in inspect.getmembers(self.gd_device, inspect.ismethod):
            self.logs.append('method '+m[0] + '--' + m[1].__qualname__ + ' -- sig: ' + str(inspect.signature(m[1])))
        return self.ui

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.apihandlers = list()
        self.initUI()
    def initUI(self):
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
            statusTip="Exit the application", triggered=self.close)
        self.aboutAct = QAction("&About", self,
                    statusTip="Show the application's About box",
                    triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                    statusTip="Show the Qt library's About box",
                    triggered=QApplication.instance().aboutQt)
        self.testMenu = self.menuBar().addMenu("&My Empty Menu")
        self.testMenu.addAction(self.exitAct)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)
        self.centralFrame = QFrame()
        self.setCentralWidget(self.centralFrame)
        self.centrallayout = QVBoxLayout(self.centralFrame)
        INDIListener.Instance().newTelescope.connect(self.addAPIHandler)

        self.setWindowTitle('Test PyQt INDI API')
        self.show()

    def about(self):
        QMessageBox.about(self, 'API Test',
                'This <b>API</b> example demonstrates how to integrate '
                'PyQt INDI API in your Qt application. ')
    @QtCore.pyqtSlot(ISD.GDInterface)
    def addAPIHandler(self, gdi):
        apih = APIHandler(gdi)
        apihui = apih.buildUI()
        self.centrallayout.addWidget(apihui)
        self.apihandlers.append(apih)

# No logging category in PyQt5 and debug output is disabled
# thus install a message handler and filter our category
# you need to launch this test with this command
# QT_LOGGING_RULES="*.debug=true" python3 testdm.py
# to pass over the /usr/share/qt5/qtlogging.ini rules
def qt_message_handler(mode, context, message):
    if not message.startswith('npindi'): return
    if mode == QtCore.QtInfoMsg:
        mode = 'INFO'
    elif mode == QtCore.QtWarningMsg:
        mode = 'WARNING'
    elif mode == QtCore.QtCriticalMsg:
        mode = 'CRITICAL'
    elif mode == QtCore.QtFatalMsg:
        mode = 'FATAL'
    else:
        mode = 'DEBUG'
    #print('qt_message_handler: line: %d, func: %s(), file: %s' % (
    #      context.line, context.function, context.file))
    print('[%s] %s' % (mode, message))

QtCore.qInstallMessageHandler(qt_message_handler)

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
