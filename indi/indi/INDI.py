# Copyright 2017 geehalel@gmail.com
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

import enum
import re
class INDI:
    MAXINDIBUF=49152
    INDIV=b'1.7'
    class SP:
        CONNECTION='CONNECTION'
        DEVICE_PORT='DEVICE_PORT'
        DEVICE_AUTO_SEARCH='DEVICE_AUTO_SEARCH'
        DEVICE_BAUD_RATE='DEVICE_BAUD_RATE'
        DEVICE_TCP_ADDRESS='DEVICE_TCP_ADDRESS'
    class ISState(enum.Enum):
        ISS_OFF = 'Off'
        ISS_ON = 'On'
    class IPState(enum.Enum):
        IPS_IDLE = 'Idle'
        IPS_OK = 'Ok'
        IPS_BUSY = 'Busy'
        IPS_ALERT = 'Alert'
    class ISRule(enum.Enum):
        ISR_1OFMANY='OneOfMany'
        ISR_ATMOST1='AtMostOne'
        ISR_NOFMANY='AnyOfMany'
    class IPerm(enum.Enum):
        IP_RO='ro'
        IP_WO='wo'
        IP_RW='rw'
    class BLOBHandling(enum.Enum):
        B_NEVER = 'Never'
        B_ALSO = 'Also'      
        B_ONLY = 'Only'    
    class INDI_PROPERTY_TYPE(enum.Enum):
        INDI_NUMBER = 'INDI_NUMBER'
        INDI_SWITCH = 'INDI_SWITCH'
        INDI_TEXT = 'INDI_TEXT'
        INDI_LIGHT = 'INDI_LIGHT'
        INDI_BLOB = 'INDI_BLOB'
        INDI_UNKNOWN = 'INDI_UNKNOWN'
    class INDI_ERROR_TYPE(enum.IntEnum):
        INDI_DEVICE_NOT_FOUND    = -1
        INDI_PROPERTY_INVALID    = -2
        INDI_PROPERTY_DUPLICATED = -3
        INDI_DISPATCH_ERROR      = -4
    class DRIVER_INTERFACE(enum.IntEnum):
        GENERAL_INTERFACE   = 0
        TELESCOPE_INTERFACE = (1 << 0)
        CCD_INTERFACE       = (1 << 1)
        GUIDER_INTERFACE    = (1 << 2)
        FOCUSER_INTERFACE   = (1 << 3)
        FILTER_INTERFACE    = (1 << 4)
        DOME_INTERFACE      = (1 << 5)
        GPS_INTERFACE       = (1 << 6)
        WEATHER_INTERFACE   = (1 << 7)
        AO_INTERFACE        = (1 << 8)
        DUSTCAP_INTERFACE   = (1 << 9)
        LIGHTBOX_INTERFACE  = (1 << 10)
        DETECTOR_INTERFACE  = (1 << 11)
        AUX_INTERFACE = (1 << 15)
    def crackIndi(s, c):
        for p in c:
            if s==p.value:
                return p
        return None
    _lf_pattern='[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
    _pattern='('+_lf_pattern+')[^0-9]?('+_lf_pattern+')?[^0-9]?('+_lf_pattern+')?'
    _reg_exp_sexa=re.compile(_pattern)
    def f_scan_sexa(s):
        if not s or s =='': return None
        m=INDI._reg_exp_sexa.match(s)
        if m.lastindex == 1:
            return float(m.group(1))
        elif m.lastindex == 2:
            return float(m.group(1)) + (float(m.group(2))/60.0) 
        elif m.lastindex == 2:
            return float(m.group(1)) + (float(m.group(2))/60.0) + (float(m.group(3))/3600.0)
        else:
            return None
class IText:
    def __init__(self, name, label, text, parent, aux0=None, aux1=None):
        self.name=name
        self.label=label
        self.text=text
        self.tvp=parent
        self.aux0=aux0
        self.aux1=aux1
    def __str__(self):
        return self.text
class INumber:
    def __init__(self, name, label, numformat, minvalue, maxvalue, stepvalue, value, parent, aux0=None, aux1=None):
        self.name=name
        self.label=label
        self.format=numformat
        self.min=minvalue
        self.max=maxvalue
        self.step=stepvalue
        self.value=value
        self.tvp=parent
        self.aux0=aux0
        self.aux1=aux1
    def __str__(self):
        return str(self.value)
class ISwitch:
    def __init__(self, name, label, s, parent, aux=None):
        self.name=name
        self.label=label
        self.s=s
        self.svp=parent
        self.aux=aux
    def __str__(self):
        return self.s.value
class ILight:
    def __init__(self, name, label, s, parent, aux=None):
        self.name=name
        self.label=label
        self.s=s
        self.lvp=parent
        self.aux=aux
    def __str__(self):
        return self.s.value
class IBLOB:
    def __init__(self, name, label, blobformat, blob, bloblen, size, parent, aux0=None, aux1=None, aux2=None):
        self.name=name
        self.label=label
        self.format=blobformat
        self.blob=blob
        self.bloblen=bloblen
        self.size=size
        self.bvp=parent
        self.aux0=aux0
        self.aux1=aux1
        self.aux2=aux2
    def __str__(self):
        return self.blob
class IVectorProperty:
    def __init__(self, device, name, label, group, timeout, state, prop_type, timestamp):
        self.device=device
        self.name=name
        self.label=label
        self.group=group
        self.timeout=timeout
        self.s=state
        self.type=prop_type
        self.vp=dict()
        self.timestamp=timestamp
        self.aux=None
    def __str__(self):
        return '<IVectorProperty: '+(self.name) +', type='+str(self.type.value)+', device='+self.device.name+'>'
