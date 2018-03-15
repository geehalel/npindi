from PyQt5.QtCore import QObject#, QLoggingCategory

from indi.INDI import *
from indi.indibase.baseclientqt import BaseClientQt
from indi.indibase.basedevice import BaseDevice
from indi.client.qt.deviceinfo import DeviceInfo
from indi.client.qt.indicommon import *
from indi.client.qt.guimanager import GUIManager


class ClientManager(BaseClientQt):
    newINDIDevice=QtCore.pyqtSignal(DeviceInfo)
    removeINDIDevice=QtCore.pyqtSignal(DeviceInfo)
    newINDIProperty=QtCore.pyqtSignal(IVectorProperty)
    removeINDIProperty=QtCore.pyqtSignal(IVectorProperty)
    newINDIBLOB=QtCore.pyqtSignal(IBLOB)
    newINDISwitch=QtCore.pyqtSignal(IVectorProperty)
    newINDINumber=QtCore.pyqtSignal(IVectorProperty)
    newINDIText=QtCore.pyqtSignal(IVectorProperty)
    newINDILight=QtCore.pyqtSignal(IVectorProperty)
    newINDIMessage=QtCore.pyqtSignal(BaseDevice, int)
    newINDIUniversalMessage=QtCore.pyqtSignal(str)
    connectionSuccessful=QtCore.pyqtSignal()
    #connectionFailure=QtCore.pyqtSignal(ClientManager)
    connectionFailure=QtCore.pyqtSignal(QObject)
    def __init__(self):
        BaseClientQt.__init__(self, mediator=self)
        self.managedDrivers = list()
        self.sManager = None
    def isDriverManaged(self, di):
        return di in self.managedDrivers
    def appendManagedDriver(self, dv):
        self.managedDrivers.append(dv)
        dv.setClientManager(self)
        self.sManager = dv.getServerManager()
    def removeManagedDriver(self, dv):
        dv.setClientState(False)
        for di in dv.getDevices():
            #INDIListener::Instance()->removeDevice(di);
            GUIManager.Instance().removeDevice(di);
            dv.removeDevice(di)
        self.managedDrivers.remove(dv)
        if dv.getDriverSource() == DriverSource.GENERATED_SOURCE:
            del(dv)
    def getManagedDrivers(self):
        return self.managedDrivers
    def findDriverInfoByName(self, name):
        for dv in self.managedDrivers:
            if dv.getName() == name:
                return dv
        return None
    def driverInfoByLabel(self, label):
        for dv in self.managedDrivers:
            if dv.getTreeLabel() == label:
                return dv
        return None
    def new_device(self, dp):
        self.set_blob_mode(INDI.BLOBHandling.B_ALSO, dp, None)
        deviceDriver = None
        if not dp.name or dp.name == '':
            QLoggingCategory.qCWarning(QLoggingCategory.NPINDI, 'Received invalid device with empty name! Ignoring the device...')
        QLoggingCategory.qCDebug(QLoggingCategory.NPINDI, 'Received new device '+dp.name)
        for dv in self.managedDrivers:
            if dv.getUniqueLabel() == dp.name:
                deviceDriver = dv
                break
        if not deviceDriver:
            for dv in self.managedDrivers:
                dvName = dv.getName().split(' ')[0]
                if not dvName or dvName == '':
                    dvName = dv.getName()
                if dp.name.lower().startswith(dvName.lower()) or \
                  dv.getDriverSource() == DriverSource.HOST_SOURCE or \
                  dv.getDriverSource() == DriverSource.GENERATED_SOURCE:
                    deviceDriver = dv
                    break
        if not deviceDriver:
            return
        deviceDriver.setUniqueLabel(dp.name)
        devInfo = DeviceInfo(deviceDriver, dp)
        deviceDriver.addDevice(devInfo)
        self.newINDIDevice.emit(devInfo)
    def remove_device(self, dp):
        for driverInfo in self.managedDrivers:
            for deviceInfo in driverInfo.getDevices():
                if deviceInfo.getBaseDevice() == dp:
                    QLoggingCategory.qCDebug(QLoggingCategory.NPINDI, 'Removing device '+dp.name)
                    self.removeINDIDevice.emit(deviceInfo)
                    driverInfo.removeDevice(deviceInfo)
                    if driverInfo.isEmpty():
                        self.managedDrivers.remove(driverInfo)
                    return
    def new_property(self, prop):
        self.newINDIProperty.emit(prop)
    def remove_property(self, prop):
        self.removeINDIProperty.emit(prop)
    def new_blob(self, bp):
        self.newINDIBLOB.emit(bp)
    def new_switch(self, svp):
        self.newINDISwitch.emit(svp)
    def new_number(self, nvp):
        self.newINDINumber.emit(nvp)
    def new_text(self, tvp):
        self.newINDIText.emit(tvp)
    def new_light(self, lvp):
        self.newINDILight.emit(lvp)
    def new_message(self, dp, messageID):
        self.newINDIMessage.emit(dp, messageID)
    def new_universal_message(self, message):
        self.newINDIUniversalMessage.emit(message)
    def server_connected(self):
        QLoggingCategory.qCDebug(QLoggingCategory.NPINDI, 'INDI server connected')
        for device in self.managedDrivers:
            device.setClientState(True)
            if self.sManager is not None:
                device.setHostParameters(self.sManager.getHost(), self.sManager.getPort())
    def server_disconnected(self, exit_code):
        QLoggingCategory.qCDebug(QLoggingCategory.NPINDI, 'INDI server disconnected. Exit Code:{:d}'.format(exit_code))
        for device in self.managedDrivers:
            device.setClientState(False)
            device.reset()
        if exit_code < 0:
            self.connectionFailure.emit(self)
