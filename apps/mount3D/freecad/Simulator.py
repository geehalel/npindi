#!/usr/bin/freecadcmd
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

from pivy.sogui import *
from pivy.coin import *
import sys

import Telescope
import EqMount
import Tripod
import FreeCAD

import math

class Simulator:
    southernhemisphere=False
    def Build(self):
        #Materials
        self.white=SoBaseColor()
        self.white.rgb=(1,1,1)
        self.blue=SoBaseColor()
        self.blue.rgb=(0,0,1)
        self.red=SoBaseColor()
        self.red.rgb=(1,0,0)
        self.green=SoBaseColor()
        self.green.rgb=(0,1,0)
        self.gray50=SoBaseColor()
        self.gray50.rgb=(0.5,0.5,0.5)
        self.gray70=SoBaseColor()
        self.gray70.rgb=(0.7,0.7,0.7)
        self.gray20=SoBaseColor()
        self.gray20.rgb=(0.2,0.2,0.2)
        self.lensmaterial=SoMaterial()
        self.lensmaterial.diffuseColor=(0, 0, 0.2)
        self.lensmaterial.shininess=0.8
        self.lensmaterial.transparency=0.7
        self.stainless=SoMaterial()
        self.stainless.diffuseColor=(0.572, 0.579, 0.598)
        self.stainless.specularColor=(1.0, 1.0, 0.984)
        self.stainless.shininess=0.8
        self.stainless.transparency=0.0

        #Tripod
        self.roottripod = SoSeparator()
        self.bt=Tripod.BaseTripod(None)
        self.bt.origin=FreeCAD.Vector(0,0,850)
        self.bt.MakeBaseTripod()
        self.rootbasetripod=self.bt.draw(self.gray20)
        self.leg1=Tripod.Leg(self.bt.origin+FreeCAD.Vector(self.bt.holderxshift + self.bt.holderlength/2, 0, -(self.bt.baseheight - self.bt.holderheight/2)))
        self.leg1.MakeLeg()
        self.rootleg1=self.leg1.draw(self.stainless)
        self.roottripod.addChild(self.rootbasetripod)
        self.roottripod.addChild(self.rootleg1)
        self.leg2 = Tripod.Leg(self.bt.origin+FreeCAD.Vector(self.bt.holderxshift + self.bt.holderlength/2, 0, -(self.bt.baseheight - self.bt.holderheight/2)))
        self.leg2.MakeLeg()
        self.rootleg2 = self.leg2.draw(self.stainless)
        self.leg2node = SoSeparator()
        self.leg2rot = SoTransform()
        self.leg2rot.rotation.setValue(SbVec3f(0,0,1), math.radians(120.0))
        self.leg2node.addChild(self.leg2rot)
        self.leg2node.addChild(self.rootleg2)
        self.roottripod.addChild(self.leg2node)
        self.leg3 = Tripod.Leg(self.bt.origin+FreeCAD.Vector(self.bt.holderxshift + self.bt.holderlength/2, 0, -(self.bt.baseheight - self.bt.holderheight/2)))
        self.leg3.MakeLeg()
        self.rootleg3 = self.leg3.draw(self.stainless)
        self.leg3node = SoSeparator()
        self.leg3rot = SoTransform()
        self.leg3rot.rotation.setValue(SbVec3f(0,0,1), math.radians(240.0))
        self.leg3node.addChild(self.leg3rot)
        self.leg3node.addChild(self.rootleg3)
        self.roottripod.addChild(self.leg3node)

        #Mount
        self.bh=EqMount.Baseholder(None)
        self.rh=EqMount.Rahousing(None)
        self.ra=EqMount.Raaxis(None)
        self.dh=EqMount.Dehousing(None)
        self.da=EqMount.Deaxis(None)
        self.bh.origin=self.bt.origin
        self.rh.origin=self.bh.origin + FreeCAD.Vector(self.bh.holderxshift+(self.bh.holderwidth/2),
                        0,
                        self.bh.baseheight + self.bh.holderheight - (self.bh.holderwidth/2))
        self.ra.origin=self.rh.origin + FreeCAD.Vector(self.rh.rahousingxshift + self.rh.rahousinglength,
                           0, self.rh.raaxisshift)
        self.dh.origin=self.ra.origin + FreeCAD.Vector(self.ra.racylinderlength, 0, 0)
        self.deaxiszshift=self.dh.deboxheight + self.dh.deboxzshift + \
            self.dh.deconelength + self.dh.decylinderlength
        self.da.origin=self.dh.origin + FreeCAD.Vector(self.dh.deaxisxshift, 0, self.deaxiszshift)

        self.bh.MakeBaseholder()
        self.rootbaseholder=self.bh.draw(self.gray50)
        self.rh.MakeRahousing()
        self.rootrahousing=self.rh.draw(self.gray50)
        self.ra.MakeRaaxis()
        self.rootraaxis=self.ra.draw(self.gray50, self.white)
        self.dh.MakeDehousing()
        self.rootdehousing=self.dh.draw(self.gray50)
        self.da.MakeDeaxis()
        self.rootdeaxis=self.da.draw(self.gray50, self.white, self.gray70)

        #Scope
        self.d=Telescope.Dovetail(None)
        self.r=Telescope.Refractor(None)
        self.c=Telescope.Crayford(None)
        self.d.origin=self.da.origin + FreeCAD.Vector(0,0,self.da.decylinderlength)
        self.r.origin=self.d.origin+FreeCAD.Vector(0,0,self.d.baseheight + self.d.coilradius)
        self.c.origin=self.r.origin+FreeCAD.Vector(-self.r.tubelength / 2)

        self.d.MakeDovetail()
        self.rootdovetail=self.d.draw(self.green, self.gray50)
        self.r.MakeRefractor()
        self.rootrefractor=self.r.draw(self.white, self.white, self.lensmaterial)
        self.c.MakeCrayford()
        self.rootcrayford=self.c.draw(self.gray50, self.red, self.white)



        # Assemble part components including rotation/transform nodes
        self.scene=SoSeparator()
        self.scene.addChild(self.roottripod)
        self.rotationazimuth=SoTransform()
        self.rotationazimuth.rotation.setValue(SbVec3f(0,0,1), math.radians(0.0))
        self.rotationazimuth.center=self.bh.origin
        self.azimuthnode=SoSeparator()
        self.azimuthnode.addChild(self.rotationazimuth)
        self.scene.addChild(self.azimuthnode)
        self.azimuthnode.addChild(self.rootbaseholder)
        self.rotationlatitude=SoTransform()
        self.rotationlatitude.rotation.setValue(SbVec3f(0,1,0), math.radians(0.0))
        self.rotationlatitude.center=self.rh.origin
        self.latitudenode=SoSeparator()
        self.latitudenode.addChild(self.rotationlatitude)
        self.azimuthnode.addChild(self.latitudenode)

        self.latitudenode.addChild(self.rootrahousing)
        self.rotationra=SoTransform()
        self.rotationra.rotation.setValue(SbVec3f(1,0,0), math.radians(0))
        self.rotationra.center=self.ra.origin
        self.ranode=SoSeparator()
        self.ranode.addChild(self.rotationra)
        self.latitudenode.addChild(self.ranode)

        self.ranode.addChild(self.rootraaxis)
        self.ranode.addChild(self.rootdehousing)
        self.rotationde=SoTransform()
        self.rotationde.rotation.setValue(SbVec3f(0,0,1), math.radians(0))
        self.rotationde.center=self.da.origin
        self.denode=SoSeparator()
        self.denode.addChild(self.rotationde)
        self.ranode.addChild(self.denode)

        self.denode.addChild(self.rootdeaxis)

        self.denode.addChild(self.rootdovetail)
        self.denode.addChild(self.rootrefractor)
        self.denode.addChild(self.rootcrayford)

        # All angles in degrees
    def setLatitude(self, latitude):
        self.latitude=latitude
        self.rotationlatitude.rotation.setValue(SbVec3f(0,1,0), math.radians(-abs(latitude)))
        if (latitude >= 0.0):
            self.southernhemisphere=False
        else:
            self.southernhemisphere=True
    def setAzimuth(self, azimuth):
        self.azimuth = azimuth
        self.rotationazimuth.rotation.setValue(SbVec3f(0,0,1), math.radians(azimuth))
    def setRAangle(self, raangle):
        self.rotationra.rotation.setValue(SbVec3f(1,0,0), math.radians(raangle))

    def setDEangle(self, deangle):
        self.rotationde.rotation.setValue(SbVec3f(0,0,1), math.radians(deangle))

    def setFocuserangle(self, focangle):
        self.c.rotationcrayford.rotation.setValue(SbVec3f(1,0,0), math.radians(focangle))

    def setFocuserposition(self, position):
        self.c.translationfocus.translation.setValue([-position, 0, 0])

    def Show(self):
        # 3D Window
        self.myWindow=SoGui.init("EQ Simulator")
        if self.myWindow == None: sys.exit(1)

        self.viewer=SoGuiExaminerViewer(self.myWindow)
        self.viewer.setTitle("EQ Simulator")
        self.viewer.setSceneGraph(self.scene)
        #self.viewer.setSize((800,600))
        self.viewer.show()
        SoGui.show(self.myWindow)

    def Embed(self, widget):
         self.viewer=SoGuiExaminerViewer(widget)
         self.viewer.setSceneGraph(self.scene)
