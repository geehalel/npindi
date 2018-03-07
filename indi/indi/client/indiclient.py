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

from indi.INDI import *
from indi.indibase.baseclient import BaseClient
from indi.client.indieventqueuemediator import IndiEventQueueMediator
from indi.client.indievent import IndiEventType, IndiEvent

class IndiClient(BaseClient):
    def __init__(self, host='localhost', port=7624, logger=None, mediator=None):
        super(IndiClient, self).__init__(host=host, port=port, mediator=None, logger=logger)
        if mediator is None:
            self.mediator=IndiEventQueueMediator(logger=self.logger)
        else:
            self.mediator=mediator
    def wait_indi_event(self, indi_event, timeout=2):
        event=self.mediator.queue_wait_event(indi_event, timeout)
        if not event:
            self.logger.warn('wait_indi_event timeout('+str(timeout)+'s): '+str(indi_event))
        return event
    def wait_device(self, device_name, connect=False, timeout=2):
        if not device_name or device_name=='':
            self.logger.warn('wait_device: device undefined')
            return INDI.INDI_ERROR_TYPE.INDI_DEVICE_NOT_FOUND
        if not device_name in self.devices:
            indi_event=IndiEvent(IndiEventType.NEW_DEVICE, device=device_name, value=None)
            self.wait_indi_event(indi_event, timeout)
        if connect:
            if not INDI.SP.CONNECTION in self.devices[device_name].properties:
                indi_event=IndiEvent(IndiEventType.NEW_PROPERTY, device=device_name, value=INDI.SP.CONNECTION)
                self.wait_indi_event(indi_event, timeout)
            self.connect_device(device_name)
    def wait_properties(self, device, propname_list, timeout=2):
        if type(device) == str: device = self.devices[device]
        for pname in propname_list:
            if pname in device.properties: propname_list.remove(pname)
        while propname_list:
            indi_event=IndiEvent(IndiEventType.NEW_PROPERTY, device=device)
            self.logger.debug('wait event', str(indi_event))
            event=self.wait_indi_event(indi_event, timeout)
            if not event:
                return
            self.logger.debug('got event', str(event))
            if event.value.name in propname_list:
                self.logger.debug('catch property', str(event.value_name))
                propname_list.remove(event.value.name)
                
