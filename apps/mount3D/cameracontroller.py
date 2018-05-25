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

from PyQt5.QtGui import QVector3D
from PyQt5.QtCore import Qt

from PyQt5 import Qt3DExtras
from PyQt5 import Qt3DRender
from PyQt5 import Qt3DLogic
from PyQt5 import Qt3DInput

import math

class CameraController(Qt3DExtras.QOrbitCameraController):
    def __init__(self, parent):
        super().__init__(parent)
        self.frameAction = Qt3DLogic.QFrameAction()
        self.frameAction.triggered.connect(self.mymoveCamera)
        self.addComponent(self.frameAction)
        self.time = 0.0
        self.last = 0.0
        self.calls = 0
        self.kbdevice = Qt3DInput.QKeyboardDevice()
        self.shiftButtonInput = Qt3DInput.QActionInput()
        self.shiftButtonAction = Qt3DInput.QAction()
        self.shiftButtonInput.setButtons([Qt.Key_Shift])
        self.shiftButtonInput.setSourceDevice(self.kbdevice)
        self.shiftButtonAction.addInput(self.shiftButtonInput)

        self.tzposInput = Qt3DInput.QButtonAxisInput()
        self.tzAxis = Qt3DInput.QAxis()
        self.tzposInput.setButtons([Qt.Key_Right])
        self.tzposInput.setScale(1.0)
        self.tzposInput.setSourceDevice(self.kbdevice)
        self.tzAxis.addInput(self.tzposInput)

        self.tznegInput = Qt3DInput.QButtonAxisInput()
        self.tznegInput.setButtons([Qt.Key_Left])
        self.tznegInput.setScale(-1.0)
        self.tznegInput.setSourceDevice(self.kbdevice)
        self.tzAxis.addInput(self.tznegInput)

        self.logicalDevice = Qt3DInput.QLogicalDevice()
        self.logicalDevice.addAction(self.shiftButtonAction)
        self.logicalDevice.addAxis(self.tzAxis)
        self.enabledChanged.connect(self.logicalDevice.setEnabled)

        self.addComponent(self.logicalDevice)
        self.speed = 0.5
    #@pyqtSlot(float)
    def mymoveCamera(self, dt):
        self.time += dt
        self.calls += 1
        if self.time > self.last + 1.0:
            #print('move camera', self.time, self.calls)
            self.calls = 0
            self.last = self.time
        if self.shiftButtonAction.isActive():
            #print(self.tzAxis.value())
            #self.camera().rollAboutViewCenter(self.tzAxis.value() * self.lookSpeed() * dt)
            p = self.camera().position()
            x = p.x()
            y = p.y()
            z = p.z()
            r = math.sqrt(x * x + y * y)
            #print(x, y, z)
            theta = math.atan2(y, x)
            dx = -1.0 * r * self.speed * dt * math.sin(theta) * self.tzAxis.value()
            dy = r * self.speed * dt * math.cos(theta) * self.tzAxis.value()
            self.camera().translateWorld(QVector3D(dx, dy, 0.0), Qt3DRender.QCamera.DontTranslateViewCenter)
