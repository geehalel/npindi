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

import collections
import logging
import queue
import asyncio
import time

from indi.indibase.basemediator import BaseMediator
from indi.client.indievent import IndiEventType, IndiEvent

class IndiEventMediator(BaseMediator):
    def __init__(self, logger=None):
        if not logger:
            self.logger=logging.getLogger(self.__class__.__name__)
        else:
            self.logger=logger        
        self.queue=None
    def queue_wait_event(self, indi_event, timeout=None):
        remains=timeout
        start=time.monotonic()
        while True:
            event=self.queue_pop(timeout=remains)
            if not event: return None
            if indi_event.includes(event):
                break
            if timeout:
                remains-=(time.monotonic() - start)
                if remains <= 0:
                    return None
        return event
    def queue_pop_filter(self, indieventfilter=None, timeout=None):
        #return self.queue.popleft()
        found=False
        remains=timeout
        start=time.monotonic()
        while True:
            event=self.queue_pop(timeout=remains)
            if not(indieventfilter) or (indieventfilter and indieventfilter.filter(event)):
                found = True
                break
            if timeout: remains-=(time.monotonic() - start)
        return event
    def queue_empty(self):
        #return len(self.queue) > 0
        return self.queue.empty()
    def new_device(self, device):
        indi_event = IndiEvent(IndiEventType.NEW_DEVICE, device=device)
        self.queue_append(indi_event)
        self.logger.debug('Mediator: queuing ' + str(indi_event))
    def remove_device(self, device):
        indi_event = IndiEvent(IndiEventType.REMOVE_DEVICE, device=device)
        self.queue_append(indi_event)
        self.logger.debug('Mediator: queuing ' + str(indi_event))    
    def new_property(self, iproperty):   
        indi_event = IndiEvent(IndiEventType.NEW_PROPERTY, device=iproperty.device, value=iproperty)
        self.queue_append(indi_event)
        self.logger.debug('Mediator: queuing ' + str(indi_event))
    def remove_property(self, iproperty):   
        indi_event = IndiEvent(IndiEventType.REMOVE_PROPERTY, device=iproperty.device, value=iproperty)
        self.queue_append(indi_event)
        self.logger.debug('Mediator: queuing ' + str(indi_event))
    def new_blob(self, blob):
        indi_event = IndiEvent(IndiEventType.NEW_BLOB, device=blob.bvp.device, value=blob)
        self.queue_append(indi_event)
        self.logger.debug('Mediator: queuing ' + str(indi_event)) 
    def new_switch(self, switch):
        indi_event = IndiEvent(IndiEventType.NEW_SWITCH, device=switch.device, value=switch)
        self.queue_append(indi_event)
        self.logger.debug('Mediator: queuing ' + str(indi_event)) 
    def new_number(self, number):
        indi_event = IndiEvent(IndiEventType.NEW_NUMBER, device=number.device, value=number)
        self.queue_append(indi_event)
        self.logger.debug('Mediator: queuing ' + str(indi_event)) 
    def new_text(self, text):
        indi_event = IndiEvent(IndiEventType.NEW_TEXT, device=text.device, value=text)
        self.queue_append(indi_event)
        self.logger.debug('Mediator: queuing ' + str(indi_event)) 
    def new_light(self, light):
        indi_event = IndiEvent(IndiEventType.NEW_LIGHT, device=light.device, value=light)
        self.queue_append(indi_event)
        self.logger.debug('Mediator: queuing ' + str(indi_event)) 
    def new_message(self, device, message_id):
        indi_event = IndiEvent(IndiEventType.NEW_MESSAGE, device=device, value=message_id)
        self.queue_append(indi_event)
        self.logger.debug('Mediator: queuing ' + str(indi_event)) 
    def server_connected(self):
        indi_event = IndiEvent(IndiEventType.SERVER_CONNECTED)
        self.queue_append(indi_event)
        self.logger.debug('Mediator: queuing ' + str(indi_event)) 
    def server_disconnected(self, exit_code):
        indi_event = IndiEvent(IndiEventType.SERVER_DISCONNECTED)
        self.queue_append(indi_event)
        self.logger.debug('Mediator: queuing ' + str(indi_event)) 

class IndiEventQueueMediator(IndiEventMediator):
    def __init__(self, logger=None):
        super().__init__(logger=logger)
        self.queue = queue.Queue()
    def queue_append(self, event):
        self.queue.put(event)
    def queue_pop(self, timeout=None):
        try:
            event=self.queue.get(timeout=timeout)
        except queue.Empty:
            event=None
        if event: self.queue.task_done()
        return event

class IndiEventAsyncioMediator(IndiEventMediator):
    def __init__(self, logger=None):
        super().__init__(logger=logger)
        self.queue=asyncio.Queue()
    def queue_append(self, event):
        asyncio.run_coroutine_threadsafe(self.queue.put(event), self.queue._loop)
    def queue_pop(self, timeout=None):
        try:
            future = asyncio.wait_for(self.queue.get(), timeout=timeout)
            future = asyncio.ensure_future(future)
            asyncio.get_event_loop().run_until_complete(future)
            event = future.result() 
        except asyncio.TimeoutError:
            event=None
            future.cancel()
        if event: self.queue.task_done()
        return event

class IndiEventDequeMediator(IndiEventMediator):
    def __init__(self, logger=None):
        super().__init__(logger=logger)
        self.queue=collections.deque()
    def queue_append(self, event):
        self.queue.append(event)
    def queue_pop(self, timeout=None):
        remains=timeout
        start=time.monotonic()
        while True:
            try:
                event=self.queue.popleft()
            except IndexError:
                event=None          
            if event:
                break
            if timeout:
                remains-=(time.monotonic() - start)
                if remains <= 0.0:
                    break
                time.sleep(0.001)
        return event
