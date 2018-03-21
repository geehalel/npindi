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
# Default getLST fonction
from PyQt5.QtCore import QDateTime
def getLST():
    return 0.0
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
        self.setValue('useComputerSource', True)
        self.setValue('useDeviceSource', True)
        self.setValue('useTimeUpdate', True)
        self.setValue('useGeographicUpdate', True)
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
