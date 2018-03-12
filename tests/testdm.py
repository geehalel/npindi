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
