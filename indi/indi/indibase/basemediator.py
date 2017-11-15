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

class BaseMediator:
    def __init__(self, logger=None):
        if not logger:
            self.logger=logging.getLogger('basemediator')
        else:
            self.logger=logger
    def new_device(self, device):
        self.logger.warn('BaseMediator: new_device: ' + device.name)
    def remove_device(self, device):
        self.logger.warn('BaseMediator: remove_device: ' + device.name)
    def new_property(self, iproperty):
        self.logger.warn('BaseMediator: new_property: ' + iproperty.name)
    def remove_property(self, iproperty):
        self.logger.warn('BaseMediator: remove_property: ' + iproperty.name)
    def new_blob(self, blob):
        self.logger.warn('BaseMediator: new_blob element: ' + blob.name + ' ('+ str(blob.size) +' bytes, '+
                    blob.format + ')in BLOB ' + blob.parent.name)
    def new_switch(self, switch):
        self.logger.warn('BaseMediator: new_switch: ' + switch.name)
    def new_number(self, number):
        self.logger.warn('BaseMediator: new_number: ' + number.name)
    def new_text(self, text):
        self.logger.warn('BaseMediator: new_text: ' + text.name)
    def new_light(self, light):
        self.logger.warn('BaseMediator: new_light: ' + light.name)
    def new_message(self, device, message_id):
        self.logger.warn('BaseMediator: new_message(id=' + str(message_id)+'): ' + device.message_queue(message_id))
    def server_connected(self):
        self.logger.warn('BaseMediator: server_connected')
    def server_disconnected(self, exit_code):
        self.logger.warn('BaseMediator: server_disconnected: ' + str(exit_code))
