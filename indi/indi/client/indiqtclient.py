# Copyright 2018 geehalel@gmail.com
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


from PyQt5 import QtCore
from indi.INDI import *
from indi.indibase.basedevice import BaseDevice
from indi.indibase.baseclient import BaseClient
from indi.indibase.basemediator import BaseMediator

class IndiQtMediator(BaseMediator, QtCore.QObject):
    newdevice=QtCore.pyqtSignal(BaseDevice)
    removedevice=QtCore.pyqtSignal(BaseDevice)
    newproperty=QtCore.pyqtSignal(IVectorProperty)
    removeproperty=QtCore.pyqtSignal(IVectorProperty)
    newblob=QtCore.pyqtSignal(IBLOB)
    #newblob=QtCore.pyqtSignal(Device, IndiProperty, int)
    newswitch=QtCore.pyqtSignal(IVectorProperty)
    newnumber=QtCore.pyqtSignal(IVectorProperty)
    newtext=QtCore.pyqtSignal(IVectorProperty)
    newlight=QtCore.pyqtSignal(IVectorProperty)
    newmessage=QtCore.pyqtSignal(BaseDevice, int)
    serverconnected=QtCore.pyqtSignal()
    serverdisconnected=QtCore.pyqtSignal(int)

    def __init__(self, logger=None):
        BaseMediator.__init__(self, logger)
        QtCore.QObject.__init__(self)
    def new_device(self, device):
        self.logger.debug('new_device: ' + device.name)
        self.newdevice.emit(device)
    def remove_device(self, device):
        self.logger.debug('remove_device: ' + device.name)
        self.removedevice.emit(device)
    def new_property(self, iproperty):
        self.logger.debug('new_property: ' + iproperty.name)
        self.newproperty.emit(iproperty)
    def remove_property(self, iproperty):
        self.logger.debug('remove_property: ' + iproperty.name)
        self.removeproperty.emit(iproperty)
    def new_blob(self, blob):
        self.logger.debug('new_blob element: ' + blob.name + ' ('+ str(blob.size) +' bytes, '+
                    blob.format + ')in BLOB ' + blob.bvp.name)
        self.newblob.emit(blob)
    def new_switch(self, switch):
        self.logger.debug('new_switch: ' + switch.name)
        self.newswitch.emit(switch)
    def new_number(self, number):
        self.logger.debug('new_number: ' + number.name)
        self.newnumber.emit(number)
    def new_text(self, text):
        self.logger.debug('new_text: ' + text.name)
        self.newtext.emit(text)
    def new_light(self, light):
        self.logger.debug('new_light: ' + light.name)
        self.newlight.emit(light)
    def new_message(self, device, message_id):
        self.logger.debug('new_message(id=' + str(message_id)+'): ' + device.message_queue(message_id))
        self.newmessage.emit(device, message_id)
    def server_connected(self):
        self.logger.debug('server_connected')
        self.serverconnected.emit()
    def server_disconnected(self, exit_code):
        self.logger.debug('server_disconnected: ' + str(exit_code))
        self.serverdisconnected.emit(exit_code)

    
class IndiQtClient(BaseClient):
    def __init__(self, host='localhost', port=7624, logger=None):
        mediator=IndiQtMediator(logger=logger)
        super(IndiQtClient, self).__init__(host=host, port=port, mediator=mediator, logger=logger)
