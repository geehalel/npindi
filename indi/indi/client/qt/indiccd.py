from PyQt5.QtCore import pyqtSignal, pyqtSlot
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
        expProp.np['CCD_EXPOSURE_VALUE'].value = exposure
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
    def __init__(self, iPtr):
        super().__init__(iPtr)
        self.dType = DeviceFamily.KSTARS_CCD
        self.baseDevice = ccd.getBaseDevice()
        self.clientManager = ccd.getDriverInfo().getClientManager()
        self.filter = None
        self.ISOMode = True
        self.HasGuideHead = False
        self.HasCooler = False
        self.HasCoolerControl = False
        self.HasVideoStream = False
        self.isLooping = False
        self.seqPrefix = None
        self.fitsDir = None
        self.BLOBFilename = None
        self.nextSequenceID = 0
        self.primaryChip = None
        self.guideChip = None
        self.transferFormat = CCD.TransferFormat.FORMAT_FITS
        self.targetTransferFormat = CCD.TransferFormat.FORMAT_FITS
        self.telescopeType = CCD.TelescopeType.TELESCOPE_UNKNOWN
        self.gainN = None
