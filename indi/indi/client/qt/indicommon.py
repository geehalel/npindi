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

import enum
INDI_MAX_TRIES = 3
PROPERTY_LABEL_WIDTH = 100
ELEMENT_LABEL_WIDTH = 175
ELEMENT_READ_WIDTH = 175
ELEMENT_WRITE_WIDTH = 175
ELEMENT_FULL_WIDTH = 175
MIN_SET_WIDTH = 50
MAX_SET_WIDTH = 110
MED_INDI_FONT = 2
MAX_LABEL_LENGTH = 20
class DriverSource(enum.IntEnum):
    PRIMARY_XML = 0
    THIRD_PARTY_XML = 1
    EM_XML = 2
    HOST_SOURCE = 3
    GENERATED_SOURCE = 4
class ServerMode(enum.Enum):
    SERVER_CLIENT = 0
    SERVER_ONLY = 1
class PGui(enum.Enum):
    PG_NONE = 0
    PG_TEXT = 1
    PG_NUMERIC = 2
    PG_BUTTONS = 3
    PG_RADIO = 4
    PG_MENU = 5
    PG_LIGHTS = 6
    PG_BLOB = 7
class DeviceFamily(enum.Enum):
    """
    Devices families that we explicitly support (i.e. with std properties)
    """
    KSTARS_TELESCOPE = 0
    KSTARS_CCD = 1
    KSTARS_FILTER = 2
    KSTARS_VIDEO = 3
    KSTARS_FOCUSER = 4
    KSTARS_ROTATOR = 5
    KSTARS_DOME = 6
    KSTARS_ADAPTIVE_OPTICS = 7
    KSTARS_RECEIVERS = 8
    KSTARS_GPS = 9
    KSTARS_WEATHER = 10
    KSTARS_AUXILIARY = 11
    KSTARS_UNKNOWN = 12
class INDIConfig(enum.Enum):
    LOAD_LAST_CONFIG = 0
    SAVE_CONFIG = 1
    LOAD_DEFAULT_CONFIG = 2
class INDIDataType(enum.Enum):
    DATA_FITS = 0
    DATA_VIDEO = 1
    DATA_CCDPREVIEW = 2
    DATA_ASCII = 3
    DATA_OTHER = 4
class GuideDirection(enum.Enum):
    NO_DIR = 0
    RA_INC_DIR = 1
    RA_DEC_DIR = 2
    DEC_INC_DIR = 3
    DEC_DEC_DIR = 4
class DeviceCommand(enum.Enum):
    INDI_SEND_COORDS = 0
    INDI_ENGAGE_TRACKING = 1
    INDI_CENTER_LOCK = 2
    INDI_CENTER_UNLOCK = 3
    INDI_SET_PORT = 4
    INDI_CONNECT = 5
    INDI_DISCONNECT = 6
    INDI_SET_FILTER = 7
    INDI_SET_ROTATOR_TICKS = 8
    INDI_SET_ROTATOR_ANGLE = 9
class CCDFrameType(enum.Enum):
    FRAME_LIGHT = 0
    FRAME_BIAS = 1
    FRAME_DARK = 2
    FRAME_FLAT = 3
class CCDBinType(enum.Enum):
    SINGLE_BIN = 0
    DOUBLE_BIN = 1
    TRIPLE_BIN = 2
    QUADRUPLE_BIN = 3
##### npindi specific stuff #####
from PyQt5 import QtCore
# PyQt5 lacks QLoggingCategory
# QLoggingCategory.Q_LOGGING_CATEGORY(NPINDI, 'npindi')
class QLoggingCategory(enum.Enum):
    NPINDI = 'npindi'
    def qCCritical(cat, msg):
        QtCore.qCritical(cat.value+': '+msg)
    def qCDebug(cat, msg):
        QtCore.qDebug(cat.value+': '+msg)
    def qCInfo(cat, msg):
        #QtCore.qInfo(cat.value+': '+msg)
        QtCore.qDebug(cat.value+': '+msg)
    def qCWarning(cat, msg):
        QtCore.qWarning(cat.value+': '+msg)
# a simple square led
from PyQt5.QtWidgets import QFrame
class QLed(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self._mcolor = 'green'
        self.setStyleSheet('QFrame {background-color: '+self._mcolor+'}')
    def sizeHint(self):
        return QtCore.QSize(48, 48)
    def setColor(self, color):
        self._mcolor = color
        self.setStyleSheet('QFrame {background-color: '+self._mcolor+'}')
# Default getJD/getLST fonction
from PyQt5.QtCore import QDateTime, QDate, QTimer
import math
_INDIUtcDatetime = None
_INDIUtcTimer = None
_INDIUtcRefresh = 250
_INDIUtcSynced = False
def setINDIUtc(dt):
    global _INDIUtcDatetime, _INDIUtcTimer, _INDIUtcSynced
    QLoggingCategory.qCWarning(QLoggingCategory.NPINDI, 'INDI UTC Timer not implemented.  Local clock will be used.')
    _INDIUtcSynced = True
    return
    _INDIUtcDatetime = dt
    _INDIUtcTimer = QTimer()
    _INDIUtcTimer.setSingleShot(False)
    _INDIUtcTimer.setInterval(_INDIUtcRefresh)
    _INDIUtcTimer.timeout.connect(lambda : _INDIUtcDatetime.addMSecs(_INDIUtcRefresh))
    _INDIUtcTimer.start()
    _INDIUtcSynced = True
def resetINDIUtc():
    global _INDIUtcDatetime, _INDIUtcTimer, _INDIUtcSynced
    _INDIUtcDatetime = None
    _INDIUtcTimer.stop()
    _INDIUtcTimer.timeout.disconnect()
    _INDIUtcTimer = None
    _INDIUtcSynced = False
def isINDIUtcSynced():
    global _INDIUtcDatetime, _INDIUtcTimer, _INDIUtcSynced
    return _INDIUtcSynced
def getJD():
    global _INDIUtcDatetime, _INDIUtcTimer, _INDIUtcSynced
    if _INDIUtcDatetime is None:
        now = QDateTime.currentDateTimeUtc()
    else:
        now = _INDIUtcDatetime.toUTC()
    jd0 = now.date().toJulianDay() - 0.5
    h = now.time().msecsSinceStartOfDay() / (3600 * 1000)
    jd = jd0 + h / 24.0
    return jd
def getGAST():
    global _INDIUtcDatetime, _INDIUtcTimer, _INDIUtcSynced
    # using approximation from http://aa.usno.navy.mil/faq/docs/GAST.php
    if _INDIUtcDatetime is None:
        now = QDateTime.currentDateTimeUtc()
    else:
        now = _INDIUtcDatetime.toUTC()
    jd0 = now.date().toJulianDay() - 0.5
    h = now.time().msecsSinceStartOfDay() / (3600 * 1000)
    jd = jd0 + h / 24.0
    d = jd - 2451545.0
    d0 = jd0 - 2451545.0
    t = d / 36525
    gmst = 6.697374558 + 0.06570982441908 * d0 + 1.00273790935 * h + 0.000026 * (t * t)
    omega = 125.04 - 0.052954 * d
    l = 280.47 + 0.98565 * d
    epsilon = 23.4394 - 0.0000004 * d
    nutlon = -0.000319 * math.sin(math.radians(omega)) - 0.000024 * math.sin(math.radians(2 * l))
    eqeq = nutlon * math.cos(math.radians(epsilon))
    gast = gmst + eqeq
    while gast < 0.0:
        gast += 24.0
    while gast >= 24.0:
        gast -= 24.0
    return gast
# Config/Settings, derived from kstars::Options
from PyQt5.QtCore import QSettings, QDir
class Options(QSettings):
    __instance = None
    def __new__(cls, parent):
        if Options.__instance is None:
            Options.__instance = QSettings.__new__(cls)
        return Options.__instance
    def __init__(self, parent):
        if Options.__instance is not None: pass
        super().__init__(parent=parent)
        self.beginGroup('npindi')
        self.setValue('useComputerSource', False)
        self.setValue('useDeviceSource', True)
        self.setValue('useTimeUpdate', True)
        self.setValue('useGeographicUpdate', True)
        self.setValue('useRefraction', False)
        self.setValue('fitsDir', QDir.homePath())
        self.endGroup()
        self.beginGroup('location')
        self.setValue('latitude', 50.3)
        self.setValue('longitude', 123.4)
        self.setValue('elevation', 132)
        self.endGroup()
    @classmethod
    def Instance(cls):
        if Options.__instance is None:
            Options.__instance = Options(parent=None)
        return Options.__instance
from PyQt5.QtWidgets import QCheckBox, QGroupBox, QFrame, QLineEdit, QMessageBox, QSizePolicy, QPushButton, QLayout, QGridLayout, QVBoxLayout, QHBoxLayout, QLCDNumber, QLabel
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtCore import QLocale
class ui_Options(QFrame):
    def __init__(self, parent=None, settings=Options.Instance()):
        super().__init__(parent)
        self.settings = settings
        self.initUI(parent)
    def setTextOption(self, key, widget):
        #print('setting text option for', key, 'value', widget)
        self.settings.setValue(key, widget.text())
    def setFloatOption(self, key, widget):
        locale = QLocale()
        #print('setting float option for', key, 'value', widget)
        self.settings.setValue(key, locale.toDouble(widget.text()))
    def setIntOption(self, key, widget):
        locale = QLocale()
        #print('setting int option for', key, 'value', widget)
        self.settings.setValue(key, locale.toInt(widget.text()))
    def setBoolOption(self, key, widget, state):
        #print('setting bool option for', key, 'value', widget)
        self.settings.setValue(key, False if state==0 else True)
    def initUI(self, parent=None):
        locale = QLocale()
        if parent is not None and parent.layout() is not None:
            layout = parent.layout()
        else:
            layout = QVBoxLayout(parent if parent is not None else self)
        for k in self.settings.childKeys():
            hboxlayout = QHBoxLayout()
            label = QLabel(k)
            hboxlayout.addWidget(label)
            value = self.settings.value(k)
            valuewidget = None
            if isinstance(value, str):
                valuewidget = QLineEdit(value)
                valuewidget.editingFinished.connect(lambda key=self.settings.group()+'/'+k, widget=valuewidget: self.setTextOption(key, widget))
            elif isinstance(value, float):
                valuewidget = QLineEdit(locale.toString(value))
                valuewidget.setValidator(QDoubleValidator())
                valuewidget.editingFinished.connect(lambda key=self.settings.group()+'/'+k, widget=valuewidget: self.setFloatOption(key, widget))
            elif isinstance(value, int) and not isinstance(value, bool):
                valuewidget = QLineEdit(locale.toString(value))
                valuewidget.setValidator(QIntValidator())
                valuewidget.editingFinished.connect(lambda key=self.settings.group()+'/'+k, widget=valuewidget: self.setIntOption(key, widget))
            elif isinstance(value, bool):
                valuewidget = QCheckBox()
                valuewidget.setChecked(value)
                valuewidget.stateChanged.connect(lambda state, key=self.settings.group()+'/'+k, widget=valuewidget: self.setBoolOption(key, widget, state))
            if valuewidget is not None:
                hboxlayout.addWidget(valuewidget)
            layout.addLayout(hboxlayout)
        for g in self.settings.childGroups():
            groupbox = QGroupBox(g)
            layout.addWidget(groupbox)
            self.settings.beginGroup(g)
            self.initUI(parent=groupbox)
            self.settings.endGroup()
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    optui = ui_Options()
    optui.show()
    app.exec_()
    for key in Options.Instance().allKeys():
        print(key, Options.Instance().value(key))
