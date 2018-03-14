from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy, QCheckBox, QPushButton, QSpacerItem, QVBoxLayout, QHBoxLayout, QButtonGroup, QComboBox, QLabel, QFrame

from indi.client.qt.indicommon import *
from indi.INDI import *
from indi.client.qt.indielement import INDI_E
class INDI_P(QObject):
    def __init__(self, ipg, prop):
        super().__init__()
        self.pg = ipg
        self.dataProp = prop
        self.name = prop.getName()
        self.PHBox = QHBoxLayout()
        self.PHBox.setContentsMargins(0, 0, 0, 0)
        self.PVBox = QVBoxLayout()
        self.PVBox.setContentsMargins(0, 0, 0, 0)
        self.elementList = list()
        self.initGUI()
        self.updateStateLed()
    def getGUIType(self):
        return self.guiType
    def getGroup(self):
        return self.pg
    def getContainer(self):
        return self.PHBox
    def getName(self):
        return self.name
    def getElements(self):
        return self.elementList
    def initGUI(self):
        label = self.dataProp.getLabel()
        if not label:
            label = self.name
        self.labelW = QLabel(label, self.pg.getContainer())
        self.labelW.setFrameShape(QFrame.StyledPanel)
        self.labelW.setFixedWidth(PROPERTY_LABEL_WIDTH)
        self.labelW.setTextFormat(Qt.RichText)
        self.labelW.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.labelW.setWordWrap(True)
        self.PHBox.addWidget(self.labelW)
        self.labelW.show()

        self.PHBox.addLayout(self.PVBox)
        ptype = self.dataProp.getType()
        if ptype == INDI.INDI_PROPERTY_TYPE.INDI_TEXT:
            self.buildTextGUI()
        elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_NUMBER:
            self.buildNumberGUI()
        elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_LIGHT:
            self.buildLightGUI()
        elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_SWITCH:
            self.buildSwitchGUI()
        elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_BLOB:
            self.buildBLOBGUI()
    def updateStateLed(self):
        pstate=self.dataProp.getState()
        if pstate == INDI.IPState.IPS_IDLE:
            self.labelW.setStyleSheet('QLabel {color: gray}')
        elif pstate == INDI.IPState.IPS_OK:
            self.labelW.setStyleSheet('QLabel {color: green}')
        elif pstate == INDI.IPState.IPS_BUSY:
            self.labelW.setStyleSheet('QLabel {color: orange}')
        elif pstate == INDI.IPState.IPS_ALERT:
            self.labelW.setStyleSheet('QLabel {color: red}')
    def buildTextGUI(self):
        tvp = self.dataProp.vp
        if tvp is None:
            return
        for itext in tvp.values():
            lp = INDI_E(self, self.dataProp)
            lp.buildText(itext)
            self.elementList.append(lp)
        horSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.PHBox.addItem(horSpacer)
        if self.dataProp.p == INDI.IPerm.IP_RO:
            return
        self.setupSetButton('Set')
    def buildNumberGUI(self):
        nvp = self.dataProp.vp
        if nvp is None:
            return
        for inumber in nvp.values():
            lp = INDI_E(self, self.dataProp)
            lp.buildNumber(inumber)
            self.elementList.append(lp)
        horSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.PHBox.addItem(horSpacer)
        if self.dataProp.p == INDI.IPerm.IP_RO:
            return
        self.setupSetButton('Set')
    def buildLightGUI(self):
        pass
    def buildSwitchGUI(self):
        pass
    def buildBLOBGUI(self):
        pass
    def setupSetButton(self, caption):
        self.setB = QPushButton(caption, self.pg.getContainer())
        self.setB.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setB.setMinimumWidth(MIN_SET_WIDTH)
        self.setB.setMaximumWidth(MAX_SET_WIDTH)
        self.setB.clicked.connect(self.processSetButton)
        self.PHBox.addWidget(self.setB)
    @QtCore.pyqtSlot()
    def processSetButton(self):
        ptype = self.dataProp.getType()
        if ptype == INDI.INDI_PROPERTY_TYPE.INDI_TEXT:
            self.sendText()
        elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_NUMBER:
            self.sendText()
        elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_BLOB:
            self.sendBlob()
    @QtCore.pyqtSlot()
    def sendText(self):
        pass
    @QtCore.pyqtSlot()
    def sendBlob(self):
        pass
    def addWidget(self, w):
        self.PHBox.addWidget(w)
    def addLayout(self, layout):
        self.PVBox.addLayout(layout)
    @QtCore.pyqtSlot()
    def sendText(self):
        pass
