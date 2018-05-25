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

import FreeCAD
import Part
import pivy.coin
import Render

class Baseholder:
    # Origin: bottom center of the base cylinder
    origin=FreeCAD.Vector(0,0,0)
    baseradius=50
    baseheight=30
    basefillet=2
    holderwidth=60
    holderlength=66
    holderheight=75
    holderxshift=-25
    holderyshift=-33
    holderspacerlength=30
    holderspacerheight=60
    holderaxisradius=10

    def __init__(self, origin):
        if origin != None: self.origin=origin


    def MakeBaseholder(self):
        self.basecylinder=Part.makeCylinder(self.baseradius, self.baseheight, self.origin,
                                            FreeCAD.Vector(0,0,1), 360)
        self.base=self.basecylinder.makeFillet(self.basefillet,[self.basecylinder.Edges[0]])
        self.holderbox=Part.makeBox(self.holderwidth, self.holderlength, self.holderheight,
           self.origin+ FreeCAD.Vector(self.holderxshift, self.holderyshift, self.baseheight), FreeCAD.Vector(0,0,1))
        self.holderbox=self.holderbox.makeFillet((self.holderwidth/2)-0.5,
                                                 [self.holderbox.Edges[1], self.holderbox.Edges[5]])
        self.holderspacer=Part.makeBox(self.holderwidth, self.holderspacerlength, self.holderspacerheight,
          self.origin+FreeCAD.Vector((self.holderxshift, -(self.holderspacerlength / 2),
                                      (self.baseheight + self.holderheight) - self.holderspacerheight)),
          FreeCAD.Vector(0,0,1))
        self.holderbox=self.holderbox.cut(self.holderspacer)
        self.holderaxis=Part.makeCylinder(self.holderaxisradius, self.holderlength,
          self.origin+FreeCAD.Vector(self.holderxshift + (self.holderwidth/2), -self.holderlength/2,
                                     self.baseheight + self.holderheight - (self.holderwidth/2)),
          FreeCAD.Vector(0,1,0), 360)
        self.holderbox=self.holderbox.fuse(self.holderaxis)
        self.baseholder=self.base.fuse(self.holderbox)
        self.shape=self.baseholder
        return self.shape

    def draw(self, baseholdermat):
        if self.shape == None: self.MakeBaseholder()
        baseholdernode=Render.Render.draw(self.baseholder, baseholdermat)
        rootnode=pivy.coin.SoSeparator()
        rootnode.addChild(baseholdernode)
        return rootnode

class Rahousing:
    # Origin: center of the latitude axis
    origin=FreeCAD.Vector(0,0,0)
    latitudeaxisradius=30
    latitudeaxisholeradius=6
    latitudeboxwidth=50
    latitudeboxlength=60
    latitudeboxheight=85
    latitudeboxxshift=-10
    latitudeboxyshift=-latitudeboxlength/2
    latitudeboxzshift=-20
    latitudeboxaxisradius=33
    latitudeboxaxislength=30
    rahousingradius=45
    rahousinglength=55
    rahousingxshift=40
    raconeradius=32.5
    raconelength=45
    raaxisshift=80
    raaxisradius=15

    def __init__(self, origin):
        if origin != None: self.origin=origin


    def MakeRahousing(self):
        self.latitudeaxis=Part.makeCylinder(self.latitudeaxisradius, self.latitudeboxaxislength,
          self.origin+FreeCAD.Vector(0, -self.latitudeboxaxislength/2, 0), FreeCAD.Vector(0,1,0), 360)
        self.latitudeaxishole=Part.makeCylinder(self.latitudeaxisholeradius, self.latitudeboxlength,
          self.origin+FreeCAD.Vector(0, -self.latitudeboxlength/2, 0), FreeCAD.Vector(0,1,0), 360)
        self.latitudebox=Part.makeBox(self.latitudeboxwidth, self.latitudeboxlength, self.latitudeboxheight,
          self.origin+FreeCAD.Vector(self.latitudeboxxshift, self.latitudeboxyshift, self.latitudeboxzshift),
           FreeCAD.Vector(0,0,1))
        self.latitudebox=self.latitudebox.cut(
             Part.makeCylinder(self.latitudeboxaxisradius, (self.latitudeboxlength-self.latitudeboxaxislength)/2,
                 self.origin+FreeCAD.Vector(0, self.latitudeboxaxislength/2, 0), FreeCAD.Vector(0,1,0), 360))
        self.latitudebox=self.latitudebox.cut(
             Part.makeCylinder(self.latitudeboxaxisradius, (self.latitudeboxlength-self.latitudeboxaxislength)/2,
                 self.origin+FreeCAD.Vector(0, -self.latitudeboxlength/2, 0), FreeCAD.Vector(0,1,0), 360))
        self.latitudebox=self.latitudebox.cut(
             Part.makeBox(self.latitudeboxaxisradius, (self.latitudeboxlength-self.latitudeboxaxislength)/2,
                          self.latitudeboxaxisradius,
                          self.origin+FreeCAD.Vector(0, -self.latitudeboxlength/2, -self.latitudeboxaxisradius),
                          FreeCAD.Vector(0,0,1)))
        self.latitudebox=self.latitudebox.cut(
             Part.makeBox(self.latitudeboxaxisradius, (self.latitudeboxlength-self.latitudeboxaxislength)/2,
                          self.latitudeboxaxisradius,
                          self.origin+FreeCAD.Vector(0,self.latitudeboxaxislength / 2 , -self.latitudeboxaxisradius),
                          FreeCAD.Vector(0,0,1)))

        self.latitudeaxis=self.latitudeaxis.fuse(self.latitudebox)
        self.latitudeaxis=self.latitudeaxis.cut(self.latitudeaxishole)

        self.raaxis=Part.makeCylinder(self.rahousingradius, self.rahousinglength,
          self.origin+FreeCAD.Vector(self.rahousingxshift, 0, self.raaxisshift), FreeCAD.Vector(1,0,0), 360)
        self.racone=Part.makeCone(self.raconeradius, self.rahousingradius, self.raconelength,
          self.origin+FreeCAD.Vector(self.rahousingxshift-self.raconelength, 0, self.raaxisshift),
           FreeCAD.Vector(1,0,0), 360)
        self.racone=self.racone.fuse(Part.makeCylinder(self.raconeradius, 10,
          self.origin+FreeCAD.Vector(self.rahousingxshift-self.raconelength-10, 0, self.raaxisshift),
           FreeCAD.Vector(1,0,0), 360))
        self.raaxis=self.raaxis.fuse(self.racone)
        self.raaxis=self.raaxis.cut(
             Part.makeCylinder(self.raaxisradius, self.rahousinglength+self.raconelength+10,
               self.origin+FreeCAD.Vector(self.rahousingxshift-self.raconelength-10, 0, self.raaxisshift),
               FreeCAD.Vector(1,0,0), 360))
        self.rahousing=self.raaxis.fuse(self.latitudeaxis)
        self.shape=self.rahousing
        return self.shape

    def draw(self, rahousingmat):
        if self.shape == None: self.MakeRahousing()
        rahousingnode=Render.Render.draw(self.rahousing, rahousingmat)
        rootnode=pivy.coin.SoSeparator()
        rootnode.addChild(rahousingnode)
        return rootnode

class Raaxis:
    # Origin: bottom center of the main cylinder
    origin=FreeCAD.Vector(0,0,0)
    raaxisradius=15
    raaxislength=180
    racylinderradius=45
    racylinderlength=35
    racoordcircleradius=29
    racoordcirclelength=10

    def __init__(self, origin):
        if origin != None: self.origin=origin

    def MakeRaaxis(self):
        self.raaxis=Part.makeCylinder(self.raaxisradius, self.raaxislength,
           self.origin+FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(-1,0,0), 360)
        self.racoord=Part.makeCylinder(self.racoordcircleradius, self.racoordcirclelength,
           self.origin+FreeCAD.Vector(-120, 0, 0), FreeCAD.Vector(1,0,0), 360)
        self.racylinder=Part.makeCylinder(self.racylinderradius, self.racylinderlength,
           self.origin+FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1,0,0), 360)

        self.raaxiscyl=self.raaxis.fuse(self.racylinder)
        self.raaxis=self.raaxiscyl.fuse(self.racoord)
        self.shape=self.raaxis
        return self.shape

    def draw(self, raaxismat, racoordmat):
        if self.shape == None: self.MakeRaaxis()
        raaxisnode=Render.Render.draw(self.raaxiscyl, raaxismat)
        racoordnode=Render.Render.draw(self.racoord, racoordmat)
        rootnode=pivy.coin.SoSeparator()
        rootnode.addChild(raaxisnode)
        rootnode.addChild(racoordnode)
        return rootnode

class Dehousing:
    # Origin: center of the base cylinder
    origin=FreeCAD.Vector(0,0,0)
    debasecylinderradius=45
    debasecylinderlength=10
    decylinderradius=41
    decylinderlength=35
    deconelength=15
    deboxheight=75
    deboxwidth=62
    deboxlength=62
    deboxzshift=-45
    deaxisradius=15
    deaxisxshift=35
    desphereradius=80
    despherexshift=-56
    desphereangle=55.6

    def __init__(self, origin):
        if origin != None:self.origin=origin


    def MakeDehousing(self):
        self.debase=Part.makeCylinder(self.debasecylinderradius, self.debasecylinderlength,
          self.origin+FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1,0,0), 360)
        self.desphere=Part.makeSphere(self.desphereradius, self.origin+FreeCAD.Vector(self.despherexshift,0,0),
           FreeCAD.Vector(1,0,0), self.desphereangle, 90, 360)
        self.debase=self.debase.fuse(self.desphere)

        self.debox=Part.makeBox(self.deboxwidth, self.deboxlength, self.deboxheight,
          self.origin+FreeCAD.Vector(3, -self.deboxlength / 2, self.deboxzshift),  FreeCAD.Vector(0,0,1))
        self.debox=self.debox.makeFillet(self.deboxlength/2 - 0.5, [self.debox.Edges[4],self.debox.Edges[6]])

        self.decone=Part.makeCone(self.deboxlength/2 , self.decylinderradius, self.deconelength,
          self.origin+FreeCAD.Vector(self.deaxisxshift, 0, self.deboxheight + self.deboxzshift),
           FreeCAD.Vector(0,0,1), 310)
        self.decone.rotate(self.origin+FreeCAD.Vector(self.deaxisxshift, 0, self.deboxheight + self.deboxzshift),
           FreeCAD.Vector(0,0,1), -155)
        self.debox=self.debox.fuse(self.decone)

        self.decylinder=Part.makeCylinder(self.decylinderradius, self.decylinderlength,
          self.origin+FreeCAD.Vector(self.deaxisxshift, 0, self.deboxheight + self.deboxzshift + self.deconelength),
          FreeCAD.Vector(0,0,1), 360)
        #self.decylinder=self.decylinder.fuse(self.decone)

        self.dehousing=self.debase.fuse(self.debox)
        self.dehousing=self.dehousing.fuse(self.decylinder)
        self.dehousing=self.dehousing.cut(Part.makeCylinder(self.deaxisradius,
                      self.deboxheight+self.deconelength+self.decylinderlength,
                      self.origin+FreeCAD.Vector(self.deaxisxshift, 0, self.deboxzshift),
                      FreeCAD.Vector(0,0,1), 360))

        self.shape=self.dehousing
        return self.shape

    def draw(self, dehousingmat):
        if self.shape == None: self.MakeDehousing()
        dehousingnode=Render.Render.draw(self.dehousing, dehousingmat)
        rootnode=pivy.coin.SoSeparator()
        rootnode.addChild(dehousingnode)
        return rootnode

class Deaxis:
    # Origin: bottom center of the main cylinder
    origin=FreeCAD.Vector(0,0,0)
    deaxisradius=15
    deaxislength=180
    decylinderradius=41
    decylinderlength=45
    demountholderlength=10
    demountholderwidth=45
    decoordcircleradius=29
    decoordcirclelength=10
    decwaxisradius=10
    decwaxislength=350
    decwscrewradius=27
    decwscrewlength=22
    decwscrewconeradius=15
    decwscrewconelength=28

    def __init__(self, origin):
        if origin != None:self.origin=origin


    def MakeDeaxis(self):
        self.deaxismain=Part.makeCylinder(self.deaxisradius, self.deaxislength,
           self.origin+FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0,0,-1), 360)
        self.decoord=Part.makeCylinder(self.decoordcircleradius, self.decoordcirclelength,
           self.origin+FreeCAD.Vector(0, 0, -120), FreeCAD.Vector(0,0,-1), 360)
        self.decylinder=Part.makeCylinder(self.decylinderradius, self.decylinderlength,
           self.origin+FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0,0,1), 360)
        self.decylinder=self.decylinder.fuse(Part.makeCylinder(self.decylinderradius, self.demountholderlength,
           self.origin+FreeCAD.Vector(0, 0, self.decylinderlength), FreeCAD.Vector(0,0,1), 360))
        self.decylinder=self.decylinder.cut(Part.makeBox(self.decylinderradius*2, self.demountholderwidth,
           self.demountholderlength,
           self.origin+FreeCAD.Vector(-self.decylinderradius, -self.demountholderwidth/2, self.decylinderlength),
            FreeCAD.Vector(0,0,1)))

        self.decw=Part.makeCylinder(self.decwaxisradius, self.decwaxislength,
           self.origin+FreeCAD.Vector(0, 0, -120), FreeCAD.Vector(0,0,-1), 360)
        self.decw=self.decw.fuse(Part.makeCylinder(self.decwscrewradius, self.decwscrewlength,
           self.origin+FreeCAD.Vector(0, 0, -120-self.decoordcirclelength), FreeCAD.Vector(0,0,-1), 360))
        self.decw=self.decw.fuse(Part.makeCone(self.decwscrewradius, self.decwscrewconeradius,
           self.decwscrewconelength,
           self.origin+FreeCAD.Vector(0, 0, -120-self.decoordcirclelength-self.decwscrewlength),
           FreeCAD.Vector(0,0,-1), 360))

        self.deaxis=self.deaxismain.fuse(self.decylinder)
        self.deaxis=self.deaxis.fuse(self.decoord)
        #Qt3D self.deaxis=self.deaxis.fuse(self.decw)
        self.shape=self.deaxis
        return self.shape

    def draw(self, decylindermat,decoordmat, decwmat):
        if self.shape == None: self.MakeDeaaxis()
        deaxismainnode=Render.Render.draw(self.deaxismain, decylindermat)
        decylindernode=Render.Render.draw(self.decylinder, decylindermat)
        decoordnode=Render.Render.draw(self.decoord, decoordmat)
        decwnode=Render.Render.draw(self.decw, decwmat)
        rootnode=pivy.coin.SoSeparator()
        rootnode.addChild(deaxismainnode)
        rootnode.addChild(decylindernode)
        rootnode.addChild(decoordnode)
        rootnode.addChild(decwnode)
        return rootnode

class EQ5:
    # Origin: bottom center of the bas
    origin=FreeCAD.Vector(0,0,0)

    def __init__(self, origin):
        if origin != None: self.origin=origin

    def Makemount(self):
        self.baseholder=Baseholder(self.origin)
        self.baseholder.MakeBaseholder()

        self.rahousingorigin=self.origin + \
          FreeCAD.Vector(self.baseholder.holderxshift+(self.baseholder.holderwidth/2),
                        0,
                        self.baseholder.baseheight + self.baseholder.holderheight - (self.baseholder.holderwidth/2))
        self.rahousing=Rahousing(self.rahousingorigin)
        self.rahousing.MakeRahousing()

        self.raaxisorigin=self.rahousingorigin + \
            FreeCAD.Vector(self.rahousing.rahousingxshift + self.rahousing.rahousinglength,
                           0, self.rahousing.raaxisshift)
        self.raaxis=Raaxis(self.raaxisorigin)
        self.raaxis.MakeRaaxis()

        self.dehousingorigin=self.raaxisorigin + \
            FreeCAD.Vector(self.raaxis.racylinderlength, 0, 0)
        self.dehousing=Dehousing(self.dehousingorigin)
        self.dehousing.MakeDehousing()

        #self.deaxiszshift=self.dehousing.deboxheight + self.dehousing.deboxzshift + \
        #                       self.dehousing.deconelength + self.dehousing.decylinderlength
        #self.deaxisorigin=self.dehousingorigin + \
        #    FreeCAD.Vector(self.dehousing.deaxisxshift, 0, 65)
        #self.deaxis=Deaxis(self.deaxisorigin)
        #self.deaxis.MakeDeaxis()

        self.shape=self.baseholder.shape.fuse(self.rahousing.shape)
        self.shape=self.shape.fuse(self.raaxis.shape)
        self.shape=self.shape.fuse(self.dehousing.shape)
        #self.shape=self.shape.fuse(self.deaxis.shape)
        return self.shape
