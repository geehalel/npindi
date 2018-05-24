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

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QDateTime, Qt, QFile, QIODevice, QDataStream

from indi.INDI import *
from indi.client.qt.indicommon import *

class ISD:
    class GDSetCommand(QObject):
        def __init__(self, inPropertyType, inProperty, inElement, qValue, parent):
            super().__init__(parent=parent)
            self.propType = inPropertyType
            self.indiProperty = inProperty
            self.indiElement = inElement
            self.elementValue = qValue
    class GDInterface(QObject):
        Connected = pyqtSignal()
        Disconnected = pyqtSignal()
        switchUpdated = pyqtSignal(IVectorProperty)
        textUpdated = pyqtSignal(IVectorProperty)
        numberUpdated = pyqtSignal(IVectorProperty)
        lightUpdated = pyqtSignal(IVectorProperty)
        BLOBUpdated = pyqtSignal(IBLOB)
        messageUpdated = pyqtSignal(int)
        propertyDefined = pyqtSignal(IVectorProperty)
        propertyDeleted = pyqtSignal(IVectorProperty)
        def __init__(self):
            super().__init__()
            self.dType = DeviceFamily.KSTARS_CCD
            self.properties = list()
        def registerProperty(self, prop):
            raise NotImplementedError("Class %s doesn't implement registerProperty(prop)" % (self.__class__.__name__))
        def removeProperty(self, prop):
            raise NotImplementedError("Class %s doesn't implement removeProperty(prop)" % (self.__class__.__name__))
        def processSwitch(self, svp):
            raise NotImplementedError("Class %s doesn't implement processSwitch(svp)" % (self.__class__.__name__))
        def processText(self, tvp):
            raise NotImplementedError("Class %s doesn't implement processText(tvp)" % (self.__class__.__name__))
        def processNumber(self, nvp):
            raise NotImplementedError("Class %s doesn't implement processNumber(nvp)" % (self.__class__.__name__))
        def processLight(self, lvp):
            raise NotImplementedError("Class %s doesn't implement processLight(lvp)" % (self.__class__.__name__))
        def processBLOB(self, bp):
            raise NotImplementedError("Class %s doesn't implement processBLOB(bp)" % (self.__class__.__name__))
        def processMessage(self, messageID):
            raise NotImplementedError("Class %s doesn't implement processMessage(messageID)" % (self.__class__.__name__))
        def getProperties(self):
            raise NotImplementedError("Class %s doesn't implement getProperties()" % (self.__class__.__name__))
        def getType(self):
            raise NotImplementedError("Class %s doesn't implement getType()" % (self.__class__.__name__))
        def getDriverInfo(self):
            raise NotImplementedError("Class %s doesn't implement getDriverInfo()" % (self.__class__.__name__))
        def getDeviceInfo(self):
            raise NotImplementedError("Class %s doesn't implement getDeviceInfo()" % (self.__class__.__name__))
        def setConfig(self, tConfig):
            raise NotImplementedError("Class %s doesn't implement setConfig(tConfig)" % (self.__class__.__name__))
        def getDeviceName(self):
            raise NotImplementedError("Class %s doesn't implement getDeviceName()" % (self.__class__.__name__))
        def isConnected(self):
            raise NotImplementedError("Class %s doesn't implement isConnected()" % (self.__class__.__name__))
        def getMinMaxStep(self, propName, elementName):
            raise NotImplementedError("Class %s doesn't implement getMinMaxStep(propName, elementName)" % (self.__class__.__name__))
        def getState(self):
            raise NotImplementedError("Class %s doesn't implement getState()" % (self.__class__.__name__))
        def getPermission(self):
            raise NotImplementedError("Class %s doesn't implement getPermission()" % (self.__class__.__name__))
        def getProperty(self):
            raise NotImplementedError("Class %s doesn't implement getProperty()" % (self.__class__.__name__))
        @pyqtSlot()
        def Connect(self):
            raise NotImplementedError("Class %s doesn't implement Connect()" % (self.__class__.__name__))
        @pyqtSlot()
        def Disconnect(self):
            raise NotImplementedError("Class %s doesn't implement Disconnect()" % (self.__class__.__name__))
        @pyqtSlot()
        def runCommand(self, command, ptr):
            raise NotImplementedError("Class %s doesn't implement runCommand(command, ptr)" % (self.__class__.__name__))
        @pyqtSlot()
        def setProperty(self, other):
            raise NotImplementedError("Class %s doesn't implement setProperty(other)" % (self.__class__.__name__))
    class GenericDevice(GDInterface):
        def __init__(self, idv):
            super().__init__()
            self.connected = False
            self.driverInfo = idv.getDriverInfo()
            self.deviceInfo = idv
            self.baseDevice = idv.getBaseDevice()
            self.clientManager = self.driverInfo.getClientManager()
            self.watchDogTimer = None
            self.BLOBFilename = ''
            self.dType = DeviceFamily.KSTARS_UNKNOWN
        def getType(self):
            return self.dType
        def getDriverInfo(self):
            return self.driverInfo
        def getDeviceInfo(self):
            return self.deviceInfo
        def getProperties(self):
            return self.properties
        def isConnected(self):
            return self.connected
        def getBaseDevice(self):
            return self. baseDevice
        def getDeviceName(self):
            return self.baseDevice.getDeviceName()
        def getState(self, propName):
            return self.baseDevice.getPropertyState(propName)
        def getPermission(self, propName):
            return self.baseDevice.getPropertyPermission(propName)
        def getProperty(self, propName):
            for oneProp in self.properties:
                if propName == oneProp.getName():
                    return oneProp
            return None
        def getMinMaxStep(self, propName, elementName):
            nvp = self.baseDevice.getNumber(propName)
            if nvp is None:
                return False
            np = INDI.IUFindNumber(nvp, elementName)
            if np is None:
                return False
            return np.min, np.max, np.step
        def registerProperty(self, prop):
            for pp in self.properties:
                if pp == prop:
                    return
            self.properties.append(prop)
            self.propertyDefined.emit(prop)
            if prop.getName() == 'CONNECTION':
                if prop.vp == None:
                    return
                if prop.s == INDI.IPState.IPS_BUSY:
                    return
                conSP = INDI.IUFindSwitch(prop, 'CONNECT')
                if conSP is None:
                    return
                if prop.s == INDI.IPState.IPS_OK and conSP.s == INDI.ISState.ISS_ON:
                    self.connected = True
                    self.Connected.emit()
                    self.createDeviceInit()
            if prop.getName() == 'TIME_UTC':
                if Options.Instance().value('npindi/useTimeUpdate'):
                    if Options.Instance().value('npindi/useComputerSource'):
                        if prop.vp is None: return
                        if prop.p != INDI.IPerm.IP_RO:
                            self.updateTime()
                    elif Options.Instance().value('npindi/useDeviceSource'):
                        tp = INDI.IUFindText(prop, 'UTC')
                        if tp is None: return
                        indiDateTime = QDateTime.fromString(tp.text, Qt.ISODate)
                        if indiDateTime.isNull() or not indiDateTime.isValid():
                            return
                        tp = INDI.IUFindText(prop, 'OFFSET')
                        if tp is None: return
                        try:
                            utcOffset = float(tp.text)
                        except:
                            QLoggingCategory.qCWarning(QLoggingCategory.NPINDI, 'Unable to convert UTC Offset: '+tp.text)
                        QLoggingCategory.qCInfo(QLoggingCategory.NPINDI, 'Setting UTC time from device '+self.getDeviceName() + ': '+indiDateTime.toString())
                        setINDIUtc(indiDateTime)
            elif prop.getName() == 'GEOGRAPHIC_COORD':
                if Options.Instance().value('npindi/useGeographicUpdate'):
                    if Options.Instance().value('npindi/useComputerSource'):
                        if prop.vp is None: return
                        if prop.p != INDI.IPerm.IP_RO:
                            self.updateLocation()
                    elif Options.Instance().value('npindi/useDeviceSource'):
                        latEle = INDI.IUFindNumber(prop, 'LAT')
                        lonEle = INDI.IUFindNumber(prop, 'LONG')
                        eleEle = INDI.IUFindNumber(prop, 'ELEV')
                        if latEle is not None and lonEle is not None and eleEle is not None:
                            QLoggingCategory.qCInfo(QLoggingCategory.NPINDI,'Setting geographic coords from device (lat,lon,ele)=('+str(latEle.value)+', '+str(lonEle.value)+','+str(eleEle.value)+')')
                            Options.Instance().setValue('location/latitude', latEle.value)
                            Options.Instance().setValue('location/longitude', lonEle.value)
                            Options.Instance().setValue('location/elevation', eleEle.value)
            # TODO WATCHDOG_HEARTBEAT
        def removeProperty(self, prop):
            self.properties.remove(prop)
            self.propertyDeleted.emit(prop)
        def processSwitch(self, prop):
            if prop.name == 'CONNECTION':
                if prop.s == INDI.IPState.IPS_BUSY:
                    return
                conSP = INDI.IUFindSwitch(prop, 'CONNECT')
                if conSP is None:
                    return
                if prop.s == INDI.IPState.IPS_OK and conSP.s == INDI.ISState.ISS_ON:
                    self.connected = True
                    self.Connected.emit()
                    self.createDeviceInit()
                    # TODO WATCHDOG_HEARTBEAT
                else:
                    self.connected = False
                    self.Disconnected.emit()
            self.switchUpdated.emit(prop)
        def processNumber(self, prop):
            if Options.Instance().value('npindi/useDeviceSource') and prop.name == 'GEOGRAPHIC_COORD' and prop.s == INDI.IPState.IPS_OK and Options.Instance().value('npindi/useGeographicUpdate'):
                latEle = INDI.IUFindNumber(prop, 'LAT')
                lonEle = INDI.IUFindNumber(prop, 'LONG')
                eleEle = INDI.IUFindNumber(prop, 'ELEV')
                if latEle is not None and lonEle is not None and eleEle is not None:
                    QLoggingCategory.qCInfo(QLoggingCategory.NPINDI,'Setting geographic coords from device (lat,lon,ele)=('+str(latEle.value)+', '+str(lonEle.value)+','+str(eleEle.value)+')')
                    Options.Instance().setValue('location/latitude', latEle.value)
                    Options.Instance().setValue('location/longitude', lonEle.value)
                    Options.Instance().setValue('location/elevation', eleEle.value)
            elif prop.name == 'WATCHDOG_HEARTBEAT':
                # TODO WATCHDOG_HEARTBEAT
                pass
            self.numberUpdated.emit(prop)
        def processText(self, prop):
            if Options.Instance().value('npindi/useDeviceSource') and prop.name == 'TIME_UTC' and prop.s == INDI.IPState.IPS_OK and Options.Instance().value('npindi/useTimeUpdate') and not isINDIUtcSynced():
                tp = INDI.IUFindText(prop, 'UTC')
                if tp is None: return
                indiDateTime = QDateTime.fromString(tp.text, Qt.ISODate)
                if indiDateTime.isNull() or not indiDateTime.isValid():
                    QLoggingCategory.qCWarning(QLoggingCategory.NPINDI, 'Unable to convert UTC DateTime: '+tp.text)
                    return
                tp = INDI.IUFindText(prop, 'OFFSET')
                if tp is None: return
                try:
                    utcOffset = float(tp.text)
                except:
                    QLoggingCategory.qCWarning(QLoggingCategory.NPINDI, 'Unable to convert UTC Offset: '+tp.text)
                QLoggingCategory.qCInfo(QLoggingCategory.NPINDI, 'Setting UTC time from device '+self.getDeviceName() +': '+ indiDateTime.toString())
                setINDIUtc(indiDateTime)
            self.textUpdated.emit(prop)
        def processLight(self, prop):
            self.lightUpdated.emit(prop)
        def processBLOB(self, bp):
            if bp.bvp.p == INDI.IPerm.IP_WO:
                return
            data_file = QFile()
            dataType = DATA_ASCII if bp.format == '.ascii' else DATA_OTHER
            currentDir = Options.Instance().value('npindi/fitsDir')
            if currentDir[-1] == '/':
                currentDir = currentDir[0:-1]
            filename = currentDir + '/'
            ts = QDateTime.currentDateTime().toString('yyyy-MM-ddThh-mm-ss')
            filename = bp.label + '_' + ts + bp.format.strip()
            bp.aux2 = filename[0:INDI.MAXINDIFILENAME]
            if dataType == DATA_ASCII:
                if bp.aux0 == None:
                    bp.aux0 = 0
                    ascii_data_file = QFile()
                    ascii_data_file.setFileName(filename)
                    if not ascii_data_file.open(QIODevice.WriteOnly):
                        QLoggingCategory.qCCritical(QLoggingCategory.NPINDI, 'GenericDevice Error: Unable to open '+ascii_data_file.fileName())
                        return
                    bp.aux1 = ascii_data_file
                data_file = bp.aux1
                out = QDataStream(data_file)
                nr, n =0, 0
                while nr < bp.size:
                    n = out.writeRawData(bp.blob[nr:], bp.size - nr)
                    nr += n
                out.writeRawData(b'\n', 1)
                data_file.flush()
            else:
                fits_temp_file = QFile(filename)
                if not fits_temp_file.open(QIODevice.WriteOnly):
                    QLoggingCategory.qCCritical(QLoggingCategory.NPINDI, 'GenericDevice Error: Unable to open ' + fits_temp_file.fileName())
                    return
                out = QDataStream(data_file)
                nr, n =0, 0
                while nr < bp.size:
                    n = out.writeRawData(bp.blob[nr:], bp.size - nr)
                    nr += n
                fits_temp_file.close()
                fmt = bp.format.lower().remove('.')
                # TODO imageviewer.py see PySide example
            self.BLOBUpdated.emit(bp)
        def setConfig(self, tConfig):
            svp = self.baseDevice.getSwitch('CONFIG_PROCESS')
            if svp is None:
                return False
            sp = None
            INDI.IUResetSwitch(svp)
            if tConfig == INDIConfig.LOAD_LAST_CONFIG:
                sp = INDI.IUFindSwitch(svp, 'CONFIG_LOAD')
                if sp is None:
                    return False
                INDI.IUResetSwitch(svp)
                sp.s = INDI.ISState.ISS_ON
            elif tConfig == INDIConfig.SAVE_CONFIG:
                sp = INDI.IUFindSwitch(svp, 'CONFIG_SAVE')
                if sp is None:
                    return False
                INDI.IUResetSwitch(svp)
                sp.s = INDI.ISState.ISS_ON
            elif tConfig == INDIConfig.LOAD_DEFAULT_CONFIG:
                sp = INDI.IUFindSwitch(svp, 'CONFIG_DEFAULT')
                if sp is None:
                    return False
                INDI.IUResetSwitch(svp)
                sp.s = INDI.ISState.ISS_ON
            self.clientManager.send_new_property(svp)
            return True
        def createDeviceInit(self):
            pass
        def updateTime(self):
            now = QDateTime.currentDateTimeUtc()
            offset = QDateTime.currentDateTime().offsetFromUtc() // 3600
            isoTS = now.toString(Qt.ISODate)[:-1]
            timeUTC= self.baseDevice.getText('TIME_UTC')
            if timeUTC:
                timeEle = INDI.IUFindText(timeUTC, 'UTC')
                if timeEle:
                    timeEle.text = isoTS
                offsetEle = INDI.IUFindText(timeUTC, 'OFFSET')
                if offsetEle:
                    offsetEle.text = str(offset)
                if timeEle and offsetEle:
                    self.clientManager.send_new_property(timeUTC)
        def updateLocation(self):
            locationNP = self.baseDevice.getNumber('GEOGRAPHIC_COORD')
            if locationNP is None:
                return
            latEle = INDI.IUFindNumber(locationNP, 'LAT')
            lonEle = INDI.IUFindNumber(locationNP, 'LONG')
            eleEle = INDI.IUFindNumber(locationNP, 'ELEV')
            if latEle is None or lonEle is None or eleEle is None:
                return
            latEle.value = Options.Instance().value('location/latitude')
            lonEle.value = Options.Instance().value('location/longitude')
            eleEle.value = Options.Instance().value('location/elevation')
            self.clientManager.send_new_property(locationNP)
        def Connect(self):
            return self.runCommand(DeviceCommand.INDI_CONNECT)
        def Disconnect(self):
            return self.runCommand(DeviceCommand.INDI_DISCONNECT)
        def runCommand( self, command, ptr = None):
            if command == DeviceCommand.INDI_CONNECT:
                self.clientManager.connect_device(self.baseDevice.getDeviceName())
            elif command == DeviceCommand.INDI_DISCONNECT:
                self.clientManager.disconnect_device(self.baseDevice.getDeviceName())
            else:
                pass # TO continue
        def setProperty(self, setPropCommand):
            if not isinstance(setPropCommand, GDSetCommand):
                raise ValueError('setProperty: setPropCommand is not a GDSetCommand')
            pp = self.baseDevice.getProperty(setPropCommand.indiProperty)
            if pp is None:
                return False
            if setPropCommand.propType == INDI.INDI_PROPERTY_TYPE.INDI_SWITCH:
                sp = INDI.IUFindSwitch(pp, setPropCommand.indiElement)
                if sp is None:
                    return False
                if pp.r == INDI.ISRule.ISR_1OFMANY or pp.r == INDI.ISRule.ISR_ATMOST1:
                    INDI.IUResetSwitch(pp)
                sp.s = INDI.ISState.ISS_OFF if setPropCommand.elementValue == 0 else INDI.ISState.ISS_ON
                self.clientManager.send_new_property(pp)
                return True
            elif setPropCommand.propType == INDI.INDI_PROPERTY_TYPE.INDI_NUMBER:
                np = INDI.IUFindNumber(pp, setPropCommand.indiElement)
                if np is None:
                    return False
                value = float(setPropCommand.elementValue)
                if np.value == value:
                    return True
                np.value = value
                self.clientManager.send_new_property(pp)
                return True
            # TODO other property types
            return True
        def resetWatchdog(self):
            pass
    class DeviceDecorator(GDInterface):
        def __init__(self, iPtr):
            super().__init__()
            self.interfacePtr = iPtr
            iPtr.Connected.connect(self.Connected)
            iPtr.Disconnected.connect(self.Disconnected)
            iPtr.propertyDefined.connect(self.propertyDefined)
            iPtr.propertyDeleted.connect(self.propertyDeleted)
            iPtr.messageUpdated.connect(self.messageUpdated)
            iPtr.switchUpdated.connect(self.switchUpdated)
            iPtr.numberUpdated.connect(self.numberUpdated)
            iPtr.textUpdated.connect(self.textUpdated)
            iPtr.BLOBUpdated.connect(self.BLOBUpdated)
            iPtr.lightUpdated.connect(self.lightUpdated)
            self.baseDevice = iPtr.getBaseDevice()
            self.clientManager = iPtr.getDriverInfo().getClientManager()
        def runCommand(self, command, ptr):
            return self.interfacePtr.runCommand(command, ptr)
        def setProperty(self, setPropCommand):
            self.interfacePtr.setProperty(setPropCommand)
        def processBLOB(self, bp):
            self.interfacePtr.processBLOB(bp)
        def processLight(self, lvp):
            self.interfacePtr.processLight(lvp)
        def processNumber(self, nvp):
            self.interfacePtr.processNumber(nvp)
        def processSwitch(self, svp):
            self.interfacePtr.processSwitch(svp)
        def processText(self, tvp):
            self.interfacePtr.processText(tvp)
        def processMessage(self, messageID):
            self.interfacePtr.processMessage(messageID)
        def registerProperty(self, prop):
            self.interfacePtr.registerProperty(prop)
        def removeProperty(self, prop):
            self.interfacePtr.removeProperty(prop)
        def setConfig(self, tConfig):
            self.interfacePtr.setConfig(tConfig)
        def getType(self):
            return self.interfacePtr.getType()
        def getDriverInfo(self):
            return self.interfacePtr.getDriverInfo()
        def getDeviceInfo(self):
            return self.interfacePtr.getDeviceInfo()
        def getDeviceName(self):
            return self.interfacePtr.getDeviceName()
        def getBaseDevice(self):
            return self.interfacePtr.getBaseDevice()
        def getProperties(self):
            return self.interfacePtr.getProperties()
        def getProperty(self, propName):
            return self.interfacePtr.getProperty(propName)
        def isConnected(self):
            return self.interfacePtr.isConnected()
        def Connect(self):
            return self.interfacePtr.Connect()
        def Disconnect(self):
            return self.interfacePtr.Disconnect()
        def getMinMaxStep(self, propName, elementName):
            return self.interfacePtr.getMinMaxStep(propName, elementName)
        def getState(self, propName):
            return self.interfacePtr.getState(propName)
        def getPermission(self, propName):
            return self.interfacePtr.getPermission(propName)
    class ST4:
        def __init__(self, bdv, cm):
            self.baseDevice = bdv
            self.clientManager = cm
            self.swapDEC = False
        def getDeviceName(self):
            return self.baseDevice.getDeviceName()
        def setDECSwap(self, enable):
            self.swapDEC = enable
        def doPulse(self, ra_dir, ra_msecs, dec_dir=None, dec_msecs=None):
            pass
