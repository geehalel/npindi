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

from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractButton, QSizePolicy, QCheckBox, QPushButton, QSpacerItem, QVBoxLayout, QHBoxLayout, QButtonGroup, QComboBox, QLabel, QFrame
from PyQt5.QtGui import QIcon

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
        self.guiType = PGui.PG_NONE
        self.elementList = list()
        self.initGUI()
        self.updateStateLED()
    def removeWidgets(self):
        for e in self.elementList:
            e.removeWidgets()
        while self.PVBox.count() > 0:
            item = self.PVBox.takeAt(0)
            if not item: continue
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.PVBox.deleteLater()
        del(self.PVBox)
        while self.PHBox.count() > 0:
            item = self.PHBox.takeAt(0)
            if not item: continue
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.PHBox.deleteLater()
        del(self.PHBox)
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
        #QLoggingCategory.qCDebug(QLoggingCategory.NPINDI,'property '+label)
        self.PHBox.addLayout(self.PVBox)
        ptype = self.dataProp.getType()
        if ptype == INDI.INDI_PROPERTY_TYPE.INDI_TEXT:
            self.buildTextGUI()
        elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_NUMBER:
            self.buildNumberGUI()
        elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_LIGHT:
            self.buildLightGUI()
        elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_SWITCH:
            if self.dataProp.r == INDI.ISRule.ISR_NOFMANY:
                self.guiType = PGui.PG_RADIO
            elif len(self.dataProp.vp) > 4:
                self.guiType = PGui.PG_MENU
            else:
                self.guiType = PGui.PG_BUTTONS
            if self.guiType == PGui.PG_MENU:
                self.buildMenuGUI()
            else:
                self.buildSwitchGUI()
        elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_BLOB:
            self.buildBLOBGUI()
    def updateStateLED(self):
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
        lvp = self.dataProp.vp
        if lvp is None:
            return
        for ilight in lvp.values():
            lp = INDI_E(self, self.dataProp)
            lp.buildLight(ilight)
            self.elementList.append(lp)
        horSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.PHBox.addItem(horSpacer)
    def buildSwitchGUI(self):
        svp = self.dataProp.vp
        if svp is None:
            return
        self.groupB = QButtonGroup()
        if self.guiType == PGui.PG_BUTTONS:
            if self.dataProp.r == INDI.ISRule.ISR_1OFMANY:
                self.groupB.setExclusive(True)
            else:
                self.groupB.setExclusive(False)
        elif self.guiType == PGui.PG_RADIO:
            self.groupB.setExclusive(False)
        if self.dataProp.p != INDI.IPerm.IP_RO:
            self.groupB.buttonClicked.connect(self.newSwitch)
        for sp in svp.values():
            lp = INDI_E(self, self.dataProp)
            lp.buildSwitch(self.groupB, sp)
            self.elementList.append(lp)
        horSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.PHBox.addItem(horSpacer)
    def buildMenuGUI(self):
        onItem = -1
        onIndex = 0
        menuOptions = list()
        svp = self.dataProp.vp
        if svp is None:
            return
        self.menuC = QComboBox(self.pg.getContainer())
        if self.dataProp.p == INDI.IPerm.IP_RO:
            self.menuC.activated.connect(self.resetSwitch)
        else:
            self.menuC.activated.connect(self.newSwitch)
        for sp in svp.values():
            if sp.s == INDI.ISState.ISS_ON:
                onItem = onIndex
            onIndex += 1
            lp = INDI_E(self, self.dataProp)
            lp.buildMenuItem(sp)
            oneOption = lp.getLabel()
            menuOptions.append(oneOption)
            self.elementList.append(lp)
        self.menuC.addItems(menuOptions)
        self.menuC.setCurrentIndex(onItem)
        horSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.PHBox.addWidget(self.menuC)
        self.PHBox.addItem(horSpacer)
    def updateMenuGUI(self):
        currentIndex = INDI.IUFindOnSwitchIndex(self.dataProp)
        self.menuC.setCurrentIndex(currentIndex)
    def buildBLOBGUI(self):
        bvp = self.dataProp.vp
        if bvp is None:
            return
        for iblob in bvp.values():
            lp = INDI_E(self, self.dataProp)
            lp.buildBLOB(iblob)
            self.elementList.append(lp)
        horSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.PHBox.addItem(horSpacer)
        self.enableBLOBC = QCheckBox()
        self.enableBLOBC.setIcon(QIcon.fromTheme('modem'))
        self.enableBLOBC.setChecked(True)
        self.enableBLOBC.setToolTip('Enable binary data transfer from this property to the application and vice versa.')
        self.PHBox.addWidget(self.enableBLOBC)
        self.enableBLOBC.stateChanged.connect(self.setBLOBOption)
        if self.dataProp.getPermission() != INDI.IPerm.IP_RO:
            self.setupSetButton('Upload')
    @QtCore.pyqtSlot(int)
    def setBLOBOption(self, state):
        if state == Qt.Checked:
            self.pg.getDevice().getClientManager().set_blob_mode(INDI.BLOBHandling.B_ALSO, self.dataProp.getDeviceName(), self.dataProp.getName())
        else:
            self.pg.getDevice().getClientManager().set_blob_mode(INDI.BLOBHandling.B_NEVER, self.dataProp.getDeviceName(), self.dataProp.getName())
    @QtCore.pyqtSlot(QAbstractButton)
    def newSwitch(self, param):
        svp = self.dataProp.vp
        if svp is None:
            return
        index = None
        name = None
        button = None
        if isinstance(param, str):
            name = param
        elif isinstance(param, int):
            index = param
        else:
            button = param
        if button is not None:
            buttonText = button.text().replace('&','')
            for el in self.elementList:
                if el.getLabel() == buttonText:
                    name = el.getName()
                    break
        if index is not None:
            sp = svp[list(svp)[index]]
            INDI.IUResetSwitch(self.dataProp)
            sp.s = INDI.ISState.ISS_ON
            self.sendSwitch()
        if name is not None:
            sp = INDI.IUFindSwitch(self.dataProp, name)
            if sp is None: return
            if self.dataProp.r == INDI.ISRule.ISR_1OFMANY:
                INDI.IUResetSwitch(self.dataProp)
                sp.s = INDI.ISState.ISS_ON
            else:
                if self.dataProp.r == INDI.ISRule.ISR_ATMOST1:
                    prev_state = sp.s
                    INDI.IUResetSwitch(self.dataProp)
                    sp.s = prev_state
                sp.s = INDI.ISState.ISS_OFF if sp.s == INDI.ISState.ISS_ON else INDI.ISState.ISS_ON
            self.sendSwitch()

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
    def sendSwitch(self):
        if self.dataProp is None:
            return
        self.dataProp.s = INDI.IPState.IPS_BUSY
        for el in self.elementList:
            el.syncSwitch()
        self.updateStateLED()
        self.pg.getDevice().getClientManager().send_new_property(self.dataProp)
    @QtCore.pyqtSlot()
    def sendText(self):
        ptype = self.dataProp.getType()
        if ptype == INDI.INDI_PROPERTY_TYPE.INDI_TEXT:
            tvp = self.dataProp.vp
            if tvp is None:
                return
            self.dataProp.s = INDI.IPState.IPS_BUSY
            for el in self.elementList:
                el.updateTP()
            self.pg.getDevice().getClientManager().send_new_property(self.dataProp)
        elif ptype == INDI.INDI_PROPERTY_TYPE.INDI_NUMBER:
            nvp = self.dataProp.vp
            if nvp is None:
                return
            self.dataProp.s = INDI.IPState.IPS_BUSY
            for el in self.elementList:
                el.updateNP()
            self.pg.getDevice().getClientManager().send_new_property(self.dataProp)
        self.updateStateLED()
    @QtCore.pyqtSlot()
    def sendBlob(self):
        if self.dataProp is None:
            return
        self.dataProp.s = INDI.IPState.IPS_BUSY
        self.pg.getDevice().getClientManager().send_blob(self.dataProp)
    def addWidget(self, w):
        self.PHBox.addWidget(w)
    def addLayout(self, layout):
        self.PVBox.addLayout(layout)
