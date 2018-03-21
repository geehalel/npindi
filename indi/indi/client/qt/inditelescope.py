from PyQt5.QtCore import pyqtSignal, pyqtSlot
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
        super().processNumber(nvp)
