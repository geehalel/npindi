from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy, QPushButton, QLineEdit, QComboBox, QLabel, QApplication, QMainWindow, QMessageBox, QAction, QGroupBox, QVBoxLayout, QTextEdit, QHBoxLayout, QFrame, QDialog, QDialogButtonBox
#from PyQt5.QtWebEngineWidgets import QWebEngineView

from indi.INDI import *
from indi.client.qt.indicommon import *
from indi.client.qt.drivermanager import DriverManager
from indi.client.qt.guimanager import GUIManager
from indi.client.qt.indilistener import INDIListener
from indi.client.qt.indistd import *
from indi.client.qt.inditelescope import Telescope

# used for introspection in APIHandler
import inspect
import sys
class APIHandler(QtCore.QObject):
    __modules = ['indi.INDI', 'indi.client.qt.indicommon', 'indi.client.qt.inditelescope' ]
    #__modules = ['indi.client.qt.inditelescope'] # use first level class search here
    __text_types = ['int', 'float', 'str']
    __enum_types = list()
    def __init__(self, gd_device):
        super().__init__()
        self.gd_device = gd_device
        QLoggingCategory.qCDebug(QLoggingCategory.NPINDI,' API handler; new device '+ self.gd_device.getDeviceName())
        self.ui = None
    @staticmethod
    def buildEnumTypes():
        import importlib
        import enum
        for module_name in APIHandler.__modules:
            module = importlib.import_module(module_name)
            for m in inspect.getmembers(module, inspect.isclass):
                if issubclass(m[1], enum.Enum):
                    if m not in APIHandler.__enum_types:
                        APIHandler.__enum_types.append(m)
                # else: # Check first level enums in class
                #     for c in inspect.getmembers(m[1], inspect.isclass):
                #         if issubclass(c[1], enum.Enum):
                #             APIHandler.__enum_types.append(c)
        APIHandler.__enum_types.sort()
    def buildUI(self):
        self.ui = QGroupBox(self.gd_device.getDeviceName())
        #self.ui.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout = QVBoxLayout(self.ui)
        self.uiFrame=QFrame(self.ui)
        #self.uiFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.uiLayout = QVBoxLayout(self.uiFrame)
        self.MHBox = QHBoxLayout()
        self.uiLayout.addLayout(self.MHBox)
        self.methodMenu = QComboBox(self.ui)
        self.methodMenu.activated.connect(self.runMethod)
        self.methodMenu.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.labeldevice = QLabel('No device found', self.ui)
        self.RHBox=QHBoxLayout()
        self.uiLayout.addLayout(self.RHBox)
        self.labelrun = QLabel('Run ', self.ui)
        self.labelres = QLabel('Result', self.ui)
        self.labelresult = QLabel('', self.ui)
        self.labelresult.setStyleSheet('QLabel {background-color: white}')
        self.labelresult.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.logs = QTextEdit(self.ui)
        self.logs.setReadOnly(True)
        #self.logs = QWebEngineView(self.ui)
        self.showmethods = QPushButton('Show/hide methods')
        self.showmethods.clicked.connect(lambda c: self.logs.setVisible(not self.logs.isVisible()))
        self.showmethods.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.uiLayout.addWidget(self.showmethods)
        self.pageContent = '<html><body><h4>No device found</h4></body></html>'
        self.logs.setHtml(self.pageContent)
        self.MHBox.addWidget(self.labeldevice, Qt.AlignLeft)
        self.MHBox.addWidget(self.labelrun, Qt.AlignRight)
        self.MHBox.addWidget(self.methodMenu, Qt.AlignRight)
        self.RHBox.addWidget(self.labelres)
        self.RHBox.addWidget(self.labelresult)
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
    def setparamtext(self, pvalues, param, ptype, pedit):
        value=None
        thetype = ptype.currentText()
        textvalue = pedit.text()
        #print('setparamtext: '+thetype+' '+textvalue)
        try:
            if thetype == 'int':
                value = int(textvalue)
            elif thetype == 'float':
                value =  float(textvalue)
            elif thetype == 'str':
                value = textvalue
        except:
            value = ''
        pvalues[param.name] = value
    def setparamenum(self, index, pvalues, param, ptype, pvalue):
        #print('setparamnum ' + str(index))
        theenum = APIHandler.__enum_types[ptype.currentIndex()-len(APIHandler.__text_types)][1]
        i = 0
        value = None
        for v in theenum:
            if i == index:
                value = v
                break
            i = i + 1
        pvalues[param.name] = value
    def switchparamUI(self, index, ptype, pedit, pvalue, pvalues, param):
        if index < len(APIHandler.__text_types):
            pvalue.hide()
            pedit.show()
        else:
            pvalue.clear()
            theenum = APIHandler.__enum_types[index-len(APIHandler.__text_types)][1]
            for v in theenum:
                pvalue.addItem(str(v))
            self.setparamenum(0, pvalues, param, ptype, pvalue)
            pedit.hide()
            pvalue.show()
    def paramUI(self, param, parent, pvalues):
        ui = QFrame(parent)
        layout = QHBoxLayout(ui)
        pname = QLabel(param.name)
        ptype= QComboBox(ui)
        pvalue = QComboBox(ui)
        ptype.addItems(APIHandler.__text_types)
        ptype.addItems([m[0] for m in APIHandler.__enum_types])
        pedit = QLineEdit(ui)
        layout.addWidget(pname)
        layout.addWidget(ptype)
        layout.addWidget(pedit)
        layout.addWidget(pvalue)
        pvalue.hide()
        pedit.editingFinished.connect(lambda : self.setparamtext(pvalues, param, ptype, pedit))
        ptype.activated.connect(lambda index: self.switchparamUI(index, ptype, pedit, pvalue, pvalues, param))
        pvalue.activated.connect(lambda index: self.setparamenum(index, pvalues, param, ptype, pvalue))
        return ui
    @QtCore.pyqtSlot(int)
    def runMethod(self, methodIndex):
        res = 'running...'
        self.labelresult.setText(res)
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
            pvalues = OrderedDict((k, None) for k in sig.parameters)
            paramdialog = QDialog()
            paramdialog.setWindowTitle('Set parameters for Run '+m.__name__)
            paramdialog.setModal(True)
            paramlayout = QVBoxLayout(paramdialog)
            for p in sig.parameters.values():
                pui = self.paramUI(p, paramdialog, pvalues)
                paramlayout.addWidget(pui)
            paramdialogbbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,paramdialog)
            paramdialogbbox.accepted.connect(paramdialog.accept)
            paramdialogbbox.rejected.connect(paramdialog.reject)
            paramlayout.addWidget(paramdialogbbox)
            if paramdialog.exec_() != QDialog.Accepted:
                res = 'cancelled'
                self.labelresult.setText(res)
                return
            #res = 'unsupported'+str(pvalues)
            params = pvalues.values()
            try:
                res = m(*params)
            except:
                res = sys.exc_info()[0].__name__+':'+str(sys.exc_info()[1])
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
        self.resize(800, 480)
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
        #self.centralFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        #self.centralSpacer = QSpacerItem(self.width(), self.height(), QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(self.centralFrame)
        self.centrallayout = QVBoxLayout(self.centralFrame)
        self.centrallayout.setAlignment(Qt.AlignTop)
        #self.centrallayout.addStretch(1)
        #self.centrallayout.addSpacerItem(self.centralSpacer)
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
                'PyQt INDI API in your Qt application. With the help of '
                'Pyhton introspection you will be able to see and even run '
                'the methods defined for the INDI devices catched by the API.')
    @QtCore.pyqtSlot(ISD.GDInterface)
    def addAPIHandler(self, gdi):
        apih = APIHandler(gdi)
        apihui = apih.buildUI()
        #self.centrallayout.removeItem(self.centralSpacer)
        self.centrallayout.addWidget(apihui)
        #self.centrallayout.addItem(self.centralSpacer)
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

# This call is only necessary for the test API application
APIHandler.buildEnumTypes()

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
