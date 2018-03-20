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

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from indi.INDI import *
from indi.client.qt.clientmanager import *
from indi.client.qt.deviceinfo import DeviceInfo
from indi.client.qt.indistd import *

from indi.client.qt.inditelescope import Telescope

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

class INDIListener(QObject):
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
        if INDIListener.__instance is None:
            INDIListener.__instance = QObject.__new__(cls)
        return INDIListener.__instance
    def __init__(self, parent):
        if INDIListener.__instance is not None: pass
        super().__init__(parent=parent)
        self.clients = list()
        self.devices = list()
        self.st4Devices = list()
    @classmethod
    def Instance(cls):
        if INDIListener.__instance is None:
            INDIListener.__instance = INDIListener(parent=None)
        return INDIListener.__instance
    def isStandardProperty(self, name):
        return name in indi_std
    def getDevice(self, name):
        for gi in self.devices:
            if gi.getDeviceName() == name:
                return gi
        return None
    def getDevices(self):
        return self.devices
    def size(self):
        return len(self.devices)
    def addClient(self, cm):
        QLoggingCategory.qCDebug(QLoggingCategory.NPINDI, 'INDIListener: Adding a new client manager to INDI Listener')
        self.clients.append(cm)
        cm.newINDIDevice.connect(self.processDevice)
        cm.removeINDIDevice.connect(self.removeDevice)
        cm.newINDIProperty.connect(self.registerProperty)
        cm.removeINDIProperty.connect(self.removeProperty)
        cm.newINDISwitch.connect(self.processSwitch)
        cm.newINDIText.connect(self.processText)
        cm.newINDINumber.connect(self.processNumber)
        cm.newINDILight.connect(self.processLight)
        cm.newINDIBLOB.connect(self.processBLOB)
        cm.newINDIUniversalMessage.connect(self.processUniversalMessage)
    def removeClient(self, cm):
        QLoggingCategory.qCDebug(QLoggingCategory.NPINDI, 'INDIListener: Removing client manager for server '+cm.getHost().decode('ascii')+'@'+str(cm.getPort()))
        self.clients.remove(cm)
        it = 0
        while it < len(self.devices):
            dv = self.devices[it].getDriverInfo()
            hostSource = dv.getDriverSource() == DriverSource.HOST_SOURCE or dv.getDriverSource() == DriverSource.GENERATED_SOURCE
            if cm.isDriverManaged(dv):
                if dv.getAuxInfo().get('mdpd', False) is True:
                    while it < len(self.devices):
                        if dv.getDevice(self.devices[it].getDeviceName()) is not None:
                            del(self.devices[it])
                        else:
                            break
                else:
                    del(self.devices[it])
                cm.removeManagedDriver(dv)
                cm.disconnect(self)
                if hostSource:
                    return
            else:
                it = it + 1
    def processDevice(self, dv):
        QLoggingCategory.qCDebug(QLoggingCategory.NPINDI, 'INDIListener: New device ' + dv.getBaseDevice().getDeviceName())
        gd = ISD.GenericDevice(dv)
        self.devices.append(gd)
        self.newDevice.emit(gd)
    def removeDevice(self, dv):
        QLoggingCategory.qCDebug(QLoggingCategory.NPINDI, 'INDIListener: Removing device ' + dv.getBaseDevice().getDeviceName() +\
          'with ubique label ' + dv.getDriverInfo().getUniqueLabel())
        for gd in self.devices:
            if gd.getDeviceInfo() == dv:
                self.deviceRemoved.emit(gd)
                self.devices.remove(gd)
                del(gd)
    def registerProperty(self, prop):
        QLoggingCategory.qCDebug(QLoggingCategory.NPINDI, '<'+prop.getDeviceName()+'>: <'+prop.getName()+'>')
        pname = prop.getName()
        pdname = prop.getDeviceName()
        for gd in self.devices:
            if gd.getType() == DeviceFamily.KSTARS_UNKNOWN and pname in {'EQUATORIAL_EOD_COORD', 'HORIZONTAL_COORD'}:
                self.devices.remove(gd)
                gd = Telescope(gd)
                self.devices.append(gd)
                QLoggingCategory.qCDebug(QLoggingCategory.NPINDI, '<'+prop.getDeviceName()+'> is a ' + str(type(gd)))
                self.newTelescope.emit(gd)
            gd.registerProperty(prop)
            break
    def removeProperty(self, prop):
        if prop is None: return
        for gd in self.devices:
            if gd.getDeviceName() == prop.getDeviceName():
                gd.removeProperty(prop)
                return
    def processSwitch(self, svp):
        for gd in self.devices:
            if gd.getDeviceName() == svp.device:
                gd.processSwitch(svp)
                break
    def processNumber(self, nvp):
        for gd in self.devices:
            if gd.getDeviceName() == nvp.device:
                gd.processNumber(nvp)
                break
    def processText(self, tvp):
        for gd in self.devices:
            if gd.getDeviceName() == tvp.device:
                gd.processText(tvp)
                break
    def processLight(self, lvp):
        for gd in self.devices:
            if gd.getDeviceName() == lvp.device:
                gd.processLight(lvp)
                break
    def processBLOB(self, bp):
        for gd in self.devices:
            if gd.getDeviceName() == bp.vp.device:
                gd.processBLOB(bp)
                break
    def processMessage(self, dp, messageID):
        for gd in self.devices:
            if gd.getDeviceName() == dp.getDeviceName():
                gd.processMessage(messageID)
                break
    def processUniversalMessage(self, message):
        QLoggingCategory.qCInfo(QLoggingCategory.NPINDI, message+' (INDI)')
