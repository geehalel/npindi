#!/usr/bin/env python2.7

   ###
   # Copyright (c) 2012-2013 geehalel
   #
   # Permission to use, copy, modify, and distribute this software for any
   # purpose with or without fee is hereby granted, provided that the above
   # copyright notice and this permission notice appear in all copies.
   #
   # THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
   # WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
   # MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
   # ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
   # WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
   # ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
   # OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
   #

import os
import sys
import collections
import BaseHTTPServer
import json

from PyQt4 import QtCore, QtGui, QtNetwork
from PyQt4.QtGui import QMainWindow, QWorkspace, QAction, QFileDialog, QApplication, QTabWidget
#from PyQt4 import QtGui
#from PyQt4 import QtCore


from pivy.coin import SoInput, SoDB, SoSeparator
from pivy.quarter import QuarterWidget

FREECADPATH = ['/usr/lib64/freecad/lib', '/usr/lib/freecad/lib'] # path to your FreeCAD.so or FreeCAD.dll file
sys.path.extend(FREECADPATH)

import Simulator
#import World

class SliderPreciseValue(QtGui.QFrame):

    valueChanged = QtCore.pyqtSignal(int)

    def changeValue(self,v):
        self.qlcd.display(v)
        if self.sender != self.qslider:
            self.qslider.setValue(int(v))
        self.valueChanged.emit(int(v))

    def __init__(self, label, digits, minmax, wrap, toggable, lineeditlength, regexpstring=None, tooltip=None):
        QtGui.QFrame.__init__(self)
        self.setFrameShape(QtGui.QFrame.Box)
        #self.setStyleSheet("QFrame {font-size: 8pt}\nQSlider::groove:horizontal {height: 8px}\nQSlider::handle:horizontal {width: 18px}\nQLineEdit, QPushButton {font-size: 8pt;}\n")
        self.qboxlayout=QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight, self)
        self.qlabel=QtGui.QLabel(label)
        self.qlcd=QtGui.QLCDNumber(digits)
        self.qlcd.setFixedHeight(16)
        #self.qlcd.setSmallDecimalPoint(True)
        self.qlcd.setStyleSheet("QFrame {background-color: black; color: red; }")
        self.qlcd.setSegmentStyle(QtGui.QLCDNumber.Filled)
        #self.qslider=QtGui.QSlider(QtCore.Qt.Horizontal)
        self.qslider=QtGui.QDial()
        self.qslider.setFixedHeight(30)
        self.qslider.setWrapping(wrap)
        self.qslider.setMinimum(minmax[0])
        self.qslider.setMaximum(minmax[1])
        self.qlineedit=QtGui.QLineEdit()
        if regexpstring != None:
            self.qlineedit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(regexpstring)))
        self.qlineedit.sizeHint=lambda:QtCore.QSize((lineeditlength*10),14)
        if tooltip != None:
            self.qlineedit.setToolTip(tooltip)
        self.qbutton=QtGui.QPushButton('Set')
        self.qbutton.sizeHint=lambda:QtCore.QSize((30),24)
        self.qboxlayout.addWidget(self.qlabel)
        self.qboxlayout.addWidget(self.qlcd)
        self.qboxlayout.addWidget(self.qslider)
        self.qboxlayout.addWidget(self.qlineedit)
        self.qboxlayout.addWidget(self.qbutton)

        #QtCore.QObject.connect(self.qslider, QtCore.SIGNAL('valueChanged()'), self.changeValue)
        self.qslider.valueChanged.connect(self.changeValue)
        #self.qlineedit.editingFinished.connect(lambda:self.changeValue(float(self.qlineedit.text())))
        self.qlineedit.editingFinished.connect(self.qbutton.click)
        self.qbutton.clicked.connect(lambda:self.changeValue(float(self.qlineedit.text())))
        #QtGui.QObject.connect(self.qslider, SIGNAL(valueChanged(int v)), self.qlcd, SLOT(display(float v))
        self.qboxlayout.setContentsMargins(QtCore.QMargins(5, 0, 5, 0))
        self.sizeHint=lambda:QtCore.QSize(260,70)
        self.show()



class DockManualSetting(QtGui.QDockWidget):
    def __init__(self, simulator):
        self.dockwidget=QtGui.QDockWidget.__init__(self, QtCore.QCoreApplication.translate("DockManualSetting", "Manual Settings"))
        self.setStyleSheet("QFrame, QLineEdit, QPushButton, QCheckBox {font-size: 8pt;}\n")
        self.simulator=simulator
        self.setAllowedAreas(QtCore.Qt.TopDockWidgetArea | QtCore.Qt.BottomDockWidgetArea)
        self.content=QtGui.QWidget()
        self.content.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)

        #self.qboxlayout=QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom, self.content)
        self.qgridlayout=QtGui.QGridLayout( self.content)

        self.latitudeSPV=SliderPreciseValue(QtCore.QCoreApplication.translate("DockManualSetting", "Latitude"), 7, (-90.00, 90.00), False, False, 8, '-?\\d{1,2}(\.\\d{1,4})?', 'Enter Latitude in decimal format, negative for South hemisphere')
        self.latitudeSPV.valueChanged.connect(self.simulator.setLatitude)
        self.hemisphereframe=QtGui.QFrame()
        self.hemisphereframe.setFrameShape(QtGui.QFrame.Box)
        self.hemispherecheckbox=QtGui.QCheckBox('Southern Hemisphere', self.hemisphereframe)
        self.hemispherecheckbox.setContentsMargins(4,4,4,4)
        self.hemispherecheckbox.setCheckState(QtCore.Qt.Unchecked)
        self.hemispherecheckbox.setCheckable(False)
        self.raangleSPV=SliderPreciseValue(QtCore.QCoreApplication.translate("DockManualSetting", "RA Angle"), 8, (0.00, 360.00), True, False, 8, '(([0-2]?\\d{1,2})|(3[0-5][0-9]))(\.\\d{1,4})?', 'Enter RA axis angle in decimal degrees')
        self.raangleSPV.valueChanged.connect(self.simulator.setRAangle)
        self.deangleSPV=SliderPreciseValue(QtCore.QCoreApplication.translate("DockManualSetting", "DE Angle"), 8, (0.00, 360.00), True, False, 8, '(([0-2]?\\d{1,2})|(3[0-5][0-9]))(\.\\d{1,4})?', 'Enter DE axis angle in decimal degrees')
        self.deangleSPV.valueChanged.connect(self.simulator.setDEangle)
        self.focuserpositionSPV=SliderPreciseValue(QtCore.QCoreApplication.translate("DockManualSetting", "Foc. pos."), 6, (0.00, 120.00), True, False, 8, '((0?\\d{1,2})|(1[0-1][0-9]))(\.\\d{1,4})?', 'Enter Focuser position in millimeters')
        self.focuserpositionSPV.valueChanged.connect(self.simulator.setFocuserposition)
        self.focuserangleSPV=SliderPreciseValue(QtCore.QCoreApplication.translate("DockManualSetting", "Foc. ang."), 6, (0.00, 360.00), True, False, 8, '(([0-2]?\\d{1,2})|(3[0-5][0-9]))(\.\\d{1,4})?', 'Enter Focuser angle in decimal degrees')       
        self.focuserangleSPV.valueChanged.connect(self.simulator.setFocuserangle)
        #self.qboxlayout.addWidget(self.latitudeSPV)
        #self.qboxlayout.addWidget(self.raangleSPV)
        #self.qboxlayout.addWidget(self.deangleSPV)
        self.qgridlayout.addWidget(self.latitudeSPV, 0, 0)
        self.qgridlayout.addWidget(self.hemisphereframe, 1, 0)
        self.qgridlayout.addWidget(self.raangleSPV, 0, 1)
        self.qgridlayout.addWidget(self.deangleSPV, 1, 1)
        self.qgridlayout.addWidget(self.focuserpositionSPV, 0, 2)
        self.qgridlayout.addWidget(self.focuserangleSPV, 1, 2)

        self.content.show()
        self.setWidget(self.content)

class LcdArray(QtGui.QScrollArea):
    
    def __init__(self, valuelist):
        QtGui.QScrollArea.__init__(self)
        self.setStyleSheet("QFrame  {font-size: 8pt;}\n")
        self.qgridlayout=QtGui.QGridLayout( self)
        self.dictionnary=dict()
        lcdrecord=collections.namedtuple('LcdRecord', ['name', 'qlabel', 'qlcd']) 
        for  index, (name, label, digits, mode) in enumerate(valuelist):
            qlabel=QtGui.QLabel(label, self)
            qlcd=QtGui.QLCDNumber(digits)
            qlcd.setFixedHeight(16)
            lcdmode=QtGui.QLCDNumber.Dec
            if (mode=='H'):lcdmode=QtGui.QLCDNumber.Hex 
            elif (mode=='B'):
                lcdmode=QtGui.QLCDNumber.Bin
            qlcd.setMode(lcdmode)
            qlcd.setStyleSheet("QFrame {background-color: black; color: red; }")
            r=lcdrecord(name, qlabel, qlcd)
            self.dictionnary[name]=r
            self.qgridlayout.addWidget(r.qlabel, index, 0)
            self.qgridlayout.addWidget(r.qlcd, index, 1)
        self.show()

    def setValue(self, name, value):
        self.dictionnary[name].qlcd.display(value)

class DockSimulation(QtGui.QDockWidget):
    def __init__(self, simulator, manualdock):
        QtGui.QDockWidget.__init__(self, QtCore.QCoreApplication.translate("DockSimulation", "Simulation"))
        self.setStyleSheet("QFrame, QLineEdit, QPushButton, QCheckBox {font-size: 8pt;}\n")

        self.simulator=simulator
        self.manualdock=manualdock
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        #self.content=QtGui.QWidget()
        #self.content.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)

        #self.tabwidget=QtGui.QTabWidget(self.content)
        self.tabwidget=QtGui.QTabWidget(self)
        self.tabwidget.setTabPosition(QtGui.QTabWidget.West)
        #self.ralcd=LcdArray([('RA_STEPS_360','Tot. steps', 8, 'H'), ('ra_position', 'Cur. step', 8, 'H')])
        #self.delcd=LcdArray([('DE_STEPS_360', 'Tot. steps', 8, 'H'), ('de_position','Cur. step', 8, 'H')])
        #self.piclcd=LcdArray([('TIMER1H','TIMER1H', 8, 'H'), ('TIMER1L','TIMER1L', 8,'H')])
        #self.tabwidget.addTab(self.ralcd, "RA Stepper")
        #self.tabwidget.addTab(self.delcd, "DE Stepper")
        #self.tabwidget.addTab(self.piclcd, "PIC Reg.")

        #self.content.show()
        self.tabwidget.show()
        #self.setWidget(self.content)
        self.setWidget(self.tabwidget)

    def process_config(self, json_data, tcp_handler):
        self.config=json.loads(json_data)
        if not (self.config.has_key('config')):
            print('  received: not a config object !!')
            return
        self.config=self.config['config']
        self.allvars={}
        for tabitem in iter(self.config):
            varlcds=[]
            for debugvar in iter(self.config[tabitem]):
                if self.config[tabitem][debugvar]['type'] == 'lcd':
                    varlcds.append((debugvar, debugvar, int(self.config[tabitem][debugvar]['size']), 
                                    self.config[tabitem][debugvar]['mode']))
            arraylcd=LcdArray(varlcds)
            for v in iter(varlcds):
                self.allvars[v[0]]=arraylcd
            self.tabwidget.addTab(arraylcd, tabitem)
            #self.ralcd.setValue(v, int(self.values[v]))
        tcp_handler.process_json=self.process_json

    def process_json(self, json_data, tcp_handler):
        self.values=json.loads(json_data)
        for v in iter(self.values):
            lcd=self.allvars[v]
            lcd.setValue(v, int(self.values[v]))
            if (v == 'ra_position'):
                angle=0x800000-int(self.values[v])
                if (angle < 0): angle = angle + 0x1C2000
                #self.simulator.setRAangle((360 * angle) / 0x1C2000)
                self.manualdock.raangleSPV.changeValue(float(360 * angle) / 0x1C2000)
                

class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        print('got GET')
        self.send_response(200,'Ok-alive')

    def do_PUT(self):
        print('got PUT')
        self.send_response(200,'Ok-data displayed')

class TCPHandler(QtCore.QObject):
    def __init__(self, local_socket, server, process_json):
        print('Initializing: socket state '+str(local_socket.state()))
        QtCore.QObject.__init__(self)
        self.inputSocket = local_socket
        self.inputSocket.setSocketOption(QtNetwork.QTcpSocket.KeepAliveOption, 1)
        self.process_json=process_json
        self.inputSocket.readyRead.connect(lambda:self.readDatas())
        print('Signal connected')
        self.inputSocket.disconnected.connect(self.inputDisconnected)
        self.server=server
        self.currentData = QtCore.QByteArray()
        self.currentread=0
        self.bytestoread=4
        self.readlengthstate=True
        self.inputSocket.write('Ok')
  
    def __del__(self):
        print('Cleaning socket')
        # Clean up our socket objects, in accordance to the hint from the Qt docs (recommended practice)
        self.inputSocket.deleteLater()
        self.server.currentClient=None
                         
    def readDatas(self):        
        #print('Got data-'+str(self.inputSocket.bytesAvailable())+' bytes-'+str(self.currentread) + '/' + str(self.bytestoread))
        read = self.inputSocket.read(self.inputSocket.bytesAvailable()) 
        #CAVEAT: readAll() was seemingly truncating data here
        
        if not isinstance(read, basestring):
            print('Socket read failure')
            return
        #self.process_json=process_json

        #Convert data into a bytearray for easier processing
        datas = QtCore.QByteArray(read)
        rest=len(read)
        while (self.bytestoread - self.currentread) <= rest:
            self.currentData.append(datas.left(self.bytestoread - self.currentread))
            rest=rest-(self.bytestoread - self.currentread)
            datas=datas.right(rest)
            self.currentread=0
            if self.readlengthstate:
                (self.bytestoread, ok)=self.currentData.toInt()
                self.readlengthstate=False
            else:
                #print 'Processing json: ' + str(self.currentData)
                self.process_json(str(self.currentData), self)
                self.readlengthstate=True
                self.bytestoread=4
            self.currentData.clear()

        self.currentData.append(datas)
        self.currentread=self.currentData.size()
  
    @QtCore.pyqtSlot()
    def inputDisconnected(self):
        print('I have been disconnected')
        # Part of the hardening - ensure all buffered local replay data is read and relayed
        if self.inputSocket.bytesAvailable():
            self.readDatas()
        self.__del__()
 
def acceptClient(server, process_json):
    print('got a new client')
    if server.currentClient==None:
        server.currentClient=TCPHandler(server.nextPendingConnection(), server, process_json)
    

def main():
    try:
        import FreeCAD
    except ValueError:
        print('FreeCAD library not found. Please check the FREECADPATH variable in this script is correct')
        sys.exit(1)
    simapp=QtGui.QApplication(sys.argv)
    simappwindow=QtGui.QMainWindow()
    simappwindow.setWindowTitle("EQ Simulator")


    s=None
    s=Simulator.Simulator()
    s.Build()
    #w=None
    #w=World.World()
    #w.Build()
    manualsettingswidget=DockManualSetting(s)
    simulationwidget=DockSimulation(s, manualsettingswidget)
    simappwindow.addDockWidget(QtCore.Qt.BottomDockWidgetArea, manualsettingswidget)
    simappwindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, simulationwidget)
# FreeCAD integration: see http://sourceforge.net/apps/mediawiki/free-cad/index.php?title=Embedding_FreeCADGui/fr
# Utilisation d'un module tiers (en l'occurence Quarter ?)
#FreeCADGui.setupWithoutGUI()



    widget3D=QtGui.QWidget()
    widget3D.setMinimumSize(712,400)
    qw=QuarterWidget(widget3D)
    qw.setMinimumSize(712, 400)

    scene=SoSeparator()
    scene.addChild(s.scene)
    #scene.addChild(w.scene)
    qw.setSceneGraph(scene)
    print("texturing "+str(qw.sorendermanager.isTexturesEnabled()))

    #Http server
    #server=BaseHTTPServer.HTTPServer(('', 8000), HTTPHandler)
    #server.serve_forever()
     
    #TCP Server
    server=QtNetwork.QTcpServer()
    server.setMaxPendingConnections(1)
    server.currentClient=None
    server.newConnection.connect(lambda:acceptClient(server, simulationwidget.process_config))
    server.listen(QtNetwork.QHostAddress.Any, 64101)

#s.Embed(widget3D)
    simappwindow.setCentralWidget(widget3D)
    simappwindow.show()
#SoGui.mainloop()
    simapp.exec_() 

#if __name__ == "Simulator":
if __name__ == "__main__":
    main()
