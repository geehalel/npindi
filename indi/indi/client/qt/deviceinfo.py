from indi.indibase.basedevice import BaseDevice
from indi.client.qt.driverinfo import DriverInfo

class DeviceInfo:
    def __init__(self, parent, ibd):
        self.drv = parent
        self.dp = ibd
    def getDriverInfo(self):
        return self.drv
    def getBaseDevice(self):
        return self.dp
