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

from PyQt5.QtGui import QColor, QVector3D
from PyQt5.QtCore import QObject, pyqtSlot

from PyQt5.Qt3DExtras import Qt3DWindow, QOrbitCameraController
from PyQt5.Qt3DCore import QEntity

from world3D import World3D
from model3D import Model3D
from cameracontroller import CameraController
from indi.INDI import *
from indi.client.qt.skypoint import SkyPoint

class View3D(QObject):
    _default_clear_color = QColor(97, 97, 99)
    def __init__(self, parent=None):
        super().__init__()
        self.window = Qt3DWindow(parent)
        #self.window.show()
        self.setClearColor(View3D._default_clear_color)
        self.rootEntity = QEntity()
        self.world = World3D(self.rootEntity)
        self.model = Model3D(self.rootEntity)
        self.model.setWorld(self.world)
        self.initialiseCamera()
        self.window.setRootEntity(self.rootEntity)
        self.scope = None
    def setClearColor(self, color):
        self.clearColor = color
        self.window.defaultFrameGraph().setClearColor(self.clearColor)
    def initialiseCamera(self):
        # Camera.
        self.window.camera().lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 100000.0)
        self.window.camera().setPosition(QVector3D(0.0, 1750.0, -3000.0))
        self.window.camera().setViewCenter(QVector3D(0.0, 1000.0, 0.0))
        #camera.setUpVector(QVector3D(0.0, 0.0, 1.0))
        # For camera controls.
        self.camController = QOrbitCameraController(self.rootEntity)
        #camController = Qt3DExtras.QFirstPersonCameraController(scene)
        #self.camController = CameraController(self.rootEntity)
        self.camController.setLinearSpeed(500.0)
        self.camController.setLookSpeed(180.0)
        self.camController.setCamera(self.window.camera())
    def setLatitude(self, latitude):
        self.world.setLatitude(latitude)
        self.model.setLatitude(latitude)
    def setLongitude(self, longitude):
        self.world.setLongitude(longitude)
        self.model.setLongitude(longitude)
    def setTelescope(self, gdi):
        if self.scope is not None:
            return
        self.scope = gdi
        geo_coord = self.scope.getProperty('GEOGRAPHIC_COORD')
        lat = INDI.IUFindNumber(geo_coord, 'LAT')
        lon = INDI.IUFindNumber(geo_coord, 'LONG')
        self.setLatitude(lat.value)
        self.setLongitude(lon.value)
        prop_utc = self.scope.getProperty('TIME_UTC')
        utc = INDI.IUFindText(prop_utc, 'UTC')
        time_utc = INDI.f_scan_sexa(utc.text.split('T')[1])*15.0
        print('UTC', utc.text, time_utc)
        self.pierside = self.scope.getProperty('TELESCOPE_PIER_SIDE')
        self.scope.newCoord.connect(self.setCoord)
    @pyqtSlot(SkyPoint)
    def setCoord(self, skypoint):
        pon = INDI.IUFindOnSwitch(self.pierside)
        p = 'PIER_WEST' if  pon.name == 'PIER_WEST' else 'PIER_EAST'
        self.model.setCoord(skypoint, p)
    def removeTelescope(self):
        if self.scope is None:
            return
        self.scope.newCoord.disconnect(self.setCoord)
        self.scope = None
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app=QApplication(sys.argv)
    view = View3D()
    view.setLatitude(50.17)
    view.setLongitude(123.04)
    view.window.show()
    app.exec_()
