from PyQt5.QtCore import pyqtSignal, pyqtSlot
from indi.client.qt.indicommon import *
from indi.client.qt.indistd import *
from indi.client.qt.skypoint import *
from indi.INDI import *

import enum
class TelescopeMotionNS(enum.Enum):
    MOTION_NORTH = 0
    MOTION_SOUTH = 1
class TelescopeMotionWE(enum.Enum):
    MOTION_WEST = 0
    MOTION_EAST = 1
class TelescopeMotionCommand(enum.Enum):
    MOTION_START = 0
    MOTION_STOP = 1
class TelescopeStatus(enum.Enum):
    MOUNT_IDLE = 0
    MOUNT_MOVING = 1
    MOUNT_SLEWING = 2
    MOUNT_TRACKING = 3
    MOUNT_PARKING = 4
    MOUNT_PARKED = 5
    MOUNT_ERROR = 6
class ParkStatus(enum.Enum):
    PARK_UNKNOWN = 0
    PARK_PARKED = 1
    PARK_PARKING = 2
    PARK_UNPARKING = 3
    PARK_UNPARKED = 4
class ParkOptionCommand(enum.Enum):
    PARK_OPTION_CURRENT = 0
    PARK_OPTION_DEFAULT = 1
    PARK_OPTION_WRITE_DATA = 2
class Telescope(ISD.DeviceDecorator):
    newTarget = pyqtSignal(str)
    newCoord = pyqtSignal(SkyPoint)
    def __init__(self, iPtr):
        super().__init__(iPtr)
        self.dType = DeviceFamily.KSTARS_TELESCOPE
        self.currentCoord = SkyPoint()
        self.minAlt = -1
        self.maxAlt = -1
        self.parkStatus = ParkStatus.PARK_UNKNOWN
        self.EqCoordPreviousState = INDI.IPState.IPS_IDLE
        self.inManualMotion = False
        self.inCustomParking = False
        self.NSPreviousState = INDI.IPState.IPS_IDLE
        self.WEPreviousState = INDI.IPState.IPS_IDLE
        self.m_hasAlignmentModel = False
        self.m_canControlTrack = False
        self.m_hasTrackModes = False
        self.m_hasCustomTrackRates = False
        self.m_hasCustomParking = False
    def getType(self):
        return self.dType
    def canControlTrack(self):
        return self.m_canControlTrack
    def hasTrackModes(self):
        return self.m_hasTrackModes
    def hasCustomTrackRate(self):
        return self.m_hasCustomTrackRates
    def isParked(self):
        return self.parkStatus == ParkStatus.PARK_PARKED
    def canCustomPark(self):
        return self.m_hasCustomParking
    def getParkStatus(self):
        return self.parkStatus
    def hasAlignmentModel(self):
        return self.m_hasAlignmentModel
    def getEqCoords(self):
        ra, dec = None, None
        EqProp = self.baseDevice.getNumber('EQUATORIAL_EOD_COORD')
        if EqProp is not None:
            RAEle = INDI.IUFindNumber(EqProp, 'RA')
            if RAEle is not None:
                ra = RAEle.value
            DecEle = INDI.IUFindNumber(EqProp, 'DEC')
            if DecEle is not None:
                dec = DecEle.value
        return (ra, dec)
    def registerProperty(self, prop):
        #QLoggingCategory.qCDebug(QLoggingCategory.NPINDI, 'inditelescope registerProperty '+prop.getName())
        if prop.getName() == 'TELESCOPE_INFO':
            if prop.vp is None: return
            aperture_ok = True
            focal_ok = True
            aperture = IUFindNumber(prop, 'TELESCOPE_APERTURE')
            if aperture and aperture.value == 0:
                try:
                    temp = float(self.getDriverInfo().getAuxInfo().value('TELESCOPE_APERTURE'))
                except:
                    aperture_ok = False
                if aperture_ok:
                    aperture.value = temp
                    g_aperture = IUFindNumber(prop, 'GUIDER_APERTURE')
                    if g_aperture and g_aperture.value == 0:
                        g_aperture.value = aperture.value
            focal_length = IUFindNumber(prop, 'TELESCOPE_FOCAL_LENGTH')
            if focal_length and focal_length.value == 0:
                try:
                    temp = float(self.getDriverInfo().getAuxInfo().value('TELESCOPE_FOCAL_LENGTH'))
                except:
                    focal_ok = False
                if focal_ok:
                    focal_length.value = temp
                    g_focal = IUFindNumber(prop, 'GUIDER_FOCAL_LENGTH')
                    if g_focal and g_focal.value == 0:
                        g_focal.value = focal_length.value
            if aperture_ok and focal_ok:
                self.clientManager.send_new_property(prop)
        if prop.getName() == 'TELESCOPE_PARK':
            if prop.vp is None: return
            sp = INDI.IUFindNumber(prop, 'PARK')
            if sp is not None:
                if sp.s == INDI.ISState.ISS_ON and prop.s == INDI.IPState.IPS_OK:
                    self.parkStatus = ParkStatus.PARK_PARKED
                elif sp.s == INDI.ISState.ISS_OFF and prop.s == INDI.IPState.IPS_OK:
                    self.parkStatus = ParkStatus.PARK_UNPARKED
        if prop.getName() in {'ALIGNMENT_POINTSET_ACTION', 'ALIGNLIST'}:
            self.m_hasAlignmentModel = True
        elif prop.getName() == 'TELESCOPE_TRACK_STATE':
            self.m_canControlTrack = True
        elif prop.getName() == 'TELESCOPE_TRACK_MODE':
            self.m_hasTrackModes = True
        elif prop.getName() == 'TELESCOPE_TRACK_RATE':
            self.m_hasCustomTrackRates = True
        elif prop.getName() == 'TELESCOPE_PARK_OPTION':
            self.m_hasCustomParking = True
        super().registerProperty(prop)
    def processNumber(self, nvp):
        if nvp.name == 'EQUATORIAL_EOD_COORD':
            RA = INDI.IUFindNumber(nvp, 'RA')
            DEC = INDI.IUFindNumber(nvp, 'DEC')
            if RA is None or DEC is None:
                return
            prevCoord = SkyPoint(self.currentCoord.ra(), self.currentCoord.dec())
            self.currentCoord.setRA(RA.value)
            self.currentCoord.setDec(DEC.value)
            lstdms = dms(getGAST() * 15.0 + Options.Instance().value('location/longitude'))
            self.currentCoord.EquatorialToHorizontal(lstdms, dms(Options.Instance().value('location/latitude')))
            self.EqCoordPreviousState = nvp.s
            if prevCoord.ra() != self.currentCoord.ra() or prevCoord.dec() != self.currentCoord.dec():
                self.newCoord.emit(self.currentCoord)
        # elif nvp.name == 'HORIZONTAL_COORD':
        #     Az = INDI.IUFindNumber(nvp, 'AZ')
        #     Alt = INDI.IUFindNumber(nvp, 'ALT')
        #     if Az is None or Alt is None:
        #         return
        #     prevCoord = SkyPoint(self.currentCoord.ra(), self.currentCoord.dec())
        #     self.currentCoord.setAz(Az.value)
        #     self.currentCoord.setAlt(Alt.value)
        #     lstdms = dms(getGAST() * 15.0 + Options.Instance().value('location/longitude'))
        #     self.currentCoord.HorizontalToEquatorial(lstdms, dms(Options.Instance().value('location/latitude')))
        #     if prevCoord.ra() != self.currentCoord.ra() or prevCoord.dec() != self.currentCoord.dec():
        #         self.newCoord.emit(self.currentCoord)
        super().processNumber(nvp)
    def processSwitch(self, svp):
        manualMotionChanged = False
        if svp.name == 'TELESCOPE_PARK':
            sp = INDI.IUFindSwitch(svp, 'PARK')
            if sp is not None:
                if svp.s == INDI.IPState.IPS_ALERT:
                    if self.parkStatus == ParkStatus.PARK_PARKING:
                        self.parkStatus = ParkStatus.PARK_UNPARKED
                    elif self.parkStatus == ParkStatus.PARK_UNPARKING:
                        self.parkStatus = ParkStatus.PARK_PARKED
                elif svp.s == INDI.IPState.IPS_BUSY and sp.s == INDI.ISState.ISS_ON and self.parkStatus != ParkStatus.PARK_PARKING:
                    self.parkStatus = ParkStatus.PARK_PARKING
                elif svp.s == INDI.IPState.IPS_BUSY and sp.s == INDI.ISState.ISS_OFF and self.parkStatus != ParkStatus.PARK_UNPARKING:
                    self.parkStatus = ParkStatus.PARK_UNPARKING
                elif svp.s == INDI.IPState.IPS_OK and sp.s == INDI.ISState.ISS_ON and self.parkStatus != ParkStatus.PARK_PARKED:
                    self.parkStatus = ParkStatus.PARK_PARKED
                elif (svp.s == INDI.IPState.IPS_BUSY or svp.s == INDI.IPState.IPS_IDLE) and sp.s == INDI.ISState.ISS_OFF and self.parkStatus != ParkStatus.PARK_UNPARKED:
                    self.parkStatus = ParkStatus.PARK_UNPARKED
        elif svp.name == 'TELESCOPE_ABORT_MOTION':
            if svp.s == INDI.IPState.IPS_OK:
                self.inCustomParking = False
        elif svp.name in {'TELESCOPE_MOTION_NS', 'TELESCOPE_MOTION_WE'}:
            manualMotionChanged = True
        if manualMotionChanged:
            NSCurrentMotion = self.baseDevice.getSwitch('TELESCOPE_MOTION_NS').s
            WECurrentMotion = self.baseDevice.getSwitch('TELESCOPE_MOTION_WE').s
            self.inCustomParking = False
            if NSCurrentMotion == INDI.IPState.IPS_BUSY or WECurrentMotion == INDI.IPState.IPS_BUSY or self.NSPreviousState == INDI.IPState.IPS_BUSY or self.WEPreviousState == INDI.IPState.IPS_BUSY:
                if not self.inManualMotion and \
                    ((NSCurrentMotion == INDI.IPState.IPS_BUSY and self.NSPreviousState != INDI.IPState.IPS_BUSY) or\
                    (WECurrentMotion == INDI.IPState.IPS_BUSY and self.WEPreviousState != INDI.IPState.IPS_BUSY)):
                    self.inManualMotion = True
                elif self.inManualMotion and \
                    ((NSCurrentMotion != INDI.IPState.IPS_BUSY and self.NSPreviousState == INDI.IPState.IPS_BUSY) or\
                    (WECurrentMotion != INDI.IPState.IPS_BUSY and self.WEPreviousState == INDI.IPState.IPS_BUSY)):
                    self.inManualMotion = False
                self.NSPreviousState = NSCurrentMotion
                self.WEPreviousState = WECurrentMotion
        super().processSwitch(svp)
    def processText(self, tvp):
        super().processText(tvp)
    def canGuide(self):
        raPulse = self.baseDevice.getNumber('TELESCOPE_TIMED_GUIDE_WE')
        decPulse = self.baseDevice.getNumber('TELESCOPE_TIMED_GUIDE_NS')
        if raPulse is not None and decPulse is not None:
            return True
        else:
            return False
    def canSync(self):
        motionSP = self.baseDevice.getSwitch('ON_COORD_SET')
        if motionSP is None:
            return False
        syncSW = INDI.IUFindSwitch(motionSP, 'SYNC')
        return syncSW is not None
    def canPark(self):
        parkSP = self.baseDevice.getSwitch('TELESCOPE_PARK')
        if parkSP is None:
            return False
        parkSW = INDI.IUFindSwitch(parkSP, 'PARK')
        return parkSW is not None
    def isSlewing(self):
        EqProp = self.baseDevice.getNumber('EQUATORIAL_EOD_COORD')
        if EqProp is None:
            return False
        return EqProp.s == INDI.IPState.IPS_BUSY
    def isInMotion(self):
        return self.isSlewing() or self.inManualMotion
    def doPulse(self, guidedir, msecs):
        raPulse = self.baseDevice.getNumber('TELESCOPE_TIMED_GUIDE_WE')
        decPulse = self.baseDevice.getNumber('TELESCOPE_TIMED_GUIDE_NS')
        npulse = None
        if raPulse is None or decPulse is None:
            return False
        if guidedir == GuideDirection.RA_INC_DIR:
            dirPulse = INDI.IUFindNumber(raPulse, 'TIMED_GUIDE_W')
            if dirPulse is None:
                return False
            npulse = raPulse
        elif guidedir == GuideDirection.RA_DEC_DIR:
            dirPulse = INDI.IUFindNumber(raPulse, 'TIMED_GUIDE_E')
            if dirPulse is None:
                return False
            npulse = raPulse
        elif guidedir == GuideDirection.DEC_INC_DIR:
            dirPulse = INDI.IUFindNumber(decPulse, 'TIMED_GUIDE_N')
            if dirPulse is None:
                return False
            npulse = decPulse
        elif guidedir == GuideDirection.DEC_DEC_DIR:
            dirPulse = INDI.IUFindNumber(raPulse, 'TIMED_GUIDE_S')
            if dirPulse is None:
                return False
            npulse = decPulse
        else:
            return False
        dirPulse.value = msecs
        self.clientManager.send_new_property(npulse)
        return True
    def doPulseRaDec(self, ra_dir, ra_msecs, dec_dir, dec_msecs):
        if not self.canGuide():
            return False
        if not ra_dir in {GuideDirection.RA_INC_DIR, GuideDirection.RA_DEC_DIR}:
            return False
        if not _dec_dir in {GuideDirection.DEC_INC_DIR, GuideDirection.DEC_DEC_DIR}:
            return False
        raOk = self.doPulse(ra_dir, ra_msecs)
        decOk = self.doPulse(dec_dir, dec_msecs)
        return ra_ok and decOk
    def sendCoords(self, ScopeTarget):
        if not isinstance(ScopeTarget, SkyPoint):
            raise ValueError('sendCoords: ScopeTarget should be a SkyPoint object')
        useJ2000 = False
        EqProp = self.baseDevice.getNumber('EQUATORIAL_EOD_COORD')
        if EqProp is None:
            EqProp = self.baseDevice.getNumber('EQUATORIAL_COORD')
            if EqProp is not None:
                useJ2000 = True
        HorProp = self.baseDevice.getNumber('HORIZONTAL_COORD')
        if EqProp is not None and EqProp.p == INDI.IPerm.IP_RO:
            EqProp = None
        if HorProp is not None and HorProp.p == INDI.IPerm.IP_RO:
            HorProp = None
        if EqProp:
            RAEle = INDI.IUFindNumber(EqProp, 'RA')
            if RAEle is None:
                return False
            DecEle = INDI.IUFindNumber(EqProp, 'DEC')
            if DecEle is None:
                return False
            if useJ2000:
                ScopeTarget.apparentCoord(GetJD(), J2000)
            currentRA = RAEle.value
            currentDEC = DecEle.value
            lstdms = dms(getGAST() * 15.0 + Options.Instance().value('location/longitude'))
            ScopeTarget.EquatorialToHorizontal(lstdms, dms(Options.Instance().value('location/latitude')))
        if HorProp:
            AzEle = INDI.IUFindNumber(HorProp, 'AZ')
            if AzEle is None:
                return False
            AltEle = INDI.IUFindNumber(HorProp, 'ALT')
            if AltEle is None:
                return False
            currentAz = AzEle.value
            currentAlt = AltEle.value
        if EqProp is None and HorProp is None:
            return False
        targetAlt = ScopeTarget.altRefracted().Degrees()
        if self.minAlt != -1.0 and self.maxAlt != -1.0:
            if targetAlt < self.minAlt or targetAlt > self.maxAlt:
                return False
        if targetAlt < 0.0:
            if EqProp:
                RAEle.value = currentRA
                DecEle.value = currentDEC
            if HorProp:
                AzEle.value = currentAz
                AltEle.value = currentAlt
            return False
        if EqProp:
            RAEle.value = ScopeTarget.ra().Hours()
            DecEle.value = ScopeTarget.dec().Degrees()
            self.clientManager.send_new_property(EqProp)
            RAEle.value = currentRA
            DecEle.value = currentDEC
        elif HorProp:
            AzEle.value = ScopeTarget.az().Degrees()
            AltEle.value = ScopeTarget.alt().Degrees()
            self.clientManager.send_new_property(HorProp)
            AzEle.value = currentAz
            AltEle.value = currentAlt
        return True
    def Slew(self, ra, dec):
        target = SkyPoint()
        target.setRA(ra)
        target.setDec(dec)
        return self.SlewSkyPoint(target)
    def SlewSkyPoint(self, ScopeTarget):
        motionSP = self.baseDevice.getSwitch('ON_COORD_SET')
        if motionSP is None:
            return False
        slewSW = INDI.IUFindSwitch(motionSP, 'TRACK')
        if slewSW is None:
            slewSW = INDI.IUFindSwitch(motionSP, 'SLEW')
        if slewSW is None:
            return False
        if slewSW.s != INDI.ISState.ISS_ON:
            INDI.IUResetSwitch(motionSP)
            slewSW.s = INDI.ISState.ISS_ON
            self.clientManager.send_new_property(motionSP)
        return self.sendCoords(ScopeTarget)
    def Sync(self, ra, dec):
        target = SkyPoint()
        target.setRA(ra)
        target.setDec(dec)
        return self.SyncSkyPoint(target)
    def SyncSkyPoint(self, ScopeTarget):
        motionSP = self.baseDevice.getSwitch('ON_COORD_SET')
        if motionSP is None:
            return False
        syncSW = INDI.IUFindSwitch(motionSP, 'SYNC')
        if syncSW is None:
            return False
        if syncSW.s != INDI.ISState.ISS_ON:
            INDI.IUResetSwitch(motionSP)
            syncSW.s = INDI.ISState.ISS_ON
            self.clientManager.send_new_property(motionSP)
        return self.sendCoords(ScopeTarget)
    @pyqtSlot()
    def Abort(self):
        motionSP = self.baseDevice.getSwitch('TELESCOPE_ABORT_MOTION')
        if motionSP is None:
            return False
        abortSW = INDI.IUFindSwitch(motionSP, 'ABORT')
        if abortSW is None:
            return False
        abortSW.s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(motionSP)
        self.inCustomParking = False
        return True
    @pyqtSlot()
    def Park(self):
        parkSP = self.baseDevice.getSwitch('TELESCOPE_PARK')
        if parkSP is None:
            return False
        parkSW = INDI.IUFindSwitch(parkSP, 'PARK')
        if parkSW is None:
            return False
        INDI.IUResetSwitch(parkSP)
        parkSW.s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(parkSP)
        return True
    @pyqtSlot()
    def UnPark(self):
        parkSP = self.baseDevice.getSwitch('TELESCOPE_PARK')
        if parkSP is None:
            return False
        parkSW = INDI.IUFindSwitch(parkSP, 'UNPARK')
        if parkSW is None:
            return False
        INDI.IUResetSwitch(parkSP)
        parkSW.s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(parkSP)
        return True
    def MoveNS(self, dir, cmd):
        motionSP = self.baseDevice.getSwitch('TELESCOPE_MOTION_NS')
        if motionSP is None:
            return False
        motionNorth = INDI.IUFindSwitch(motionSP, 'MOTION_NORTH')
        motionSouth = INDI.IUFindSwitch(motionSP, 'MOTION_SOUTH')
        if motionNorth is None or motionSouth is None:
            return False
        if dir == TelescopeMotionNS.MOTION_NORTH and motionNorth.s == (INDI.ISState.ISS_ON if cmd == TelescopeMotionCommand.MOTION_START else INDI.ISState.ISS_OFF):
            return True
        if dir == TelescopeMotionNS.MOTION_SOUTH and motionSouth.s == (INDI.ISState.ISS_ON if cmd == TelescopeMotionCommand.MOTION_START else INDI.ISState.ISS_OFF):
            return True
        INDI.IUResetSwitch(motionSP)
        if cmd == TelescopeMotionCommand.MOTION_START:
            if dir == TelescopeMotionNS.MOTION_NORTH:
                motionNorth.s = INDI.ISState.ISS_ON
            else:
                motionSouth.s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(motionSP)
        return True
    def MoveWE(self, dir, cmd):
        motionSP = self.baseDevice.getSwitch('TELESCOPE_MOTION_WE')
        if motionSP is None:
            return False
        motionWest = INDI.IUFindSwitch(motionSP, 'MOTION_WEST')
        motionEast = INDI.IUFindSwitch(motionSP, 'MOTION_EAST')
        if motionWest is None or motionEast is None:
            return False
        if dir == TelescopeMotionWE.MOTION_WEST and motionWest.s == (INDI.ISState.ISS_ON if cmd == TelescopeMotionCommand.MOTION_START else INDI.ISState.ISS_OFF):
            return True
        if dir == TelescopeMotionWE.MOTION_EAST and motionEast.s == (INDI.ISState.ISS_ON if cmd == TelescopeMotionCommand.MOTION_START else INDI.ISState.ISS_OFF):
            return True
        INDI.IUResetSwitch(motionSP)
        if cmd == TelescopeMotionCommand.MOTION_START:
            if dir == TelescopeMotionWE.MOTION_WEST:
                motionWest.s = INDI.ISState.ISS_ON
            else:
                motionEast.s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(motionSP)
        return True
    @pyqtSlot(int)
    def setSlewRate(self, index):
        slewRateSP = self.baseDevice.getSwitch('TELESCOPE_SLEW_RATE')
        if slewRateSP is None:
            return False
        if index < 0 or index > len(slewRateSP.vp):
            return False
        INDI.IUResetSwitch(slewRateSP)
        list(slewRateSP.vp.values())[index].s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(slewRateSP)
        return True
    def setAltLimits(self, minAltitude, maxAltitude):
        self.minAlt = minAltitude
        self.maxAlt = maxAltitude
    def setAlignmentModelEnabled(self, enable):
        wasExecuted = False
        alignSwitch = self.baseDevice.getSwitch('ALIGNMENT_SUBSYSTEM_ACTIVE')
        if alignSwitch is not None:
            alignSwitch.vp['ALIGNMENT SUBSYSTEM ACTIVE'].s = INDI.ISState.ISS_ON if enable else INDI.ISState.ISS_OFF
            self.clientManager.send_new_property(alignSwitch)
            wasExecuted = True
        alignSwitch = self.baseDevice.getSwitch('ALIGNMODE')
        if alignSwitch is not None:
            INDI.IUResetSwitch(alignSwitch)
            if enable:
                alignSwitch.vp['ALIGNNSTAR'].s = INDI.ISState.ISS_ON
            else:
                alignSwitch.vp['NOALIGN'].s = INDI.ISState.ISS_ON
            self.clientManager.send_new_property(alignSwitch)
            wasExecuted = True
        return wasExecuted
    def clearAlignmentModel(self):
        wasExecuted = False
        clearSwitch = self.baseDevice.getSwitch('ALIGNMENT_POINTSET_ACTION')
        commitSwitch = self.baseDevice.getSwitch('ALIGNMENT_POINTSET_COMMIT')
        if clearSwitch is not None and commitSwitch is not None:
            INDI.IUResetSwitch(clearSwitch)
            clearSwitch.vp['CLEAR'].s = INDI.ISState.ISS_ON
            self.clientManager.send_new_property(clearSwitch)
            commitSwitch.vp['COMMIT'].s = INDI.ISState.ISS_ON
            self.clientManager.send_new_property(commitSwitch)
            wasExecuted = True
        clearSwitch = self.baseDevice.getSwitch('ALIGNLIST')
        if clearSwitch is not None:
            IUResetSwitch(clearSwitch)
            clearSwitch.vp['ALIGNLISTCLEAR'].s = INDI.ISState.ISS_ON
            self.clientManager.send_new_property(clearSwitch)
            wasExecuted = True
        return wasExecuted
    def getStatus(self):
        EqProp = self.baseDevice.getNumber('EQUATORIAL_EOD_COORD')
        if EqProp is None:
            return TelescopeStatus.MOUNT_ERROR
        if EqProp.s == INDI.IPState.IPS_IDLE:
            if self.inManualMotion:
                return TelescopeStatus.MOUNT_MOVING
            elif self.isParked():
                return TelescopeStatus.MOUNT_PARKED
            else:
                return TelescopeStatus.MOUNT_IDLE
        elif EqProp.s == INDI.IPState.IPS_OK:
            if self.inManualMotion:
                return TelescopeStatus.MOUNT_MOVING
            elif self.inCustomParking:
                self.inCustomParking = False
                self.sendParkingOptionCommand(ParkOptionCommand.PARK_OPTION_CURRENT)
                self.sendParkingOptionCommand(ParkOptionCommand.PARK_OPTION_WRITE_DATA)
                return TelescopeStatus.MOUNT_TRACKING
            else:
                return TelescopeStatus.MOUNT_TRACKING
        elif EqProp.s == INDI.IPState.IPS_BUSY:
            parkSP = self.baseDevice.getSwitch('TELESCOPE_PARK')
            if parkSP is not None and parkSP.s == INDI.IPState.IPS_BUSY:
                return TelescopeStatus.MOUNT_PARKING
            else:
                return TelescopeStatus.MOUNT_SLEWING
        elif EqProp.s == INDI.IPState.IPS_ALERT:
            self.inCustomParking = False
            return TelescopeStatus.MOUNT_ERROR
        return TelescopeStatus.MOUNT_ERROR
    def getStatusString(self, status):
        if status == TelescopeStatus.MOUNT_IDLE:
            return 'Idle'
        if status == TelescopeStatus.MOUNT_PARKED:
            return 'Parked'
        if status == TelescopeStatus.MOUNT_PARKING:
            return 'Parking'
        if status == TelescopeStatus.MOUNT_SLEWING:
            return 'Slewing'
        if status == TelescopeStatus.MOUNT_MOVING:
            return 'Moving ' + self.getManualMotionString()
        if status == TelescopeStatus.MOUNT_TRACKING:
            return 'Tracking'
        if status == TelescopeStatus.MOUNT_ERROR:
            return 'Error'
        return 'Error'
    def getManualMotionString(self):
        movementSP = self.baseDevice.getSwitch('TELESCOPE_MOTION_NS')
        NSMotion = ''
        if movementSP is not None:
            if movementSP.vp['MOTION_NORTH'].s == INDI.ISState.ISS_ON:
                NSMotion = 'N'
            elif movementSP.vp['MOTION_SOUTH'].s == INDI.ISState.ISS_ON:
                NSMotion = 'S'
        movementSP = self.baseDevice.getSwitch('TELESCOPE_MOTION_WE')
        WEMotion = ''
        if movementSP is not None:
            if movementSP.vp['MOTION_WEST'].s == INDI.ISState.ISS_ON:
                WEMotion = 'W'
            elif movementSP.vp['MOTION_EAST'].s == INDI.ISState.ISS_ON:
                WEMotion = 'E'
        return NSMotion + WEMotion
    @pyqtSlot(bool)
    def setTrackEnabled(self, enable):
        trackSP = self.baseDevice.getSwitch('TELESCOPE_TRACK_STATE')
        if trackSP is None:
            return False
        trackON = INDI.IUFindSwitch(trackSP, 'TRACK_ON')
        trackOFF = INDI.IUFindSwitch(trackSP, 'TRACK_OFF')
        if trackON is None or trackOFF is None:
            return False
        trackON.s = INDI.ISState.ISS_ON if enable else INDI.ISState.ISS_OFF
        trackOFF.s = INDI.ISState.ISS_OFF if enable else INDI.ISState.ISS_ON
        self.clientManager.send_new_property(trackSP)
    def isTracking(self):
        return self.getStatus() == TelescopeStatus.MOUNT_TRACKING
    @pyqtSlot(int)
    def setTrackMode(self, index):
        trackModeSP = self.baseDevice.getSwitch('TELESCOPE_TRACK_MODE')
        if trackModeSP is None:
            return False
        if index < 0 or index >= len(trackModeSP.vp):
            return False
        INDI.IUResetSwitch(trackModeSP)
        list(trackModeSP.vp.values())[index].s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(trackModeSP)
        return True
    def getTrackMode(self):
        trackModeSP = self.baseDevice.getSwitch('TELESCOPE_TRACK_MODE')
        if trackModeSP is None:
            return None
        index = INDI.IUFindOnSwitchIndex(trackModeSP)
        return index
    @pyqtSlot(float, float)
    def setCustomTrackRate(self, raRate, deRate):
        trackRateNP = self.baseDevice.getNumber('TELESCOPE_TRACK_RATE')
        if trackRateNP is None:
            return False
        raRateN = INDI.IUFindNumber(trackRateNP, 'TRACK_RATE_RA')
        deRateN = INDI.IUFindNumber(trackRateNP, 'TRACK_RATE_DE')
        if raRateN is None or deRateN is None:
            return False
        raRateN.value = raRate
        deRateN.value = deRate
        self.clientManager.send_new_property(trackRateNP)
        return True
    def getCustomTrackRate(self):
        trackRateNP = self.baseDevice.getNumber('TELESCOPE_TRACK_RATE')
        if trackRateNP is None:
            return (None, None)
        raRateN = INDI.IUFindNumber(trackRateNP, 'TRACK_RATE_RA')
        deRateN = INDI.IUFindNumber(trackRateNP, 'TRACK_RATE_DE')
        if raRateN is None or deRateN is None:
            return (None, None)
        return (raRateN.value, deRateN.value)
    def sendParkingOptionCommand(self, command):
        parkOptionsSp = self.baseDevice.getSwitch('TELESCOPE_PARK_OPTION')
        if parkOptionsSp is None:
            return False
        INDI.IUResetSwitch(parkOptionsSp)
        list(parkOptionsSp.vp.values())[command.value].s = INDI.ISState.ISS_ON
        self.clientManager.send_new_property(parkOptionsSp)
        return True
