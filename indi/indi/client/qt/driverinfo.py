from PyQt5 import QtCore

from indi.client.qt.indicommon import *

class DriverInfo(QtCore.QObject):
    """
 DriverInfo holds all metadata associated with a particular INDI driver.
 An INDI drivers holds both static and dynamic information. Example for static information:
 <ul>
  <li>Device name.</li>
  <li>Device label.</li>
  <li>Driver version.</li>
  <li>Device Family: Telescope, CCD, Focuser...etc</li>

 Dynamic information include associated Server and Client managers, port in use, associated devices...etc.
 Most INDI drivers operate only one device, but some driver can present multiple devices simultaneously.

 Driver information are obtained from multiple sources:
 <ol>
  <li>INDI driver XML file: All INDI driver install an XML file (usually to /usr/share/indi) that contains information
  on the driver and device or devices it is capabale of running.</li>
  <li>Client DriverInfos: Users can add a new host/port combo in the Device Manager in order to connect to
  to local or remote INDI servers.</li>
  <li>Generated DriverInfos: DriverInfo can be created programatically to connect to local or remote INDI server with unknown
  number of actual drivers/devices at the server side.
 </ol>

 @author Jasem Mutlaq
    """
    #deviceStateChanged = QtCore.pyqtSignal(DriverInfo)
    deviceStateChanged = QtCore.pyqtSignal(QtCore.QObject)
    def __init__(self, inName=None, di=None):
        super().__init__()
        if inName and not di:
            self.name = inName
            self.hostname = 'localhost'
            self.port = '-1'
            self.userPort = '-1'
            self.treeLabel = None
            self.uniqueLabel = None
            self.driver = None
            self.version = None
            self.skelFile = None
            self.type = DeviceFamily.KSTARS_UNKNOWN
            self.serverState = False
            self.clientState = False
            self.driverSource = DriverSource.PRIMARY_XML
            self.serverManager = None
            self.clientManager = None
            self.auxInfo = dict()
            self.devices = list()
        if di and not inName:
            self.name = di.getName()
            self.treeLabel = di.getTreeLabel()
            self.uniqueLabel = di.getUniqueLabel()
            self.driver = di.getDriver()
            self.version = di.getVersion()
            self.userPort = di.getUserPort()
            self.skelFile = di.getSkeletonFile()
            self.port = di.getPort()
            self.hostname = di.getHost()
            self.type = di.getType()
            self.serverState = di.getServerState()
            self.clientState = di.getClientState()
            self.driverSource = di.getDriverSource()
            self.serverManager = di.getServerManager()
            self.clientManager = di.getClientManager()
            self.auxInfo = di.getAuxInfo()
            self.devices = di.getDevices()
        if (di and inName) or (not di and not inName):
            raise ValueError('DriverInfo: specify name or driver, and not both')
    def clone(self, resetClone=True):
        clone = DriverInfo(self)
        if resetClone:
            clone.reset()
            clone.resetDevices()
        return clone
    def reset(self):
        self.serverState = False
        self.clientState = False
        self.serverManager = None
        self.clientManager = None
    def resetDevices(self):
        self.devices.clear()
    def getServerBuffer(self):
        if serverManager is not None:
            return serverManager.getLogBuffer()
        return ''
    def isEmpty(self):
        return self.devices == []
    def getName(self):
        return self.name
    def setName(self, newName):
        self.name = newName
    def setTreeLabel(self, inTreeLabel):
        self.treeLabel = inTreeLabel
    def getTreeLabel(self):
        return self.treeLabel
    def setUniqueLabel(self, inUniqueLabel):
        if self.auxInfo.get('mdpd', False) == True or \
            self.driverSource == DriverSource.HOST_SOURCE:
            return
        self.uniqueLabel = inUniqueLabel
    def getUniqueLabel(self):
        return self.uniqueLabel
    def setDriver(self, newDriver):
        self.driver = newDriver
    def getDriver(self):
        return self.driver
    def setVersion(self, newVersion):
        self.version = newVersion
    def getVersion(self):
        return self.version
    def setType(self, newType):
        assert newType in DeviceFamily
        self.type = newType
    def getType(self):
        return self.type
    def setDriverSource(self, newDriverSource):
        assert newDriverSource in DriverSource
        self.driverSource = newDriverSource
    def getDriverSource(self):
        return self.driverSource
    def setServerManager(self, newServerManager):
        self.serverManager = newServerManager
    def getServerManager(self):
        return self.serverManager
    def setClientManager(self, newClientManager):
        self.clientManager = newClientManager
    def getClientManager(self):
        return self.clientManager
    def setUserPort(self, inUserPort):
        if inUserPort and inUserPort != '':
            self.userPort = inUserPort
        else:
            self.userPort = '-1'
    def getUserPort(self):
        return self.userPort
    def setSkeletonFile(self, inSkeleton):
        self.skelFile = inSkeleton
    def getSkeletonFile(self):
        return self.skelFile
    def setServerState(self, inState):
        if inState == self.serverState:
            return
        self.serverState = inState
        if self.serverState == False:
            self.serverManager = None
        self.deviceStateChanged.emit(self)
    def getServerState(self):
        return self.serverState
    def setClientState(self, inState):
        if inState == self.clientState:
            return
        self.clientState = inState
        if self.clientState == False:
            self.clientManager = None
        self.deviceStateChanged.emit(self)
    def getClientState(self):
        return self.clientState
    def setHostParameters(self, inHost, inPort):
        self.hostname = inHost
        self.port = inPort
    def setPort(self, inPort):
        self.port = inPort
    def getPort(self):
        return self.port
    def setHost(self, inHost):
        self.hostname = inHost
    def getHost(self):
        return self.hostname
    def addDevice(self, idv):
        self.devices.append(idv)
    def removeDevice(self, idv):
        self.devices.remove(idv)
    def getDevice(self, deviceName):
        for idv in self.devices:
            if idv.getBaseDevice().getDeviceName() == deviceName:
                return idv
        return None
    def getDevices(self):
        return self.devices
    def getAuxInfo(self):
        return self.auxInfo
    def setAuxInfo(self, value):
        self.auxInfo = value
    def addAuxInfo(self, key, value):
        self.auxInfo[key] = value

#DriverInfo.deviceStateChanged = QtCore.pyqtSignal(DriverInfo)
