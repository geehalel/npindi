from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QMainWindow, QMessageBox, QAction
from indi.client.qt.drivermanager import DriverManager
from indi.client.qt.guimanager import GUIManager
class TestWidget(QMainWindow):
    def __init__(self):
        super().__init__()
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


        self.setWindowTitle('Test DriverManager')
        self.show()
    def closeEvent(self, event):
        self.quit()
    def quit(self):
        GUIManager.Instance().close()
        DriverManager.Instance().close()
        self.close()
        #QApplication.instance().quit()
    def about(self):
        QMessageBox.about(self, 'Driver Manager Test',
                'This <b>Test</b> example demonstrates how to integrate '
                'PyQt Driver Manager in your Qt application, inside a menu bar. ')


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
test_widget=TestWidget()

#dm_ui=DriverManagerUI()
#dm_ui.show()
#DriverManager.Instance().setParent(test_widget)
DriverManager.Instance().show()
ag = DriverManager.Instance().getActionGroups()
for gkey, ggroup in ag.items():
    test_widget.menuBar().addSeparator()
    gmenu = test_widget.menuBar().addMenu(gkey)
    for a in ggroup.actions():
        gmenu.addAction(a)
rc=app.exec_()
#dm_ui.hide()
#DriverManager.Instance().hide()
sys.exit(rc)
