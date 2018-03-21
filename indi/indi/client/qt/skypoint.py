#from PyQt5.QtPositioning import QGeoCoordinate
import math
import enum

J2000 = 2451545.0
B1950 = 2433282.4235
SIDEREALSECOND = 1.002737909  # number of sidereal seconds in one solar second

class dms:
    class AngleRanges(enum.Enum):
        ZERO_TO_2PI = 0
        MINUSPI_TO_PI = 1
    def __init__(self):
        self.D = float('nan')
    def dms(self, x):
        self.D = float(x)
    def dmsH(self, x):
        self.D = self.dms(x * 15.0)
    def setD(self, d, m, s, ms = 0):
        self.D = float(abs(d)) + (float(m) +(float(s) + float(ms)/1000.0)/60.0)/60.0
        if d < 0:
            self.D = -1.0 * self.D
    def setH(self, h, m, s, ms=0.0):
        self.D = 15.0 * (float(abs(d)) + (float(m) +(float(s) + float(ms)/1000.0)/60.0)/60.0)
        if h < 0:
            self.D = -1.0 * self.D
    def setRadians(self, Rad):
        self.dms(math.degrees(Rad))
    def reduce(self):
        if math.isnan(self.D):
            return self.dms(0)
        return self.dms(self.D - (360.0 * math.floor(self.D/360.0)))
    def reduceToRange(self, rng):
        if math.isnan(self.D):
            return
        if rng == AngleRanges.MINUSPI_TO_PI:
            self.D -= (360.0 * math.floor((self.D + 180.0) / 360.0))
        else:
            self.D -= (360.0 * math.floor(self.D / 360.0))
    def SinCos(self):
        return (math.sin(math.radians(self.D)), math.cos(math.radians(self.D)))
    def radians(self):
        return math.radians(self.D)
    def cos(self):
        return math.cos(math.radians(self.D))
    def sin(self):
        return math.sin(math.radians(self.D))
class SkyPoint:
    def __init__(self, r = None, d = None):
        self.RA0 = self.RA = dms()
        self.Dec0 = self.Dec = dms()
        self.lastPrecessJD = J2000
        if r is not None and d is not None:
            if isinstance(r, dms) and isinstance(d, dms):
                self.RA0 = self.RA = r
                self.Dec0 = self.Dec = d
            elif isinstance(r, float) and isinstance(d, float):
                self.RA0.dmsH(r); self.RA.dmsH(r)
                self.Dec0 = self.Dec = d
