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

class IndiEventType(enum.Enum):
    NEW_DEVICE = 'NEW_DEVICE'
    REMOVE_DEVICE = 'REMOVE_DEVICE'
    NEW_PROPERTY = 'NEW_PROPERTY'
    REMOVE_PROPERTY = 'REMOVE_PROPERTY'
    NEW_BLOB = 'NEW_BLOB'
    NEW_SWITCH = 'NEW_SWITCH'
    NEW_NUMBER = 'NEW_NUMBER'
    NEW_TEXT = 'NEW_TEXT'
    NEW_LIGHT = 'NEW_LIGHT'
    NEW_MESSAGE = 'NEW_MESSAGE'
    SERVER_CONNECTED = 'SERVER_CONNECTED'
    SERVER_DISCONNECTED = 'SERVER_DISCONNECTED'
    def __str__(self):
        return self.value
class IndiEvent:
    def __init__(self, indi_event_type, device=None, value=None):
        self.type = indi_event_type
        self.device = device
        if type(device) == str or not device:
            self.device_name = device if device else 'None'
        else:
            self.device_name=device.name
        self.value = value
    def __str__(self):
        if self.type == IndiEventType.NEW_BLOB:
            str_value = 'BLOB '+self.value.name+' size='+str(self.value.size)+', format='+self.value.format
        else:
            str_value= str(self.value) if self.value else 'None'
        return '<IndiEvent:'+str(self.type)+ ' device='+self.device_name +\
            ' value=' + str_value +  '>'
    def includes(self, other):
        return (not(self.type) or (other.type and self.type == other.type)) and \
            (not(self.device) or (other.device and self.device == other.device)) and \
            (not(self.value) or (other.value and self.value.name == other.value.name))
class IndiEventFilter:
    def __init__(self, indi_event_types, devices_prop_names):
        self.indi_event_types=indi_event_types
        self.device_prop_names=devices_prop_names
    def filter(self, event):
        if not event: return False
        if not self.device_prop_names and  self.indi_event_types and event.type in self.indi_event_types:
            return True
        if event.device and self.device_prop_names and (event.device.name in self.device_prop_names):
            props=self.device_prop_names[event.device]
            if not props:
                return True
            if event.type in [IndiEventType.NEW_PROPERTY, IndiEventType.REMOVE_PROPERTY,
                              IndiEventType.NEW_BLOB, IndiEventType.NEW_NUMBER, IndiEventType.NEW_TEXT,
                              IndiEventType.NEW_SWITCH, IndiEventType.NEW_LIGHT]:
                event_prop_name=event.value.name
                if event_prop_name in props: return True
        return False
        
