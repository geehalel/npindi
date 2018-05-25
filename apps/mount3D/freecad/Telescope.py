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

import FreeCAD
import Part
import pivy.coin
import Render
import math

class Dovetail:
    # Origin: bottom center of the base box
    origin=FreeCAD.Vector(0,0,0)
    basewidth=45
    upperbasewidth=30
    baselength=200
    baseheight=20
    coilradius=75
    coilinnerradius=65
    coillength=40
    coilxshift=60

    def __init__(self, origin):
        if origin != None: self.origin=origin
        self.shape=None

    def MakeDovetail(self):
        self.coilcylinder1=Part.makeCylinder(self.coilradius, self.coillength,
                 self.origin + FreeCAD.Vector(-self.coilxshift-self.coillength, 0, self.baseheight+self.coilradius),
                 FreeCAD.Vector(1,0,0), 360)
        self.coilcylinder1=self.coilcylinder1.cut(
            Part.makeCylinder(self.coilinnerradius, self.coillength,
                 self.origin + FreeCAD.Vector(-self.coilxshift-self.coillength, 0, self.baseheight+self.coilradius),
                 FreeCAD.Vector(1,0,0), 360))
        self.coilcylinder1=self.coilcylinder1.fuse(
            Part.makeBox(self.coillength, self.upperbasewidth, self.coilradius - self.coilinnerradius,
              self.origin + \
              FreeCAD.Vector(-self.coilxshift-self.coillength, -self.upperbasewidth/2, self.baseheight),
              FreeCAD.Vector(0,0,1)))

        self.coilcylinder2=Part.makeCylinder(self.coilradius, self.coillength,
                 self.origin + FreeCAD.Vector(self.coilxshift, 0, self.baseheight+self.coilradius),
                 FreeCAD.Vector(1,0,0), 360)
        self.coilcylinder2=self.coilcylinder2.cut(
            Part.makeCylinder(self.coilinnerradius, self.coillength,
                 self.origin + FreeCAD.Vector(self.coilxshift, 0, self.baseheight+self.coilradius),
                 FreeCAD.Vector(1,0,0), 360))
        self.coilcylinder2=self.coilcylinder2.fuse(
            Part.makeBox(self.coillength, self.upperbasewidth, self.coilradius - self.coilinnerradius,
              self.origin + \
              FreeCAD.Vector(self.coilxshift, -self.upperbasewidth/2, self.baseheight),
              FreeCAD.Vector(0,0,1)))


        self.dovetailpolygon=Part.makePolygon([
            FreeCAD.Vector(-self.baselength/2, self.basewidth/2, 0),
            FreeCAD.Vector(-self.baselength/2, -self.basewidth/2, 0),
            FreeCAD.Vector(-self.baselength/2, -self.upperbasewidth/2, self.baseheight),
            FreeCAD.Vector(-self.baselength/2, self.upperbasewidth/2, self.baseheight),
            FreeCAD.Vector(-self.baselength/2, self.basewidth/2, 0)
            ])
        self.dovetailface=Part.Face(self.dovetailpolygon)
        self.dovetailbase=self.dovetailface.extrude(FreeCAD.Vector(self.baselength, 0, 0))
        self.dovetailbase.translate(self.origin)

        self.dovetail=self.dovetailbase.fuse(self.coilcylinder1)
        self.dovetail=self.dovetail.fuse(self.coilcylinder2)
        self.shape=self.dovetail
        return self.shape

    def draw(self, dovetailmat, coilmat):
        if self.shape == None: self.MakeDovetail()
        dovetailnode=Render.Render.draw(self.dovetail, dovetailmat)
        coilnode1=Render.Render.draw(self.coilcylinder1, coilmat)
        coilnode2=Render.Render.draw(self.coilcylinder2, coilmat)
        rootnode=pivy.coin.SoSeparator()
        rootnode.addChild(dovetailnode)
        rootnode.addChild(coilnode1)
        rootnode.addChild(coilnode2)
        return rootnode

class Refractor:
    # Origin: center of the tube (without dew shield)
    origin=FreeCAD.Vector(0,0,0)
    tuberadius=65
    tubeinnerradius=60
    tubelength=420
    lensradius=61
    lenslength=5
    lensxshift=200
    dewshieldradius=77.5
    dewshieldinnerradius=75
    dewshieldlength=200
    dewshieldxshift=385-210
    dewshieldconelength=10

    def __init__(self, origin):
        if origin != None: self.origin=origin

    def MakeRefractor(self):
        self.tube=Part.makeCylinder(self.tuberadius, self.tubelength,
                 self.origin + FreeCAD.Vector(-self.tubelength/2, 0, 0),
                 FreeCAD.Vector(1,0,0), 360)
        self.tube=self.tube.cut(
            Part.makeCylinder(self.tubeinnerradius, self.tubelength,
                 self.origin + FreeCAD.Vector(-self.tubelength/2, 0, 0),
                 FreeCAD.Vector(1,0,0), 360))

        self.dewshield=Part.makeCylinder(self.dewshieldradius, self.dewshieldlength,
                 self.origin + FreeCAD.Vector(self.dewshieldxshift, 0, 0),
                 FreeCAD.Vector(1,0,0), 360)
        self.dewshield=self.dewshield.cut(
            Part.makeCylinder(self.dewshieldinnerradius, self.dewshieldlength,
                 self.origin + FreeCAD.Vector(self.dewshieldxshift, 0, 0),
                 FreeCAD.Vector(1,0,0), 360))
        self.dewshieldcone=Part.makeCone(self.tuberadius, self.dewshieldradius,
                 self.dewshieldconelength,
                 self.origin + FreeCAD.Vector(self.dewshieldxshift-self.dewshieldconelength, 0, 0),
                 FreeCAD.Vector(1,0,0), 360)
        self.dewshieldcone=self.dewshieldcone.cut(
            Part.makeCylinder(self.tuberadius, self.dewshieldconelength,
                 self.origin + FreeCAD.Vector(self.dewshieldxshift-self.dewshieldconelength, 0, 0),
                 FreeCAD.Vector(1,0,0), 360))
        self.dewshield=self.dewshield.fuse(self.dewshieldcone)

        self.lens=Part.makeCylinder(self.lensradius, self.lenslength,
                 self.origin + FreeCAD.Vector(self.lensxshift, 0, 0),
                 FreeCAD.Vector(1,0,0), 360)

        self.refractor=self.tube.fuse(self.dewshield)
        #Qt3D self.refractor=self.refractor.fuse(self.lens)
        self.shape=self.refractor
        return self.shape

    def draw(self, dewshieldmat, tubemat, lensmat):
        if self.shape == None: self.MakeRefractor()
        dewshieldnode=Render.Render.draw(self.dewshield, dewshieldmat)
        tubenode=Render.Render.draw(self.tube, tubemat)
        lensnode=Render.Render.draw(self.lens, lensmat)
        rootnode=pivy.coin.SoSeparator()
        rootnode.addChild(dewshieldnode)
        rootnode.addChild(tubenode)
        rootnode.addChild(lensnode)
        return rootnode

class Crayford:
    # Origin: center of the crayford cone larger face
    origin=FreeCAD.Vector(0,0,0)
    tubespacerradius=60
    tubespacerlength=10
    crayfordcylinderradius=42
    crayfordcylinderinnerradius=32
    crayfordcylinderlength=120
    crayfordcylinderxshift=-100
    crayfordconeradius=49
    crayfordconelength=40
    crayfordtuberadius=29
    crayfordtubeinnerradius=25.4
    crayfordtubelength=150
    crayfordtubexshiftmin=-12.7
    crayfordboxsize=28
    crayfordboxxshift=-80-(28/2)
    crayfordaxisradius=12
    crayfordaxislength=145
    crayfordwheelradius=21
    crayfordwheellength=18

    def __init__(self, origin):
        if origin != None: self.origin=origin

    def MakeCrayford(self):
        self.crayfordcylinder=Part.makeCylinder(self.crayfordcylinderradius, self.crayfordcylinderlength,
          self.origin+FreeCAD.Vector(self.crayfordcylinderxshift, 0, 0),
          FreeCAD.Vector(1,0,0))
        self.crayfordcone=Part.makeCone(self.crayfordconeradius,self.crayfordcylinderradius, self.crayfordconelength,
          self.origin,
          FreeCAD.Vector(-1,0,0))
        self.crayfordcylinder=self.crayfordcylinder.fuse(self.crayfordcone)

        self.crayfordbox=Part.makeBox(self.crayfordboxsize, 2*self.crayfordcylinderradius, self.crayfordboxsize,
          self.origin + FreeCAD.Vector(self.crayfordboxxshift, -self.crayfordcylinderradius,
                                       -self.crayfordcylinderradius),
          FreeCAD.Vector(0,0,1))
        self.crayfordbox=self.crayfordbox.fuse(
            Part.makeCylinder(self.crayfordaxisradius, self.crayfordaxislength,
              self.origin + FreeCAD.Vector(self.crayfordboxxshift+self.crayfordboxsize/2,
                                           -self.crayfordaxislength/2,
                                           -self.crayfordcylinderradius+self.crayfordboxsize/2),
              FreeCAD.Vector(0,1,0)))
        self.crayfordbox=self.crayfordbox.fuse(
            Part.makeCylinder(self.crayfordwheelradius, self.crayfordwheellength,
              self.origin + FreeCAD.Vector(self.crayfordboxxshift+self.crayfordboxsize/2,
                                           -self.crayfordaxislength/2,
                                           -self.crayfordcylinderradius+self.crayfordboxsize/2),
              FreeCAD.Vector(0,1,0)))
        self.crayfordbox=self.crayfordbox.fuse(
            Part.makeCylinder(self.crayfordwheelradius, self.crayfordwheellength,
              self.origin + FreeCAD.Vector(self.crayfordboxxshift+self.crayfordboxsize/2,
                                           self.crayfordaxislength/2-(self.crayfordwheellength),
                                           -self.crayfordcylinderradius+self.crayfordboxsize/2),
              FreeCAD.Vector(0,1,0)))
        self.crayfordcylinder=self.crayfordcylinder.fuse(self.crayfordbox)

        self.crayfordcylinder=self.crayfordcylinder.cut(
          Part.makeCylinder(self.crayfordcylinderinnerradius, self.crayfordcylinderlength,
          self.origin+FreeCAD.Vector(self.crayfordcylinderxshift, 0, 0),
          FreeCAD.Vector(1,0,0)))

        self.crayfordspacer=Part.makeCylinder(self.tubespacerradius, self.tubespacerlength,
          self.origin,
          FreeCAD.Vector(1,0,0))
        self.crayfordspacer=self.crayfordspacer.cut(
          Part.makeCylinder(self.crayfordcylinderradius, self.tubespacerlength,
          self.origin,
          FreeCAD.Vector(1,0,0)))

        self.crayfordtube=Part.makeCylinder(self.crayfordtuberadius, self.crayfordtubelength,
          self.origin+FreeCAD.Vector(self.crayfordcylinderxshift+self.crayfordtubexshiftmin, 0, 0),
          FreeCAD.Vector(1,0,0))
        self.crayfordtube=self.crayfordtube.cut(
           Part.makeCylinder(self.crayfordtubeinnerradius, self.crayfordtubelength,
          self.origin+FreeCAD.Vector(self.crayfordcylinderxshift+self.crayfordtubexshiftmin, 0, 0),
          FreeCAD.Vector(1,0,0)))

        self.crayford=self.crayfordcylinder.fuse(self.crayfordspacer)
        self.crayford=self.crayford.fuse(self.crayfordtube)
        self.shape=self.crayford
        return self.shape

    def draw(self, cylindermat, tubemat, spacermat):
        if self.shape == None: self.MakeRefractor()
        cylindernode=Render.Render.draw(self.crayfordcylinder, cylindermat)
        tubenode=Render.Render.draw(self.crayfordtube, tubemat)
        spacernode=Render.Render.draw(self.crayfordspacer, spacermat)
        rootnode=pivy.coin.SoSeparator()
        rootnode.addChild(spacernode)
        self.rotationcrayford=pivy.coin.SoTransform()
        self.rotationcrayford.rotation.setValue(pivy.coin.SbVec3f(1,0,0), math.radians(0.0))
        self.rotationcrayford.center=self.origin
        crayfordnode=pivy.coin.SoSeparator()
        crayfordnode.addChild(self.rotationcrayford)
        rootnode.addChild(crayfordnode)
        crayfordnode.addChild(cylindernode)
        self.translationfocus=pivy.coin.SoTransform()
        #self.translationfocus.translation=FreeCAD.Vector(0,0,0)
        self.translationfocus.translation.setValue([0,0,0])
        focusnode=pivy.coin.SoSeparator()
        focusnode.addChild(self.translationfocus)
        focusnode.addChild(tubenode)
        crayfordnode.addChild(focusnode)

        return rootnode
