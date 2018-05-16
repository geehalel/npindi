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

from PyQt5.QtWidgets import QFrame, QMessageBox, QSizePolicy, QPushButton, QLayout, QGridLayout, QVBoxLayout, QHBoxLayout, QLCDNumber, QLabel
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import pyqtSlot
import enum
from indi.client.qt.skypoint import dms
from indi.client.qt.inditelescope import *

class LCD(QLabel):
    _lcd_font = None
    _default_font = 'NODSEG14 Classic'
    _all_off = '!'
    _inactive = 'color: "#800000"; background-color:"black";'
    _active = ' color: "red"; background-color:"black";'
    _radius = ' border-radius: 10px;'
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fontdatabase = QFontDatabase()
        self.state  = LCD._inactive
        self.radius = LCD._radius
        if LCD._lcd_font is None:
            LCD._lcd_font = self.fontdatabase.font(LCD._default_font, 'Bold', 24)
            if LCD._lcd_font.family() != LCD._default_font:
                LCD._lcd_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
                LCD._lcd_font.setPointSize(24)
                LCD._lcd_font.setWeight(QFont.Bold)
            print('loaded font', LCD._lcd_font.family())
        super().setFont(LCD._lcd_font)
        #self.setMargin(4)
        self.setStyleSheet('QLabel {'+self.state + self.radius + '}')
    def setText(self, text):
        if  LCD._lcd_font.family() == LCD._default_font:
            text = text.replace(' ', LCD._all_off)
        super().setText(text)
    def setFont(self, family):
        font = self.fontdatabase.font(family, self.font().styleName(), self.font().pointSize())
        if font.family() != family:
            font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
            font.setPointSize(24)
            font.setWeight(QFont.Bold)
        super().setFont(font)
    def setPointSize(self, size):
        font = self.fontdatabase.font(self.font().family(), self.font().styleName(), size)
        super().setFont(font)
        if size <= 12:
            self.radius = ' border-radius: 5px;'
            self.setStyleSheet('QLabel {'+self.state + self.radius + '}')
    def setActivated(self, activated):
        self.state = LCD._active if activated else LCD._inactive
        self.setStyleSheet('QLabel {'+self.state + self.radius + '}')
    #def setWeight(self, weight):
    #    font = self.fontdatabase.font(self.font().family(), weight, self.font().pointSize())
    #    super().setFont(font)
class LLCD(LCD):
    def __init__(self, parent=None, label='', width=None, text=''):
        super().__init__(parent)
        self.label = label
        self.width = width if width is not None else len(self.label) + len(text)
        self.text = text
    def setLabel(self, label):
        self.label = label
        self.setText(text)
    def setText(self, text):
        self.text = text
        l = self.width - (len(self.label) + len(self.text))
        if l <= 0:
            l = 1
        lt = self.width -(len(self.label) + l)
        t = '%s%*s%*s' % (self.label, l, ' ', lt, self.text[:lt])
        super().setText(t)
class DMSLLCD(LLCD):
    class AngleFormat(enum.Enum):
        HOURS_DECIMAL = 0
        DEGREES_DECIMAL = 1
        HOURS_HMS = 2
        DEGREES_DMS = 3
        HOURS_HMS_MS = 4
        DEGRES_DMS_MS = 5
    def __init__(self, parent=None, label='', width=None, value=None, angleformat=AngleFormat.DEGREES_DECIMAL, anglerange=dms.AngleRanges.ZERO_TO_2PI):
        super().__init__(parent=parent, label=label, width=width, text=None)
        self.value = value
        self.format = angleformat
        self.range = anglerange
        self.setText(self.formatDMS())
    def setFormat(self, angleformat):
        self.format = angleformat
    def setRange(self, anglerange):
        self.range = anglerange
    def formatDMS(self):
        if self.value is None:
            return '--------'
        text = 'FORMAT ERROR'
        if self.format == DMSLLCD.AngleFormat.HOURS_DECIMAL:
            text = str(self.value.Hours())
        elif self.format == DMSLLCD.AngleFormat.DEGREES_DECIMAL:
            text = str(self.value.Degrees())
        elif self.format == DMSLLCD.AngleFormat.HOURS_HMS:
            h, m, s, ss = self.value.hmss()
            #print(h, m, s, ss)
            text = '%02d:%02d:%02d' % (h, m, s)
        elif self.format == DMSLLCD.AngleFormat.DEGREES_DMS:
            d, m, s, ss = self.value.dmss()
            #print(d, m, s, ss)
            if self.range == dms.AngleRanges.MINUSPI_TO_PI:
                text = '%+03d:%02d:%02d' % (d, m, s)
            else:
                text = '%03d:%02d:%02d' % (d, m, s)
        return text
    def setDMS(self, dms):
        self.value = dms
        self.setText(self.formatDMS())
class mountMotionController(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.motionlayout = QGridLayout()
        self.buttonlist=[
            [('Center', 12), ('\u2bc5', 36), ('Find', 12)],
            [('\u2bc7', 36), ('\u2b6e', 36), ('\u2bc8', 36)],
            [('Guide', 12), ('\u2bc6', 36), ('Slew', 12)]
            ]
        self.buttons = list()
        for row in range(len(self.buttonlist)):
            buttonrow = list()
            for col in range(len(self.buttonlist[row])):
                b = self.buttonlist[row][col]
                button = QPushButton(b[0], self)
                button.setCheckable(True)
                button.setEnabled(False)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setStyleSheet('QPushButton {font-size:'+str(b[1])+'pt; color:"#901010"; background-color:"#301010"} QPushButton:checked {color:"red";}')
                self.motionlayout.addWidget(button, row, col)
                buttonrow.append(button)
            self.buttons.append(buttonrow)
        self.RAUp = self.buttons[1][2]
        self.RADown = self.buttons[1][0]
        self.DECUp = self.buttons[0][1]
        self.DECDown = self.buttons[2][1]
        self.speedGuide = self.buttons[2][0]
        self.speedCenter = self.buttons[0][0]
        self.speedFind = self.buttons[0][2]
        self.speedSlew = self.buttons[2][2]
        self.tracklist =[('\u2605', 12), ('\u2609', 12), ('\u263D', 12), ('\u270d', 12)]
        #self.tracklist =[('\u2605', 12), ('\u2609', 12), ('\u263D', 12)]
        self.tracklayout = QHBoxLayout()
        #self.tracklayout.setSizeConstraint(QLayout.SetMinimumSize)
        #self.tracklayout.setContentsMargins(0, 0, 0, 0)
        self.trackbuttons = list()
        for b in self.tracklist:
            button = QPushButton(b[0], self)
            button.setCheckable(True)
            button.setEnabled(False)
            button.setMaximumWidth(60)
            #button.setContentsMargins(0, 0, 0, 0)
            #button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
            button.setStyleSheet('QPushButton {font-size:'+str(b[1])+'pt; color:"#901010"; background-color:"#301010";} QPushButton:checked {color:"red";}')
            self.tracklayout.addWidget(button)
            self.trackbuttons.append(button)
        self.trackSidereal = self.trackbuttons[0]
        self.trackSolar = self.trackbuttons[1]
        self.trackLunar = self.trackbuttons[2]
        self.trackCustom = self.trackbuttons[3]
        self.trackActivate = self.buttons[1][1]
        self.layout.addLayout(self.motionlayout)
        self.layout.addLayout(self.tracklayout)
    def setActivated(self, activated):
        for brow in self.buttons:
            for b in brow:
                b.setEnabled(activated)
        for b in self.trackbuttons:
            b.setEnabled(activated)
    def makeConnections(self, scope):
        self.scope = scope
        if not self.scope.canControlTrack():
            self.trackActivate.setEnabled(False)
            self.trackSidereal.setEnabled(False)
            self.trackSolar.setEnabled(False)
            self.trackLunar.setEnabled(False)
            self.trackCustom.setEnabled(False)
        if not self.scope.hasCustomTrackRate():
            self.trackCustom.setEnabled(False)
        if self.scope.canControlTrack():
            self.trackActivate.clicked.connect(self.scope.setTrackEnabled)
        self.slewSwitch = self.scope.getProperty('TELESCOPE_SLEW_RATE')
        self.slewIndex = dict()
        for speed, slew in [ (self.speedGuide, 'SLEW_GUIDE'), (self.speedCenter, 'SLEW_CENTERING'),\
            (self.speedFind, 'SLEW_FIND'), (self.speedSlew, 'SLEW_MAX')]:
            speedindex = 0
            for sw in self.slewSwitch.vp:
                #print(speedindex, sw)
                if sw == slew:
                    break
                speedindex += 1
            #print('connect', speed.text(), speedindex)
            speed.clicked.connect(lambda state, index=speedindex: self.setSlewSpeed(index))
            self.slewIndex[speedindex] = speed
            if slew == 'SLEW_FIND':
                self.setSlewSpeed(speedindex)
        if self.scope.canControlTrack():
            self.trackSwitch = self.scope.getProperty('TELESCOPE_TRACK_MODE')
            self.trackIndex = dict()
            for trackspeed, trackrate in [ (self.trackSidereal, 'TRACK_SIDEREAL'), (self.trackSolar, 'TRACK_SOLAR'),\
                (self.trackLunar, 'TRACK_LUNAR'), (self.trackCustom, 'TRACK_CUSTOM')]:
                trackindex = 0
                for sw in self.trackSwitch.vp:
                    #print(trackindex, sw)
                    if sw == trackrate:
                        break
                    trackindex += 1
                #print('connect', trackspeed.text(), trackindex)
                if trackindex < len(self.trackSwitch.vp):
                    trackspeed.clicked.connect(lambda state, index=trackindex: self.setTrackRate(index))
                    self.trackIndex[trackindex] = trackspeed
                    if trackrate == 'TRACK_SIDEREAL':
                        self.setTrackRate(trackindex)
                else:
                    trackspeed.setEnabled(False)
        self.RAUp.clicked.connect(lambda state: self.scope.MoveWE(TelescopeMotionWE.MOTION_EAST, \
            TelescopeMotionCommand.MOTION_START if state else TelescopeMotionCommand.MOTION_STOP))
        self.RADown.clicked.connect(lambda state: self.scope.MoveWE(TelescopeMotionWE.MOTION_WEST, \
            TelescopeMotionCommand.MOTION_START if state else TelescopeMotionCommand.MOTION_STOP))
        self.DECUp.clicked.connect(lambda state: self.scope.MoveNS(TelescopeMotionNS.MOTION_NORTH, \
            TelescopeMotionCommand.MOTION_START if state else TelescopeMotionCommand.MOTION_STOP))
        self.DECDown.clicked.connect(lambda state: self.scope.MoveNS(TelescopeMotionNS.MOTION_SOUTH, \
            TelescopeMotionCommand.MOTION_START if state else TelescopeMotionCommand.MOTION_STOP))
    def disconnect(self):
        if self.scope is None:
            return
        if self.scope.canControlTrack():
            self.trackActivate.clicked.disconnect()
        for speed in [ self.speedGuide, self.speedCenter,\
            self.speedFind, self.speedSlew]:
            speed.clicked.disconnect()
        for trackspeed in [self.trackSidereal, self.trackSolar,\
            self.trackLunar, self.trackCustom]:
            trackspeed.clicked.disconnect()
        self.RAUp.clicked.disconnect()
        self.RADown.clicked.disconnect()
        self.DECUp.clicked.disconnect()
        self.DECDown.clicked.disconnect()
        self.scope = None
    @pyqtSlot(QPushButton, int)
    def setSlewSpeed(self, index):
        #print('set slewspeed', button.text(), index)
        if index not in self.slewIndex:
            print('Unknown slew rate index')
            return
        self.speedGuide.setChecked(False)
        self.speedCenter.setChecked(False)
        self.speedFind.setChecked(False)
        self.speedSlew.setChecked(False)
        self.slewIndex[index].setChecked(True)
        self.scope.setSlewRate(index)
    @pyqtSlot(QPushButton, int)
    def setTrackRate(self, index):
        #print('set trackrate', button.text(), index)
        if index not in self.trackIndex:
            print('Unknown track rate index')
            return
        self.trackSidereal.setChecked(False)
        self.trackSolar.setChecked(False)
        self.trackLunar.setChecked(False)
        self.trackCustom.setChecked(False)
        self.trackIndex[index].setChecked(True)
        self.scope.setTrackMode(index)
    @pyqtSlot()
    def update(self):
        if self.scope.canControlTrack():
            trackindex = self.scope.getTrackMode()
            self.setTrackRate(trackindex)
        self.trackActivate.setChecked(self.scope.isTracking())
        slewindex = INDI.IUFindOnSwitchIndex(self.slewSwitch)
        self.setSlewSpeed(slewindex)

class mountHC(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.setStyleSheet('QFrame {background-color:"#301010";}')
        self.scope = None
    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.RA = DMSLLCD(parent=self, label='RA', width=13, value=None, angleformat=DMSLLCD.AngleFormat.HOURS_HMS)
        self.DEC = DMSLLCD(parent=self, label='DEC', width=13, value=None, angleformat=DMSLLCD.AngleFormat.DEGREES_DMS, anglerange=dms.AngleRanges.MINUSPI_TO_PI)
        self.AZ = DMSLLCD(parent=self, label='AZ', width=13, value=None, angleformat=DMSLLCD.AngleFormat.DEGREES_DMS)
        self.ALT = DMSLLCD(parent=self, label='ALT', width=13, value=None, angleformat=DMSLLCD.AngleFormat.DEGREES_DMS, anglerange=dms.AngleRanges.MINUSPI_TO_PI)
        self.layout.addWidget(self.RA)
        self.layout.addWidget(self.DEC)
        self.layout.addWidget(self.AZ)
        self.layout.addWidget(self.ALT)
        self.UTC = DMSLLCD(parent=self, label='UTC', width=13, value=None, angleformat=DMSLLCD.AngleFormat.HOURS_HMS)
        self.UTC.setPointSize(12)
        self.LST = DMSLLCD(parent=self, label='LST', width=13, value=None, angleformat=DMSLLCD.AngleFormat.HOURS_HMS)
        self.LST.setPointSize(12)
        self.timelayout = QHBoxLayout()
        self.timelayout.addWidget(self.UTC)
        self.timelayout.addWidget(self.LST)
        self.layout.addLayout(self.timelayout)
        self.LAT = DMSLLCD(parent=self, label='LAT', width=13, value=None, angleformat=DMSLLCD.AngleFormat.DEGREES_DMS, anglerange=dms.AngleRanges.MINUSPI_TO_PI)
        self.LAT.setPointSize(12)
        self.LON = DMSLLCD(parent=self, label='LON', width=13, value=None, angleformat=DMSLLCD.AngleFormat.DEGREES_DMS)
        self.LON.setPointSize(12)
        self.sitelayout = QHBoxLayout()
        self.sitelayout.addWidget(self.LAT)
        self.sitelayout.addWidget(self.LON)
        self.layout.addLayout(self.sitelayout)
        self.motion = mountMotionController(self)
        self.layout.addWidget(self.motion)
    def setActivated(self, activated):
        for lcd in [self.RA, self.DEC, self.AZ, self.ALT, self.UTC, self.LST, self.LAT, self.LON]:
            lcd.setActivated(activated)
        self.motion.setActivated(activated)
    def setCoord(self, skypoint):
        self.RA.setDMS(skypoint.ra())
        self.DEC.setDMS(skypoint.dec())
        self.AZ.setDMS(skypoint.az())
        self.ALT.setDMS(skypoint.alt())
    def setTelescope(self, gdi):
        if self.scope is not None:
            return
        self.scope = gdi
        self.setActivated(True)
        geo_coord = self.scope.getProperty('GEOGRAPHIC_COORD')
        self.lat = INDI.IUFindNumber(geo_coord, 'LAT')
        self.lon = INDI.IUFindNumber(geo_coord, 'LONG')
        self.LAT.setDMS(dms(self.lat.value))
        self.LON.setDMS(dms(self.lon.value))
        time_utc = self.scope.getProperty('TIME_UTC')
        self.utc = None
        if time_utc:
            self.utc = INDI.IUFindText(time_utc, 'UTC')
        #print(self.utc.text, INDI.f_scan_sexa(self.utc.text.split('T')[1]))
        if self.utc:
            self.UTC.setDMS(dms(INDI.f_scan_sexa(self.utc.text.split('T')[1])*15.0))
        time_lst = self.scope.getProperty('TIME_LST')
        self.lst = None
        if time_lst:
            self.lst = INDI.IUFindNumber(time_lst, 'LST')
        #print(self.lst.value)
        if self.lst:
            self.LST.setDMS(dms(self.lst.value*15.0))
        self.motion.makeConnections(self.scope)
        self.scope.newCoord.connect(self.setCoord)
    def removeTelescope(self):
        if self.scope is None:
            return
        self.motion.disconnect()
        self.scope.newCoord.disconnect(self.setCoord)
        self.setActivated(False)
        self.scope = None
    @pyqtSlot()
    def update(self):
        print('HC update')
        self.motion.update()
        self.LAT.setDMS(dms(self.lat.value))
        self.LON.setDMS(dms(self.lon.value))
        if self.utc:
            self.UTC.setDMS(dms(INDI.f_scan_sexa(self.utc.text.split('T')[1])*15.0))
        if self.lst:
            self.LST.setDMS(dms(self.lst.value*15.0))
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    mHC = mountHC()
    mHC.show()
    app.exec_()
