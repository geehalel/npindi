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
