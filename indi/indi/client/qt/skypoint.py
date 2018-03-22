#from PyQt5.QtPositioning import QGeoCoordinate
from indi.client.qt.indicommon import Options
import math
import enum

J2000 = 2451545.0
B1950 = 2433282.4235
SIDEREALSECOND = 1.002737909  # number of sidereal seconds in one solar second

class dms:
    class AngleRanges(enum.Enum):
        ZERO_TO_2PI = 0
        MINUSPI_TO_PI = 1
    def __init__(self, x = None):
        self.D = float('nan')
        if x is not None: self.D = float(x)
    def __add__(self, other):
        if type(other) == int or type(other) == float:
            return dms(self.D + other)
        else:
            return dms(self.D + other.D)
    def __radd__(self, other):
        return dms.__add__(self, other)
    def __sub__(self, other):
        if type(other) == int or type(other) == float:
            return dms(self.D - other)
        else:
            return dms(self.D - other.D)
    def __rsub__(self, other):
        return -dms.__sub__(self, other)
    def __mul__(self, other):
        if type(other) == int or type(other) == float:
            return dms(self.D * other)
        else:
            return dms(self.D * other.D)
    def __rmul__(self, other):
        return dms.__mul__(self, other)
    def __truediv__(self, other):
        if type(other) == int or type(other) == float:
            return dms(self.D / other)
        else:
            return dms(self.D / other.D)
    def __rtruediv__(self, other):
        if type(other) == int or type(other) == float:
            return dms(other / self.D)
        else:
            return dms(other.D / self.D)
    def __neg__(self):
        return dms(-self.D)
    def __eq__(self, other):
        def __lt__(self, other):
            if type(other) == int or type(other) == float:
                return self.D == other
            else:
                return self.D == other.D
    def __lt__(self, other):
        if type(other) == int or type(other) == float:
            return self.D < other
        else:
            return self.D < other.D
    def __gt__(self, other):
        if type(other) == int or type(other) == float:
            return self.D > other
        else:
            return self.D > other.D
    def Degrees(self):
        return self.D
    def Hours(self):
        return self.reduce().Degrees() / 15.0
    def setD(self, x):
        self.D = float(x)
    def setH(self, x):
        self.D = float(x) * 15.0
    def setDms(self, d, m, s, ms = 0):
        self.D = float(abs(d)) + (float(m) +(float(s) + float(ms)/1000.0)/60.0)/60.0
        if d < 0:
            self.D = -1.0 * self.D
    def setHms(self, h, m, s, ms=0.0):
        self.D = 15.0 * (float(abs(d)) + (float(m) +(float(s) + float(ms)/1000.0)/60.0)/60.0)
        if h < 0:
            self.D = -1.0 * self.D
    def setRadians(self, Rad):
        self.D = math.degrees(Rad)
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
    altCrit = -1.0
    def __init__(self, r = None, d = None):
        self.RA0 = dms(-1)
        self.Dec0 =  dms(-1)
        self.RA = self.RA0
        self.Dec = self.Dec0
        self.Alt = dms()
        self.Az = dms()
        self.lastPrecessJD = J2000
        if r is not None and d is not None:
            if isinstance(r, dms) and isinstance(d, dms):
                self.RA0.setD(r.D); self.RA.setD(r.D)
                self.Dec0.setD(d.D); self.Dec.setD(d.D)
            elif isinstance(r, float) and isinstance(d, float):
                self.RA0.setH(r); self.RA.setH(r)
                self.Dec0.setD(d); self.Dec.setD(d)
    def set(self, r, d):
        if not isinstance(r, dms) or not isinstance(d, dms):
            raise ValueError('Skypoint: ra and dec should be dms objects')
        self.RA0.D = self.RA.D = r
        self.Dec0.D = self.Dec.D = d
        self.lastPrecessJD = J2000
    def setRA0(self, r):
        if isinstance(r, dms):
            self.RA0 = r
        elif isinstance(r, float) or isinstance(r, int):
            self.RA0.setH(r)
    def setDec0(self, d):
        if isinstance(d, dms):
            self.Dec0 = d
        elif isinstance(d, float) or isinstance(d, int):
            self.Dec0.setD(d)
    def setRA(self, r):
        if isinstance(r, dms):
            self.RA = r
        elif isinstance(r, float) or isinstance(r, int):
            self.RA.setH(r)
    def setDec(self, d):
        if isinstance(d, dms):
            self.Dec = d
        elif isinstance(d, float) or isinstance(d, int):
            self.Dec.setD(d)
    def setAlt(self, alt):
        if isinstance(alt, dms):
            self.Alt = alt
        elif isinstance(alt, float) or isinstance(alt, int):
            self.Alt.setD(alt)
    def setAz(self, az):
        if isinstance(az, dms):
            self.Az = az
        elif isinstance(az, float) or isinstance(az, int):
            self.Az.setD(az)
    def ra0(self): return self.RA0
    def dec0(self): return self.Dec0
    def ra(self): return self.RA
    def dec(self): return self.Dec
    def az(self): return self.Az
    def alt(self): return self.Alt
    def getLastPrecessJD(self): return self.lastPrecessJD
    def airmass(self): return (1.0 / math.sin(self.alt().radians()))
    def EquatorialToHorizontal(self, lst, lat):
        if not isinstance(lst, dms) or not isinstance(lat, dms):
            raise ValueError('SkyPoint: lst and lat should be dms objects')
        HourAngle = lst - self.ra()
        sinlat, coslat = lat.SinCos()
        sindec, cosdec = self.dec().SinCos()
        sinHA, cosHA = HourAngle.SinCos()
        sinAlt = sindec * sinlat + cosdec * coslat * cosHA
        AltRad = math.asin(sinAlt)
        cosAlt = math.sqrt(1.0 - sinAlt * sinAlt)
        if cosAlt == 0: cosAlt = math.cos(AltRad)
        arg = (sindec - sinlat * sinAlt) / (coslat *cosAlt)
        if arg <= -1.0:
            AzRad = math.pi
        elif arg >= 1.0:
            AzRad = 0.0
        else:
            AzRad = math.acos(arg)
        if sinHA > 0.0:
            AzRad = 2.0 * math.pi - AzRad
        self.Alt.setRadians(AltRad)
        self.Az.setRadians(AzRad)
    def HorizontalToEquatorial(self, lst, lat):
        if not isinstance(lst, dms) or not isinstance(lat, dms):
            raise ValueError('SkyPoint: lst and lat should be dms objects')
        sinlat, coslat = lat.SinCos()
        sinAlt, cosAlt = self.alt().SinCos()
        sinAz, cosAz = self.az().SinCos()
        sinDec = sinAlt * sinlat + cosAlt * coslat * cosAz
        DecRad = math.asin(sinDec)
        cosDec = math.cos(DecRad)
        self.Dec.setRadians(DecRad)
        x = (sinAlt - sinlat * sinDec) / (coslat * cosDec)
        if x < -1.0 and x > -1.000001:
            HARad = math.pi
        elif x > 1.0 and x < 1.000001:
            HARad = 0.0
        elif x < -1.0:
            HARad = math.pi
        elif x > 1.0:
            HARad = 0.0
        else:
            HARad = math.acos(x)
        if sinAz > 0.0:
            HARad = 2 * math.pi - HARad
        self.RA.setRadians(lst.radians() - HARad)
        self.RA.reduceToRange(dms.AngleRanges.ZERO_TO_2PI)
    def apparentCoord(self, jd0, jdf):
        pass
    def altRefracted(self):
        if Options.Instance().value('npindi/useRefraction'):
            return dms(self.refract(self.Alt.Degrees()))
        else:
            return self.Alt
    @staticmethod
    def refractionCorr(alt):
        return 1.02 / math.tan((math.pi/180.0) * (alt + 10.3 /(alt + 5.11))) / 60.0
    def refract(self, alt):
        corrCrit = SkyPoint.refractionCorr(SkyPoint.altCrit)
        if alt > SkyPoint.altCrit:
            return (alt + SkyPoint.refractionCorr(alt))
        else:
            return (alt + corrCrit * (alt + 90.0) / (SkyPoint.altCrit + 90.0))
