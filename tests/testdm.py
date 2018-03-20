from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication
from indi.client.qt.drivermanager import DriverManager
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
dm=DriverManager(test_widget)
dm.show()
rc=app.exec_()
#dm_ui.hide()
dm.hide()
sys.exit(rc)
