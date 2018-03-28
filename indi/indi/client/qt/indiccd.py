from PyQt5.QtCore import pyqtSignal, pyqtSlot, QStandardPaths, QDir, QTemporaryFile, QDataStream, QDateTime, QFile, QIODevice
from PyQt5.Qt import QImageReader
from indi.client.qt.indicommon import *
from indi.client.qt.indistd import *
from indi.INDI import *

import enum
import math

class CCDChip:
    class ChipType(enum.Enum):
        PRIMARY_CCD = 0
        GUIDE_CCD = 1
    def __init__(self, ccd, cType):
        self.parentCCD = ccd
        self.type = cType
        self.baseDevice = ccd.getBaseDevice()
        self.clientManager = ccd.getDriverInfo().getClientManager()
        self.batchMode = False
        self.frameTypes = list()
        self.canBin = False
        self.canSubFrame = False
        self.canAbort = False
    def getType(self):
        return self.type
    def getCCD(self):
        return self.parentCCD
    def isBatchMode(self):
        return self.batchMode
    def setBatchMode(self, enable):
        self.batchMode = enable
    def getFrameTypes(self):
        return self.frameTypes
    def addFrameLabel(self, label):
        self.frameTypes.append(label)
    def clearFrameTypes(self):
        self.frameTypes.clear()
    def getFrameMinMax(self):
        frameProp = None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            frameProp = self.baseDevice.getNumber('CCD_FRAME')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            frameProp = self.baseDevice.getNumber('GUIDER_FRAME')
        if frameProp is None:
            return None
        arg = INDI.IUFindNumber(frameProp, 'X')
        if arg is None:
            return None
        minX, maxX = arg.min, arg.max
        arg = INDI.IUFindNumber(frameProp, 'Y')
        if arg is None:
            return None
        minY, maxY = arg.min, arg.max
        arg = INDI.IUFindNumber(frameProp, 'W')
        if arg is None:
            return None
        minW, maxW = arg.min, arg.max
        arg = INDI.IUFindNumber(frameProp, 'H')
        if arg is None:
            return None
        minH, maxH = arg.min, arg.max
        return ((minX, maxX), (minY, maxY), (minW, maxW), (minH, maxH))
    def setImageInfo(self, width, height, pixelX, pixelY, bitdepth):
        ccdInfoProp=None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            ccdInfoProp = self.baseDevice.getNumber('CCD_INFO')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            ccdInfoProp = self.baseDevice.getNumber('GUIDER_INFO')
        if ccdInfoProp is None:
            return False
        ccdInfoProp.vp['CCD_MAX_X'] = width
        ccdInfoProp.vp['CCD_MAX_Y'] = height
        ccdInfoProp.vp['CCD_PIXEL_SIZE'] = math.hypot(pixelX, pixelY)
        ccdInfoProp.vp['CCD_PIXEL_SIZE_X'] = pixelX
        ccdInfoProp.vp['CCD_PIXEL_SIZE_Y'] = pixelY
        ccdInfoProp.vp['CCD_BITSPERPIXEL'] = bitdepth
        self.clientManager.send_new_property(ccdInfoProp)
        return True
    def getPixelSize(self):
        ccdInfoProp=None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            ccdInfoProp = self.baseDevice.getNumber('CCD_INFO')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            ccdInfoProp = self.baseDevice.getNumber('GUIDER_INFO')
        if ccdInfoProp is None:
            return False
        pixelX = INDI.IUFindNumber(ccdInfoProp, 'CCD_PIXEL_SIZE_X')
        pixelY = INDI.IUFindNumber(ccdInfoProp, 'CCD_PIXEL_SIZE_Y')
        if pixelX is None or pixelY is None:
            return None
        return (pixelX.value, pixelY.value)
    def getFrame(self):
        frameProp = None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            frameProp = self.baseDevice.getNumber('CCD_FRAME')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            frameProp = self.baseDevice.getNumber('GUIDER_FRAME')
        if frameProp is None:
            return None
        arg = INDI.IUFindNumber(frameProp, 'X')
        if arg is None:
            return None
        x = arg.value
        arg = INDI.IUFindNumber(frameProp, 'Y')
        if arg is None:
            return None
        y = arg.value
        arg = INDI.IUFindNumber(frameProp, 'W')
        if arg is None:
            return None
        w = arg.value
        arg = INDI.IUFindNumber(frameProp, 'H')
        if arg is None:
            return None
        h = arg.value
        return (x, y, w ,h)
    def resetFrame(self):
        frameProp = None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            frameProp = self.baseDevice.getNumber('CCD_FRAME')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            frameProp = self.baseDevice.getNumber('GUIDER_FRAME')
        if frameProp is None:
            return None
        xarg = INDI.IUFindNumber(frameProp, 'X')
        yarg = INDI.IUFindNumber(frameProp, 'Y')
        warg = INDI.IUFindNumber(frameProp, 'W')
        harg = INDI.IUFindNumber(frameProp, 'H')
        if xarg is not None and yarg is not None and warg is not None and harg is not None:
            if xarg.value == xarg.min and yarg.value == yarg.min and warg.value == warg.max and harg.value == harg.max:
                return False
            xarg.value = xarg.min
            yarg.value = yarg.min
            warg.value = warg.max
            harg.value = harg.max
            self.clientManager.send_new_property(frameProp)
            return True
        return False
    def setFrame(self, x, y, w, h):
        frameProp = None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            frameProp = self.baseDevice.getNumber('CCD_FRAME')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            frameProp = self.baseDevice.getNumber('GUIDER_FRAME')
        if frameProp is None:
            return None
        xarg = INDI.IUFindNumber(frameProp, 'X')
        yarg = INDI.IUFindNumber(frameProp, 'Y')
        warg = INDI.IUFindNumber(frameProp, 'W')
        harg = INDI.IUFindNumber(frameProp, 'H')
        if xarg is not None and yarg is not None and warg is not None and harg is not None:
            if xarg.value == x and yarg.value == y and warg.value == w and harg.value == h:
                return True
            xarg.value = x
            yarg.value = y
            warg.value = w
            harg.value = h
            self.clientManager.send_new_property(frameProp)
            return True
        return False
    def capture(self, exposure):
        expProp = None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            expProp = self.baseDevice.getNumber('CCD_EXPOSURE')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            expProp = self.baseDevice.getNumber('GUIDER_EXPOSURE')
        if expProp is None:
            return False
        expProp.vp['CCD_EXPOSURE_VALUE'].value = exposure
        self.clientManager.send_new_property(expProp)
        return True
    def abortExposure(self):
        abortProp = None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            abortProp = self.baseDevice.getNumber('CCD_ABORT_EXPOSURE')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            abortProp = self.baseDevice.getNumber('GUIDER_ABORT_EXPOSURE')
        if abortProp is None:
            return False
        abort = INDI.IUFindSwitch(abortProp, 'ABORT')
        if abort is None:
            return False
        abort.s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(abortProp)
        return True
    def canBin(self):
        return self.canBin
    def setCanBin(self, value):
        self.canBin = value
    def canSubFrame(self):
        return self.canSubFrame
    def setCanSubFrame(self, value):
        self.canSubFrame = value
    def canAbort(self):
        return self.canAbort
    def setCanAbort(self, value):
        self.canAbort = value
    def getISOIndex(self):
        isoProp = self.baseDevice.getSwitch('CCD_ISO')
        if isoProp is None:
            return -1
        return INDI.IUFindOnSwitchIndex(isoProp)
    def setISOIndex(self, value):
        isoProp = self.baseDevice.getSwitch('CCD_ISO')
        if isoProp is None:
            return None
        INDI.IUResetSwitch(isoProp)
        list(isoProp.vp.values())[value].s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(isoProp)
    def getISOList(self):
        isoList = list()
        isoProp = self.baseDevice.getSwitch('CCD_ISO')
        if isoProp is None:
            return isoList
        for isoKey in isoProp.vp:
            isoList.append(isoProp[isoKey].label)
        return isoList
    def isCapturing(self):
        expProp = None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            expProp = self.baseDevice.getNumber('CCD_EXPOSURE')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            expProp = self.baseDevice.getNumber('GUIDER_EXPOSURE')
        if expProp is None:
            return False
        return expProp.s == INDI.IPState.IPS_BUSY
    def setFrameType(self, nameortype):
        fType = CCDFrameType.FRAME_LIGHT
        if isinstance(nameortype, str):
            if name == 'FRAME_LIGHT' or name == 'Light':
                fType = CCDFrameType.FRAME_LIGHT
            elif name == 'FRAME_DARK' or name == 'Dark':
                fType = CCDFrameType.FRAME_DARK
            elif name == 'FRAME_BIAS' or name == 'Bias':
                fType = CCDFrameType.FRAME_BIAS
            elif name == 'FRAME_FLAT' or name == 'Flat':
                fType = CCDFrameType.FRAME_FLAT
            else:
                QLoggingCategory.qCWarning(QLoggingCategory.NPINDI, str(nameortype) + ' frame type is unknown')
                return False
        elif not isinstance(nameortype, CCDFrameType):
            raise ValueError('setFrameType: parameter should be a CCDFrameType')
        frameProp = None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            frameProp = self.baseDevice.getSwitch('CCD_FRAME_TYPE')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            frameProp = self.baseDevice.getNumber('GUIDER_FRAME_TYPE')
        if frameProp is None:
            return False
        if fType == CCDFrameType.FRAME_LIGHT:
            ccdFrame = INDI.IUFindSwitch(frameProp, 'FRAME_LIGHT')
        elif fType == CCDFrameType.FRAME_DARK:
            ccdFrame = INDI.IUFindSwitch(frameProp, 'FRAME_DARK')
        elif fType == CCDFrameType.FRAME_BIAS:
            ccdFrame = INDI.IUFindSwitch(frameProp, 'FRAME_BIAS')
        elif fType == CCDFrameType.FRAME_FLAT:
            ccdFrame = INDI.IUFindSwitch(frameProp, 'FRAME_FLAT')
        if ccdFrame is None:
            return False
        if ccdFrame.s == INDI.ISState.ISS_ON:
            return True
        INDI.IUResetSwitch(frameProp)
        ccdFrame.s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(frameProp)
        return True
    def setBinningType(self, bintype):
        if not isinstance(bintype, CCDBinType):
            raise ValueError('setFrameType: parameter should be a CCDBinType')
        if bintype == CCDBinType.SINGLE_BIN:
            return setBinning(1, 1)
        elif bintype == CCDBinType.DOUBLE_BIN:
            return setBinning(2, 2)
        elif bintype == CCDBinType.TRIPLE_BIN:
            return setBinning(3, 3)
        elif bintype == CCDBinType.QUADRUPLE_BIN:
            return setBinning(4, 4)
        return False
    def getBinningType(self):
        binType = CCDBinType.SINGLE_BIN
        binProp = None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            binProp = self.baseDevice.getSwitch('CCD_BINNING')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            frameProp = self.baseDevice.getNumber('GUIDER_BINNING')
        if binProp is None:
            return binType
        horBin = INDI.IUFindNumber(binProp, 'HOR_BIN')
        verBin = INDI.IUFindNumber(binProp, 'VER_BIN')
        if horBin is None or verBin is None:
            return binType
        if horBin.value == 2:
            binType = CCDBinType.DOUBLE_BIN
        elif horBin.value == 3:
            binType = CCDBinType.TRIPLE_BIN
        elif horBin.value == 4:
            binType = CCDBinType.QUADRUPLE_BIN
        return binType
    def setBinning(self, bin_x, bin_y):
        binProp = None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            binProp = self.baseDevice.getSwitch('CCD_BINNING')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            frameProp = self.baseDevice.getNumber('GUIDER_BINNING')
        if binProp is None:
            return False
        horBin = INDI.IUFindNumber(binProp, 'HOR_BIN')
        verBin = INDI.IUFindNumber(binProp, 'VER_BIN')
        if horBin is None or verBin is None:
            return False
        if horBin.value == bin_x and verBin.value == bin_y:
            return True
        if bin_x > horBin.max or bin_y > verBin.max:
            return False
        horBin.value = bin_x
        verBin.value = bin_y
        self.clientManager.send_new_property(binProp)
        return True
    def getBinning(self):
        binProp = None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            binProp = self.baseDevice.getSwitch('CCD_BINNING')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            frameProp = self.baseDevice.getNumber('GUIDER_BINNING')
        if binProp is None:
            return None
        horBin = INDI.IUFindNumber(binProp, 'HOR_BIN')
        verBin = INDI.IUFindNumber(binProp, 'VER_BIN')
        if horBin is None or verBin is None:
            return None
        return (horBin.value, verBin.value)
    def getMaxBin(self):
        binProp = None
        if self.type == CCDChip.ChipType.PRIMARY_CCD:
            binProp = self.baseDevice.getSwitch('CCD_BINNING')
        elif self.type == CCDChip.ChipType.GUIDE_CCD:
            frameProp = self.baseDevice.getNumber('GUIDER_BINNING')
        if binProp is None:
            return None
        horBin = INDI.IUFindNumber(binProp, 'HOR_BIN')
        verBin = INDI.IUFindNumber(binProp, 'VER_BIN')
        if horBin is None or verBin is None:
            return None
        return (horBin.max, verBin.max)
class CCD(ISD.DeviceDecorator):
    newTemperatureValue = pyqtSignal(float)
    newExposureValue = pyqtSignal(float)
    newGuideStarData = pyqtSignal(CCDChip, float, float, float)
    newRemoteFile = pyqtSignal(str)
    videoStreamToggled = pyqtSignal(bool)
    videoRecordToggled = pyqtSignal(bool)
    newFPS = pyqtSignal(float)
    newVideoFrame = pyqtSignal(IBLOB)
    class UploadMode(enum.Enum):
        UPLOAD_CLIENT = 0
        UPLOAD_LOCAL = 1
        UPLOAD_BOTH = 2
    class TransferFormat(enum.Enum):
        FORMAT_FITS = 0
        FORMAT_NATIVE = 1
    class BlobType(enum.Enum):
        BLOB_IMAGE = 0
        BLOB_FITS = 1
        BLOB_RAW = 2
        BLOB_OTHER = 3
    class TelescopeType(enum.Enum):
        TELESCOPE_PRIMARY = 0
        TELESCOPE_GUIDE = 1
        TELESCOPE_UNKNOWN = 2
    RAWFormats = ['cr2', 'crw', 'nef', 'raf', 'dng', 'arw']
    def __init__(self, iPtr):
        super().__init__(iPtr)
        self.dType = DeviceFamily.KSTARS_CCD
        self.baseDevice = iPtr.getBaseDevice()
        self.clientManager = iPtr.getDriverInfo().getClientManager()
        self.filter = None
        self.ISOMode = True
        self.HasGuideHead = False
        self.HasCooler = False
        self.HasCoolerControl = False
        self.HasVideoStream = False
        self.IsLooping = False
        self.seqPrefix = None
        self.fitsDir = None
        self.BLOBFilename = None
        self.nextSequenceID = 0
        self.streamW = 0
        self.streamH = 0
        self.primaryChip = None
        self.guideChip = None
        self.transferFormat = CCD.TransferFormat.FORMAT_FITS
        self.targetTransferFormat = CCD.TransferFormat.FORMAT_FITS
        self.telescopeType = CCD.TelescopeType.TELESCOPE_UNKNOWN
        self.gainN = None
        self.primaryChip = CCDChip(self, CCDChip.ChipType.PRIMARY_CCD)
    def getType(self):
        return self.dType
    def hasVideoStream(self):
        return self.HasVideoStream
    def setISOMode(self, enable):
        self.ISOMode = enable
    def setSeqPrefix(self, preFix):
        self.seqPrefix = preFix
    def setNextSequenceID(self, count):
        self.nextSequenceID = count
    def setFilter(self, newFilter):
        self.filter = newFilter
    def hasGain(self):
        return self.gainN is not None
    def getTransferFormat(self):
        return self.transferFormat
    def getTelescopeType(self):
        return self.telescopeType
    def setFITSDir(self, fitsdir):
        self.fitsDir = fitsdir
    def isLooping(self):
        return self.IsLooping
    def registerProperty(self, prop):
        pname = prop.getName()
        if pname == 'GUIDER_EXPOSURE':
            self.HasGuideHead = True
            self.guideChip = CCDChip(self, CCDChip.ChipType.GUIDE_CCD)
        elif pname == 'CCD_FRAME_TYPE':
            self.primaryChip.clearFrameTypes()
            for ft in prop.vp:
                self.primaryChip.addFrameLabel(prop.vp[ft].label)
        elif pname == 'CCD_FRAME':
            if prop.p != INDI.IPerm.IP_RO:
                self.primaryChip.setCanSubFrame(True)
        elif pname == 'GUIDER_FRAME':
            if prop.p != INDI.IPerm.IP_RO:
                self.guideChip.setCanSubFrame(True)
        elif pname == 'CCD_BINNING':
            if prop.p != INDI.IPerm.IP_RO:
                self.primaryChip.setCanBin(True)
        elif pname == 'GUIDER_BINNING':
            if prop.p != INDI.IPerm.IP_RO:
                self.guideChip.setCanBin(True)
        elif pname == 'CCD_ABORT_EXPOSURE':
            if prop.p != INDI.IPerm.IP_RO:
                self.primaryChip.setCanAbort(True)
        elif pname == 'GUIDER_ABORT_EXPOSURE':
            if prop.p != INDI.IPerm.IP_RO:
                self.guideChip.setCanAbort(True)
        elif pname == 'CCD_TEMPERATURE':
            self.HasCooler = True
            self.newTemperatureValue.emit(prop.vp['CCD_TEMPERATURE_VALUE'].value)
        elif pname == 'CCD_COOLER':
            self.HasCoolerControl = True
        elif pname == 'CCD_VIDEO_STREAM':
            self.HasVideoStream = True
        elif pname == 'CCD_TRANSFER_FORMAT':
            tFormat = INDI.IUFindSwitch(prop, 'FORMAT_NATIVE')
            if tFormat is not None and tFormat.s == INDI.ISState.ISS_ON:
                self.transferFormat = CCD.TransferFormat.FORMAT_NATIVE
            else:
                self.transferFormat = CCD.TransferFormat.FORMAT_FITS
        elif pname == 'CCD_EXPOSURE_LOOP':
            looping = INDI.IUFindSwitch(prop, 'LOOP_ON')
            if looping is not None and looping.s == INDI.ISState.ISS_ON:
                self.IsLooping = True
            else:
                self.IsLooping = False
        elif pname == 'TELESCOPE_TYPE':
            tType = INDI.IUFindSwitch(prop, 'TELESCOPE_PRIMARY')
            if tType is not None and tType.s == INDI.ISState.ISS_ON:
                self.telescopeType = CCD.TelescopeType.TELESCOPE_PRIMARY
            else:
                self.telescopeType = CCD.TelescopeType.TELESCOPE_GUIDE
        elif self.gainN is None and prop.getType() == INDI.INDI_PROPERTY_TYPE.INDI_NUMBER:
            for number in prop.vp.values():
                if number.name.lower() == 'gain' or number.label.lower() == 'gain':
                    self.gainN = number
                    break
        super().registerProperty(prop)
    def processLight(self, lvp):
        super().processLight(lvp)
    def processNumber(self, nvp):
        pname = nvp.getName()
        if pname == 'CCD_EXPOSURE':
            np = INDI.IUFindNumber(nvp, 'CCD_EXPOSURE_VALUE')
            if np is not None:
                self.newExposureValue.emit(self.primaryChip, np.value, np.s)
        elif pname == 'CCD_TEMPERATURE':
            self.HasCooler = True
            np = INDI.IUFindNumber(nvp, 'CCD_TEMPERATURE_VALUE')
            if np is not None:
                self.newTemperatureValue.emit(np.value)
        elif pname == 'GUIDER_EXPOSURE':
            np = INDI.IUFindNumber(nvp, 'GUIDER_EXPOSURE_VALUE')
            if np is not None:
                self.newExposureValue.emit(self.guideChip, np.value, np.s)
        elif pname == 'CCD_RAPID_GUIDE_DATA':
            dx = dy= fit = -1.0
            np = None
            if nvp.s == INDI.IPState.IPS_ALERT:
                self.newGuideStarData(self.primaryChip, -1.0, -1.0, -1.0)
            else:
                np = INDI.IUFindNumber(nvp, 'GUIDESTAR_X')
                if np is not None:
                    dx = np.value
                np = INDI.IUFindNumber(nvp, 'GUIDESTAR_Y')
                if np is not None:
                    dy = np.value
                np = INDI.IUFindNumber(nvp, 'GUIDESTAR_FIT')
                if np is not None:
                    fit = np.value
                if dx >= 0.0 and dy >= 0.0 and fit >= 0.0:
                    self.newGuideStarData.emit(self.primaryChip, dx, dy, fit)
        elif pname == 'GUIDER_RAPID_GUIDE_DATA':
            dx = dy= fit = -1.0
            np = None
            if nvp.s == INDI.IPState.IPS_ALERT:
                self.newGuideStarData(self.guideChip, -1.0, -1.0, -1.0)
            else:
                np = INDI.IUFindNumber(nvp, 'GUIDESTAR_X')
                if np is not None:
                    dx = np.value
                np = INDI.IUFindNumber(nvp, 'GUIDESTAR_Y')
                if np is not None:
                    dy = np.value
                np = INDI.IUFindNumber(nvp, 'GUIDESTAR_FIT')
                if np is not None:
                    fit = np.value
                if dx >= 0.0 and dy >= 0.0 and fit >= 0.0:
                    self.newGuideStarData.emit(self.guideChip, dx, dy, fit)
        super().processNumber(nvp)
    def processSwitch(self, svp):
        pname = svp.getName()
        if pname == 'CCD_COOLER':
            self.HasCoolerControl = True
        elif pname == 'VIDEO_STREAM':
            self.HasVideoStream = True
            if svp.vp['STREAM_ON'].s == INDI.ISState.ISS_ON:
                streamFrame = self.baseDevice.getNumber('CCD_STREAM_FRAME')
                if streamFrame is not None:
                    w = INDI.IUFindNumber(streamFrame, 'WIDTH')
                    h = INDI.IUFindNumber(streamFrame, 'HEIGHT')
                if w is not None and h is not None:
                    self.streamW = w.value
                    self.streamH = h.value
                else:
                    rawBP = self.baseDevice.getBLOB('CCD1')
                    if rawBP is not None:
                        x = y = w = h = 0
                        binx = biny = 0
                        x, y, w, h = self.primaryChip.getFrame()
                        binx, biny = self.primaryChip.getBinning()
                        self.streamW = w / binx
                        self.streamH = h / biny
            self.videoStreamToggled(svp.vp['STREAM_ON'].s == INDI.ISState.ISS_ON)
        elif pname == 'CCD_TRANSFER_FORMAT':
            tFormat = INDI.IUFindSwitch(svp, 'FORMAT_NATIVE')
            if tFormat is not None and tFormat.s == INDI.ISState.ISS_ON:
                self.transferFormat = CCD.TransferFormat.FORMAT_NATIVE
            else:
                self.transferFormat = CCD.TransferFormat.FORMAT_FITS
        elif pname == 'RECORD_STREAM':
            recordOFF = INDI.IUFindSwitch(svp, 'RECORD_OFF')
            if recordOFF is not None and recordOFF.s == INDI.ISState.ISS_ON:
                self.videoRecordToggled.emit(False)
            else:
                self.videoRecordToggled.emit(True)
        elif pname == 'TELESCOPE_TYPE':
            tFormat = INDI.IUFindSwitch(svp, 'TELESCOPE_PRIMARY')
            if tFormat is not None and tFormat.s == INDI.ISState.ISS_ON:
                self.telescopeType = CCD.TelescopeType.TELESCOPE_PRIMARY
            else:
                self.telescopeType = CCD.TelescopeType.TELESCOPE_GUIDE
        elif pname == 'CCD_EXPOSURE_LOOP':
            looping = INDI.IUFindSwitch(svp, 'LOOP_ON')
            if looping is not None and looping.s == INDI.ISState.ISS_ON:
                self.IsLooping = True
            else:
                self.IsLooping = False
        elif pname == 'CONNECTION':
            dSwitch = INDI.IUFindSwitch(svp, 'DISCONNECT')
            if dSwitch is not None and dSwitch.s == INDI.ISState.ISS_ON:
                self.videoStreamToggled.emit(False)
        super().processSwitch(svp)
    def processText(self, tvp):
        pname = tvp.getName()
        if pname == 'CCD_FILE_PATH':
            filePath = INDI.IUFindText(tvp, 'FILE_PATH')
            if filePath is not None:
                self.newRemoteFile.emit(filePath)
        super().processText(tvp)
    def processBLOB(self, bp):
        if bp.bvp.p == INDI.IPerm.IP_RO or bp.size == 0:
            return
        BType = CCD.BlobType.BLOB_OTHER
        if 'stream' in bp.format:
            streamFrame = self.baseDevice.getNumber('CCD_STREAM_FRAME')
            if streamFrame is not None:
                w = INDI.IUFindNumber(streamFrame, 'WIDTH')
                h = INDI.IUFindNumber(streamFrame, 'HEIGHT')
            if w is not None and h is not None:
                self.streamW = w.value
                self.streamH = h.value
            else:
                x = y = w = h = 0
                binx = biny = 0
                x, y, w, h = self.primaryChip.getFrame()
                binx, biny = self.primaryChip.getBinning()
                self.streamW = w / binx
                self.streamH = h / biny
            self.newVideoFrame.emit(bp)
            return
        fmt = bp.format.lower().remove('.')
        if fmt in QImageReader.supportedImageFormats():
            BType = CCD.BlobType.BLOB_IMAGE
        elif 'fits' in bp.format:
            BType = CCD.BlobType.BLOB_FITS
        elif fmt in CCD.RAWFormats:
            BType = CCD.BlobType.BLOB_RAW
        if BType == CCD.BlobType.BLOB_OTHER:
            super().processBLOB(bp)
            return
        targetChip = None
        if bp.name == 'CCD2':
            targetChip = self.guideChip
        else:
            targetChip = self.primaryChip
        if not targetChip.isBatchMode():
            currentDir = QStandardPaths.writableLocation(QStandardPaths.TempLocation)
        else:
            currentDir = self.fitsdir if self.fitsDir is not None else Options.Instance().value('npindi/fitsDir')
        tmpFile = QTemporaryFile(QDir.tempPath() + '/fitsXXXX')
        if not Qdir(currentDir).exists():
            QDir.mkpath(currentDir)
        filename = currentDir
        if not filename.endswith('/'):
            filename += '/'
        if not targetChip.isBatchMode():
            tmpFile.setAutoRemove(False)
            if not tmpFile.open():
                QLoggingCategory.qCCritical(QLoggingCategory.NPINDI, 'CCD processBLOB: Unable to open '+ tmpFile.fileName())
                self.BLOBUpdated.emit(None)
                return
            out = QDataStream(tmpFile)
            nr, n =0, 0
            while nr < bp.size:
                n = out.writeRawData(bp.blob[nr:], bp.size - nr)
                nr += n
            tmpFile.close()
            filename = tmpFile.fileName()
        else:
            ts = QDateTime.currentDateTime().toString('yyyy-MM-ddThh-mm-ss')
            if '_ISO8601' in self.seqPrefix:
                finalPrefix = seqPrefix.replace('ISO8601', ts)
                filename += finalPrefix + '_' + ('%03d' % self.nextSequenceID) + '.' + fmt
            else:
                filename += self.seqPrefix + ('' if not self.seqPrefix else '_') + ('%03d' % self.nextSequenceID) + '.' + fmt
            fits_temp_file = QFile(filename)
            if not fits_temp_file.open(QIODevice.WriteOnly):
                QLoggingCategory.qCCritical(QLoggingCategory.NPINDI, 'CCD processBLOB: Unable to open '+ fits_temp_file.fileName())
                self.BLOBUpdated.emit(None)
                return
            out = QDataStream(fits_temp_file)
            nr, n =0, 0
            while nr < bp.size:
                n = out.writeRawData(bp.blob[nr:], bp.size - nr)
                nr += n
            fits_temp_file.close()
        bp.aux1 = BType.value
        bp.aux2 = filename.encode(encoding='ascii')[:MAXINDIFILENAME]
        if targetChip.isBatchMode():
            QLoggingCategory.qCInfo(QLoggingCategory.NPINDI, '%1 file saved to %2' % (fmt, filename))
        self.BLOBUpdated.emit(bp)
    def getTargetTransferFormat(self):
        return self.targetTransferFormat
    def setTargetTransferFormat(self, value):
        if not isinstance(value, CCD.TransferFormat):
            raise ValueError('setTargetTransferFormat: parameter should be a CCD.TransferFormat')
        self.targetTransferFormat = value
    def hasGuideHead(self):
        return self.HasGuideHead
    def hasCooler(self):
        return self.HasCooler
    def hasCoolerControl(self):
        return self.HasCoolerControl
    def setCoolerControl(self, enable):
        if not self.HasCoolerControl:
            return False
        coolerSP = self.baseDevice.getSwitch('CCD_COOLER')
        if coolerSP is None:
            return False
        coolerSP.vp['COOLER_ON'].s = INDI.ISState.ISS_ON if enable else INDI.ISState.ISS_OFF
        coolerSP.vp['COOLER_OFF'].s = INDI.ISState.ISS_OFF if enable else INDI.ISState.ISS_ON
        self.clientManager.send_new_property(coolerSP)
        return True
    def getChip(self, cType):
        if not isinstance(cType, CCDChip.ChipType):
            raise ValueError('getChip: parameter should be a CCDChip.ChipType')
        if cType == CCDChip.ChipType.PRIMARY_CCD:
            return self.primaryChip
        elif cType == CCDChip.ChipType.GUIDE_CCD:
            return self.guideChip
        return None
    def setRapidGuide(self, targetChip, enable):
        rapidSP = None
        enableS = None
        if targetChip == self.primaryChip:
            rapidSP = self.baseDevice.getSwitch('CCD_RAPID_GUIDE')
        else:
            rapidSP = self.baseDevice.getSwitch('GUIDER_RAPID_GUIDE')
        if rapidSP is None:
            return False
        enableS = INDI.IUFindSwitch(rapidSP, 'ENABLE')
        if enableS is None:
            return False
        if (enable and enableS.s == INDI.ISState.ISS_ON) or (not enable and enableS.s == INDI.ISState.ISS_OFF):
            return True
        INDI.IUResetSwitch(rapidSP)
        rapidSP.vp['ENABLE'].s = INDI.ISState.ISS_ON if enable else INDI.ISState.ISS_OFF
        rapidSP.vp['DISABLE'].s = INDI.ISState.ISS_OFF if enable else INDI.ISState.ISS_ON
        self.clientManager.send_new_property(rapidSP)
        return True
    def configureRapidGuide(self, targetChip, autoLoop, sendImage, showMarker):
        rapidSP = None
        autoLoopS = sendImageS = showMarkerS = None
        if targetChip == self.primaryChip:
            rapidSP = self.baseDevice.getSwitch('CCD_RAPID_GUIDE_SETUP')
        else:
            rapidSP = self.baseDevice.getSwitch('GUIDER_RAPID_GUIDE_SETUP')
        if rapidSP is None:
            return False
        autoLoopS = INDI.IUFindSwitch(rapidSP, 'AUTO_LOOP')
        sendImageS = INDI.IUFindSwitch(rapidSP, 'SEND_IMAGE')
        showMarkerS = INDI.IUFindSwitch(rapidSP, 'SHOW_MARKER')
        if autoLoopS is None or sendImageS is None or showMarkerS is None:
            return False
        if ((autoLoop and autoLoopS.s == INDI.ISState.ISS_ON) or (not autoLoop and autoLoopS.s == INDI.ISState.ISS_OFF)) and \
            ((sendImage and sendImageS.s == INDI.ISState.ISS_ON) or (not sendImage and sendImageS.s == INDI.ISState.ISS_OFF)) and \
            ((showMarker and showMarkerS.s == INDI.ISState.ISS_ON) or (not showMarker and showMarkerS.s == INDI.ISState.ISS_OFF)):
            return True
        autoLoopS.s = INDI.ISState.ISS_ON if autoLoop else INDI.ISState.ISS_OFF
        sendImageS.s = INDI.ISState.ISS_ON if sendImage else INDI.ISState.ISS_OFF
        showMarkerS.s = INDI.ISState.ISS_ON if showMarker else INDI.ISState.ISS_OFF
        self.clientManager.send_new_property(rapidSP)
        return True
    def updateUploadSettings(self, remoteDir):
        filename = self.seqPrefix + ('' if not self.seqPrefix else '_') + 'XXX'
        uploadSettingsTP = None
        uploadT = None
        uploadSettingsTP = self.baseDevice.getText('UPLOAD_SETTINGS')
        if uploadSettingsTP is not None:
            uploadT = INDI.IUFindText(uploadSettingsTP, 'UPLOAD_DIR')
            if uploadT is not None and self.remoteDir:
                uploadT.text = self.remoteDir
            uploadT = INDI.IUFindText(uploadSettingsTP, 'UPLOAD_PREFIX')
            if uploadT is not None:
                uploadT.text = filename
            self.clientManager.send_new_property(uploadSettingsTP)
    def getUploadMode(self):
        uploadModeSP = self.baseDevice.getSwitch('UPLOAD_MODE')
        if uploadModeSP is None:
            QLoggingCategory.qCWarning(QLoggingCategory.NPIND, 'NO UPLOAD_MODE in CCD driver. Please update driver to INDI compliant CCD driver.')
            return CCD.UploadMode.UPLOAD_CLIENT
        if uploadModeSP:
            modeS = INDI.IUFindSwitch(uploadModeSP, 'UPLOAD_CLIENT')
            if modeS is not None and modeS.s == INDI.ISState.ISS_ON:
                return CCD .UploadMode.UPLOAD_CLIENT
            modeS = INDI.IUFindSwitch(uploadModeSP, 'UPLOAD_LOCAL')
            if modeS is not None and modeS.s == INDI.ISState.ISS_ON:
                return CCD .UploadMode.UPLOAD_LOCAL
            modeS = INDI.IUFindSwitch(uploadModeSP, 'UPLOAD_BOTH')
            if modeS is not None and modeS.s == INDI.ISState.ISS_ON:
                return CCD .UploadMode.UPLOAD_BOTH
        return CCD.UploadMode.UPLOAD_CLIENT
    def setUploadMode(self, mode):
        if not isinstance(mode, CCD.UploadMode):
            raise ValueError('setUploadMode: parameter should be a CCD.UploadMode')
        uploadModeSP = self.baseDevice.getSwitch('UPLOAD_MODE')
        if uploadModeSP is None:
            QLoggingCategory.qCWarning(QLoggingCategory.NPIND, 'NO UPLOAD_MODE in CCD driver. Please update driver to INDI compliant CCD driver.')
            return False
        if mode == CCD.UploadMode.UPLOAD_CLIENT:
            modeS = INDI.IUFindSwitch(uploadModeSP, 'UPLOAD_CLIENT')
            if modeS is None:
                return False
            if modeS.s == INDI.ISState.ISS_ON:
                return True
        elif mode == CCD.UploadMode.UPLOAD_BOTH:
            modeS = INDI.IUFindSwitch(uploadModeSP, 'UPLOAD_BOTH')
            if modeS is None:
                return False
            if modeS.s == INDI.ISState.ISS_ON:
                return True
        elif mode == CCD.UploadMode.UPLOAD_LOCAL:
            modeS = INDI.IUFindSwitch(uploadModeSP, 'UPLOAD_LOCAL')
            if modeS is None:
                return False
            if modeS.s == INDI.ISState.ISS_ON:
                return True
        INDI.IUResetSwitch(uploadModeSP)
        modeS.s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(uploadModeSP)
        return True
    def getTemperature(self):
        if not self.HasCooler:
            return None
        temperatureNP = self.baseDevice.getNumber('CCD_TEMPERATURE')
        if temperatureNP is None:
            return None
        return temperatureNP.vp['CCD_TEMPERATURE_VALUE'].value
    def setTemperature(self, value):
        nvp = self.baseDevice.getNumber('CCD_TEMPERATURE')
        if nvp is None:
            return False
        np = INDI.IUFindNumber(nvp, 'CCD_TEMPERATURE_VALUE')
        if np is None:
            return False
        np.value = value
        self.clientManager.send_new_property(nvp)
        return True
    def setTransferFormat(self, tFormat):
        if not isinstance(tFormat, CCD.TransferFormat):
            raise ValueError('setTransferFormat: parameter should a CCD.TransferFormat')
        if tFormat == self.transferFormat:
            return True
        svp = self.baseDevice.getSwitch('CCD_TRANSFER_FORMAT')
        if svp is None:
            return False
        formatFITS = INDI.IUFindSwitch('FORMAT_FITS')
        formatNative = INDI.IUFindSwitch('FORMAT_NATIVE')
        if formatFITS is None or formatNative is None:
            return False
        self.transferFormat = tFormat
        formatFITS.s = INDI.ISState.ISS_ON if self.transferFormat == CCD.TransferFormat.FORMAT_FITS else INDI.ISState.ISS_OFF
        formatNative.s = INDI.ISState.ISS_ON if self.transferFormat == CCD.TransferFormat.FORMAT_NATIVE else INDI.ISState.ISS_OFF
        self.clientManager.send_new_property(svp)
        return True
    def setTelescopeType(self, tType):
        if not isinstance(tType, CCD.TelescopeType):
            raise ValueError('setTelescopeType: parameter should a CCD.TelescopeType')
        if tType == self.telescopeType:
            return True
        svp = self.baseDevice.getSwitch('TELESCOPE_TYPE')
        if svp is None:
            return False
        typePrimary = INDI.IUFindSwitch('TELESCOPE_PRIMARY')
        typeGuide = INDI.IUFindSwitch('TELESCOPE_GUIDE')
        if typePrimary is None or typeGuide is None:
            return False
        self.telescopeType = tType
        typePrimary.s = INDI.ISState.ISS_ON if self.telescopeType == CCD.TelescopeType.TELESCOPE_PRIMARY else INDI.ISState.ISS_OFF
        typeGuide.s = INDI.ISState.ISS_ON if self.transferFormat == CCD.TelescopeType.TELESCOPE_GUIDE else INDI.ISState.ISS_OFF
        self.clientManager.send_new_property(svp)
        self.setConfig(INDIConfig.SAVE_CONFIG)
        return True
    def setVideoStreamEnabled(self, enable):
        if not self.HasVideoStream:
            return False
        svp = self.baseDevice.getSwitch('CCD_VIDEO_STREAM')
        if svp is None:
            return False
        if (enable and svp.vp['STREAM_ON'].s == INDI.ISState.ISS_ON) or (not enable and svp.vp['STREAM_OFF'].s == INDI.ISState.ISS_ON):
            return True
        svp.vp['STREAM_ON'].s = INDI.ISState.ISS_ON if enable else INDI.ISState.ISS_OFF
        svp.vp['STREAM_OFF'].s = INDI.ISState.ISS_OFF if enable else INDI.ISState.ISS_ON
        self.clientManager.send_new_property(svp)
        return True
    def resetStreamingFrame(self):
        frameProp = self.baseDevice.getNumber('CCD_STREAM_FRAME')
        if frameProp is None:
            return False
        xarg = INDI.IUFindNumber(frameProp, 'X')
        yarg = INDI.IUFindNumber(frameProp, 'Y')
        warg = INDI.IUFindNumber(frameProp, 'WIDTH')
        harg = INDI.IUFindNumber(frameProp, 'HEIGHT')
        if xarg is not None and yarg is not None and warg is not None and harg is not None:
            if xarg.value == xarg.min and yarg.value == yarg.min and warg.value == warg.max and harg.value == harg.max:
                return False # check JM
            xarg.value = xarg.min
            yarg.value = yarg.min
            warg.value = warg.max
            harg.value = harg.max
            self.clientManager.send_new_property(frameProp)
            return True
        return False
    def setStreamingFrame(self, x, y, w, h):
        frameProp = self.baseDevice.getNumber('CCD_STREAM_FRAME')
        if frameProp is None:
            return False
        xarg = INDI.IUFindNumber(frameProp, 'X')
        yarg = INDI.IUFindNumber(frameProp, 'Y')
        warg = INDI.IUFindNumber(frameProp, 'WIDTH')
        harg = INDI.IUFindNumber(frameProp, 'HEIGHT')
        if xarg is not None and yarg is not None and warg is not None and harg is not None:
            if xarg.value == x and yarg.value == y and warg.value == w and harg.value == h:
                return True
            xarg.value = max(xarg.min, min(x + xarg.value, xarg.max))
            yarg.value = max(yarg.min, min(y + yarg.value, yarg.max))
            warg.value = max(warg.min, min(w, warg.max))
            harg.value = max(harg.min, min(h, harg.max))
            self.clientManager.send_new_property(frameProp)
            return True
        return False
    def isStreamingEnabled(self):
        if not self.HasVideoStream:
            return False
        svp = self.baseDevice.getSwitch('CCD_VIDEO_STREAM')
        if svp is None:
            return False
        return svp.vp['STREAM_ON'].s == INDI.ISState.ISS_ON
    def setSERNameDirectory(self, filename, directory):
        tvp = self.baseDevice.getText('RECORD_FILE')
        if tvp is None:
            return False
        filenameT = INDI.IUFindText(tvp, 'RECORD_FILE_NAME')
        dirT = INDI.IUFindText(tvp, 'RECORD_FILE_DIR')
        if filenameT is None or dirT is None:
            return False
        filenameT.text = filename.encode(encoding='ascii')
        dirT.text = directory.encode(encoding='ascii')
        self.clientManager.send_new_property(tvp)
        return True
    def getSERNameDirectory(self):
        tvp = self.baseDevice.getText('RECORD_FILE')
        if tvp is None:
            return None
        filenameT = INDI.IUFindText(tvp, 'RECORD_FILE_NAME')
        dirT = INDI.IUFindText(tvp, 'RECORD_FILE_DIR')
        if filenameT is None or dirT is None:
            return None
        filename = filenameT.text
        directory = dirT.text
        return (filename, directory)
    def startRecording(self):
        svp = self.baseDevice.getSwitch('RECORD_STREAM')
        if svp is None:
            return False
        recordON = INDI.IUFindSwitch(svp, 'RECORD_ON')
        if recordON is None:
            return False
        if recordON.s == INDI.ISState.ISS_ON:
            return True
        INDI.IUResetSwitch(svp)
        recordON.s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(svp)
        return True
    def startDurationRecording(self, duration):
        nvp = self.baseDevice.getNumber('RECORD_OPTIONS')
        if nvp is None:
            return False
        durationN = INDI.IUFindNumber(nvp, 'RECORD_DURATION')
        if durationN is None:
            return False
        svp = self.baseDevice.getSwitch('RECORD_STREAM')
        if svp is None:
            return False
        recordON = INDI.IUFindSwitch(svp, 'RECORD_DURATION_ON')
        if recordON is None:
            return False
        if recordON.s == INDI.ISState.ISS_ON:
            return True
        durationN.value = duration
        self.clientManager.send_new_property(nvp)
        INDI.IUResetSwitch(svp)
        recordON.s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(svp)
        return True
    def startFramesRecording(self, frames):
        nvp = self.baseDevice.getNumber('RECORD_OPTIONS')
        if nvp is None:
            return False
        frameN = INDI.IUFindNumber(nvp, 'RECORD_FRAME_TOTAL')
        if frameN is None:
            return False
        svp = self.baseDevice.getSwitch('RECORD_STREAM')
        if svp is None:
            return False
        recordON = INDI.IUFindSwitch(svp, 'RECORD_FRAME_ON')
        if recordON is None:
            return False
        if recordON.s == INDI.ISState.ISS_ON:
            return True
        frameN.value = frames
        self.clientManager.send_new_property(nvp)
        INDI.IUResetSwitch(svp)
        recordON.s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(svp)
        return True
    def stopRecording(self):
        svp = self.baseDevice.getSwitch('RECORD_STREAM')
        if svp is None:
            return False
        recordOFF = INDI.IUFindSwitch(svp, 'RECORD_OFF')
        if recordOFF is None:
            return False
        if recordOFF.s == INDI.ISState.ISS_ON:
            return True
        INDI.IUResetSwitch(svp)
        recordOFF.s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(svp)
        return True
    def setGain(self, value):
        if self.gainN is None:
            return False
        self.gainN.value = value
        self.clientManager.send_new_elem(self.gainN.nvp, self.gainN)
        return True
    def getGain(self):
        if self.gainN is None:
            return None
        return self.gainN.value
    def getGainMinMaxStep(self):
        if self.gainN is None:
            return None
        return (self.gainN.min, self.gainN.max, self.gainN.step)
    def isBLOBEnabled(self):
        return self.clientManager.get_blob_mode(self.getDeviceName(), 'CCD1') != INDI.BLOBHandling.B_NEVER
    def setBLOBEnabled(self, enable):
        if enable:
            self.clientManager.set_blob_mode(INDI.BLOBHandling.B_ALSO, self.baseDevice.getDeviceName(), 'CCD1')
            self.clientManager.set_blob_mode(INDI.BLOBHandling.B_ALSO, self.baseDevice.getDeviceName(), 'CCD2')
        else:
            self.clientManager.set_blob_mode(INDI.BLOBHandling.B_NEVER, self.baseDevice.getDeviceName(), 'CCD1')
            self.clientManager.set_blob_mode(INDI.BLOBHandling.B_NEVER, self.baseDevice.getDeviceName(), 'CCD2')
        return True
    def setExposureLoopingEnabled(self, enable):
        self.IsLooping = enable
        svp = self.baseDevice.getSwitch('CCD_EXPOSURE_LOOP')
        if svp is None:
            return False
        svp.vp['LOOP_ON'].s = INDI.ISState.ISS_ON if enable else INDI.ISState.ISS_OFF
        svp.vp['LOOP_OFF'].s = INDI.ISState.ISS_OFF if enable else INDI.ISState.ISS_ON
        self.clientManager.send_new_property(svp)
        return True
    def setExposureLoopCount(self, count):
        nvp = self.baseDevice.getNumber('CCD_EXPOSURE_LOOP_COUNT')
        if nvp is None:
            return False
        nvp.vp['FRAMES'].value = count
        self.clientManager.send_new_property(nvp)
        return True
