from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication

from indi.client.indiqtclient import IndiQtClient
from indi.INDI import *
from indi.indibase.basedevice import BaseDevice

class IndiThread(QtCore.QThread):
    def __init__(self, parent=None):
        super(IndiThread, self).__init__(parent)
    @QtCore.pyqtSlot(BaseDevice)
    def handlenewdevice(self, device):
        print('New Device', device.name)
    @QtCore.pyqtSlot(BaseDevice)
    def handleremovedevice(self, device):
        print('Remove Device', device.name)
    @QtCore.pyqtSlot(IVectorProperty)
    def handlenewproperty(self, prop):
        print('New Property', prop.name, 'for', prop.device.name)
    @QtCore.pyqtSlot(IVectorProperty)
    def handleremoveproperty(self, prop):
        print('Remove Property', prop.name, 'for', prop.device.name)   
    @QtCore.pyqtSlot(IBLOB)
    def handlenewblob(self, blob):
        print('New BLOB', blob.name, 'for', blob.bvp.name, '('+blob.bvp.device.name+')'\
              'format', blob.format, 'size', str(blob.size), 'len', str(blob.bloblen))
    @QtCore.pyqtSlot(IVectorProperty)
    def handlenewswitch(self, switch):
        print('New Switch states for', switch.name, 'in', switch.device.name, \
              [(switch.vp[e].name, str(switch.vp[e].s)) for e in switch.vp])
    @QtCore.pyqtSlot(IVectorProperty)
    def handlenewlight(self, light):
        print('New Light states for', light.name, 'in', light.device.name, \
              [(light.vp[e].name, str(light.vp[e].s)) for e in light.vp])
    @QtCore.pyqtSlot(IVectorProperty)
    def handlenewnumber(self, number):
        print('New Number values for', number.name, 'in', number.device.name, \
              [(number.vp[e].name, str(number.vp[e].value)) for e in number.vp])
    @QtCore.pyqtSlot(IVectorProperty)
    def handlenewtext(self, text):
        print('New Text values for', text.name, 'in', text.device.name, \
              [(text.vp[e].name, text.vp[e].text) for e in text.vp])
        
class TestQtIndi(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()                
    def initUI(self):               
        qbtn = QPushButton('Quit', self)
        qbtn.clicked.connect(self.quit)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 50)       
        
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Test indiqtclient')    
        self.show()
    def quit(self):
        self.close()
        QApplication.instance().quit()
        
import sys

indiqtclient=IndiQtClient()
indithread=IndiThread()
indiqtclient.mediator.newdevice.connect(indithread.handlenewdevice)
indiqtclient.mediator.removedevice.connect(indithread.handleremovedevice)
indiqtclient.mediator.newproperty.connect(indithread.handlenewproperty)
indiqtclient.mediator.removeproperty.connect(indithread.handleremoveproperty)
indiqtclient.mediator.newblob.connect(indithread.handlenewblob)
indiqtclient.mediator.newswitch.connect(indithread.handlenewswitch)
indiqtclient.mediator.newlight.connect(indithread.handlenewlight)
indiqtclient.mediator.newnumber.connect(indithread.handlenewnumber)
indiqtclient.mediator.newtext.connect(indithread.handlenewtext)

if not indiqtclient.connect():
    print('Usage: start a local indiserver using\n  indiserver indi_simulator_ccd indi_simulator_telescope')
    sys.exit(1)
indiqtclient.set_blob_mode(INDI.BLOBHandling.B_ALSO, 'CCD Simulator', None)

app=QApplication(sys.argv)
widget=TestQtIndi()
rc=app.exec_()
indiqtclient.disconnect()
sys.exit(rc)
