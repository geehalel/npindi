from PyQt5 import QtCore
from PyQt5.QtWidgets import QComboBox, QLabel, QApplication, QMainWindow, QMessageBox, QAction, QGroupBox, QVBoxLayout, QTextEdit, QHBoxLayout
#from PyQt5.QtWebEngineWidgets import QWebEngineView

from indi.client.qt.indicommon import *
from indi.client.qt.drivermanager import DriverManager
from indi.client.qt.guimanager import GUIManager
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
        self.uiFrame=QFrame(self.ui)
        self.MHBox = QHBoxLayout(self.uiFrame)
        self.methodMenu = QComboBox(self.ui)
        self.methodMenu.activated.connect(self.runMethod)
        self.labeldevice = QLabel('No device found', self.ui)
        self.labelrun = QLabel('Run ', self.ui)
        self.labelresult = QLabel('', self.ui)
        self.logs = QTextEdit(self.ui)
        self.logs.setReadOnly(True)
        #self.logs = QWebEngineView(self.ui)
        self.pageContent = '<html><body><h4>No device found</h4></body></html>'
        self.logs.setHtml(self.pageContent)
        self.MHBox.addWidget(self.labeldevice)
        self.MHBox.addWidget(self.labelrun)
        self.MHBox.addWidget(self.methodMenu)
        self.MHBox.addWidget(self.labelresult)
        self.layout.addWidget(self.uiFrame)
        self.layout.addWidget(self.logs)
        return self.ui
    def inspectMethods(self):
        self.genericMethods = list()
        self.deviceMethods = list()
        self.otherMethods = list()
        self.genericPrefix = 'ISD.DeviceDecorator.'
        self.devicePrefix = self.gd_device.__class__.__qualname__
        for m in inspect.getmembers(self.gd_device, inspect.ismethod):
            qname = m[1].__qualname__
            if qname.startswith(self.devicePrefix):
                self.deviceMethods.append(m[1])
            elif qname.startswith(self.genericPrefix):
                self.genericMethods.append(m[1])
            else:
                self.otherMethods.append(m[1])
    @QtCore.pyqtSlot(int)
    def runMethod(self, methodIndex):
        m = None
        if methodIndex < len(self.deviceMethods):
            m = self.deviceMethods[methodIndex]
        elif methodIndex < len(self.deviceMethods) + len(self.genericMethods):
            m = self.genericMethods[methodIndex - len(self.deviceMethods)]
        else:
            m = self.otherMethods[methodIndex -len(self.deviceMethods) - len(self.genericMethods)]
        sig = inspect.signature(m)
        if len(sig.parameters) == 0:
            res = m()
        else:
            res = 'unsupported'
        self.labelresult.setText(str(res))
    def refresh(self):
        self.pageContent='<html><body>'
        self.inspectMethods()
        self.labeldevice.setText('Instance of the <b>'+self.devicePrefix+'</b> class.')
        self.methodMenu.clear()
        self.pageContent += '<div><h4>Introspection</h4>'
        self.pageContent += '<details><summary>List of object methods</summary>'
        self.pageContent += '<table border="1"><tr><th>Name</th><th>Signature</th><th>Qualified name</th></tr>'
        self.pageContent += '<tr><td colspan="3" align="center"><i><b>'+self.devicePrefix+'</b> Methods</i></td></tr>'
        for m in self.deviceMethods:
            self.pageContent += '<tr><td>'+m.__name__+'</td><td>'+str(inspect.signature(m))+'</td><td>'+m.__qualname__+'</td></tr>'
            self.methodMenu.addItem(m.__name__)
        self.pageContent += '<tr><td colspan="3" align="center"><i><b>GenericDevice</b> Methods</i></td></tr>'
        for m in self.genericMethods:
            self.pageContent += '<tr><td>'+m.__name__+'</td><td>'+str(inspect.signature(m))+'</td><td>'+m.__qualname__+'</td></tr>'
            self.methodMenu.addItem(m.__name__)
        self.pageContent += '<tr><td colspan="3" align="center"><i><b>Other</b> Methods</i></td></tr>'
        for m in self.otherMethods:
            self.pageContent += '<tr><td>'+m.__name__+'</td><td>'+str(inspect.signature(m))+'</td><td>'+m.__qualname__+'</td></tr>'
            self.methodMenu.addItem(m.__name__)
        self.pageContent += '</table>'
        self.pageContent += '</details>'
        self.pageContent += '</div>'
        #self.logs.insertHtml(self.pageContent)
        self.pageContent += '</body></html>'
        self.logs.setHtml(self.pageContent)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.apihandlers = list()
        self.resize(640, 400)
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
    def closeEvent(self, event):
        self.quit()
    def quit(self):
        DriverManager.Instance().close()
        GUIManager.Instance().close()
        self.close()
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
        apih.refresh()

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
