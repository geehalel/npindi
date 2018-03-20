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

from PytQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from indi.INDI import *
from indi.client.qt.clientmanager import ClientManager
from indi.client.qt.deviceinfo import DeviceInfo
from indi.client.qt.indistd import *
indi_std = {
            "CONNECTION",
            "DEVICE_PORT",
            "TIME_UTC",
            "TIME_LST",
            "GEOGRAPHIC_COORD",
            "EQUATORIAL_COORD",
            "EQUATORIAL_EOD_COORD",
            "EQUATORIAL_EOD_COORD_REQUEST",
            "HORIZONTAL_COORD",
            "TELESCOPE_ABORT_MOTION",
            "ON_COORD_SET",
            "SOLAR_SYSTEM",
            "TELESCOPE_MOTION_NS",
            "TELESCOPE_MOTION_WE",
            "TELESCOPE_PARK",
            "DOME_PARK",
            "GPS_REFRESH",
            "WEATHER_STATUS",
            "CCD_EXPOSURE",
            "CCD_TEMPERATURE",
            "CCD_FRAME",
            "CCD_FRAME_TYPE",
            "CCD_BINNING",
            "CCD_INFO",
            "CCD_VIDEO_STREAM",
            "RAW_STREAM",
            "IMAGE_STREAM",
            "FOCUS_SPEED",
            "FOCUS_MOTION",
            "FOCUS_TIMER",
            "FILTER_SLOT",
            "WATCHDOG_HEARTBEAT",
            "CAP_PARK",
            "FLAT_LIGHT_CONTROL",
            "FLAT_LIGHT_INTENSITY"
            }

class IndiListener(QObject):
    newDevice = pyqtSignal(ISD.GDInterface)
    newTelescope = pyqtSignal(ISD.GDInterface)
    newCCD = pyqtSignal(ISD.GDInterface)
    newFilter = pyqtSignal(ISD.GDInterface)
    newFocuser = pyqtSignal(ISD.GDInterface)
    newDome = pyqtSignal(ISD.GDInterface)
    newWeather = pyqtSignal(ISD.GDInterface)
    newDustCap = pyqtSignal(ISD.GDInterface)
    newLightBox = pyqtSignal(ISD.GDInterface)
    newST4 = pyqtSignal(ISD.ST4)
    deviceRemoved = pyqtSignal(ISD.GDInterface)
    __instance = None
    def __new__(cls, parent):
        if IndiListener.__instance is None:
            IndiListener.__instance = QObject.__new__(cls)
        return IndiListener.__instance
    def __init__(self, parent):
        if IndiListener.__instance is not None: pass
        super().__init__(parent=parent)
        self.clients = list()
        self.devices = list()
        self.st4Devices = list()
    def isStandardProperty(self, name):
        return name in indi_std
    def getDevice(self, name):
        for gi in self.devices:
            if gi.getDeviceName() == name:
                return gi
        return None
