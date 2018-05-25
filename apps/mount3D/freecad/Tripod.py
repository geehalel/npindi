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
import math

class BaseTripod:
    # Origin: top center of the base cylinder
    origin=FreeCAD.Vector(0,0,0)
    baseradius=60
    baseheight=60
    basechamfer=10
    holderwidth=35
    holderlength=50
    holderheight=32
    holderxshift=baseradius - 5
    holderyshift=-holderlength/2
    holderzshift=-baseheight
    holderspacerlength=32
    holderspacerheight=holderheight
    holderaxisradius=8

    def __init__(self, origin):
        if origin != None: self.origin=origin


    def MakeBaseTripod(self):
        self.basecylinder=Part.makeCylinder(self.baseradius, self.baseheight, self.origin,
                                            FreeCAD.Vector(0,0,-1), 360)
        self.basetripod=self.basecylinder.makeChamfer(self.basechamfer,[self.basecylinder.Edges[2]])
        self.holderbox=Part.makeBox(self.holderwidth, self.holderlength, self.holderheight,
           self.origin+ FreeCAD.Vector(self.holderxshift, self.holderyshift, self.holderzshift), FreeCAD.Vector(0,0,1))
        self.holderbox=self.holderbox.makeFillet((self.holderheight/2)-0.5,
                                                 [self.holderbox.Edges[5], self.holderbox.Edges[7]])
        self.holderspacer=Part.makeBox(self.holderwidth-5, self.holderspacerlength, self.holderspacerheight,
          self.origin+FreeCAD.Vector((self.holderxshift+5, -(self.holderspacerlength / 2),
                                      self.holderzshift)),
                                      #(self.baseheight + self.holderheight) - self.holderspacerheight)),
          FreeCAD.Vector(0,0,1))
        self.holderbox=self.holderbox.cut(self.holderspacer)
        self.holderaxis=Part.makeCylinder(self.holderaxisradius, self.holderlength,
          self.origin+FreeCAD.Vector(self.holderxshift + + self.holderwidth - (self.holderheight/2), -self.holderlength/2,
                                     self.holderzshift + (self.holderheight/2)),
                                     #self.baseheight + self.holderheight - (self.holderwidth/2)),
          FreeCAD.Vector(0,1,0), 360)
        self.holderbox=self.holderbox.fuse(self.holderaxis)
        self.holderleg1=self.holderbox
        self.holderleg2=self.holderleg1.copy()
        self.holderleg2.rotate(self.origin + FreeCAD.Vector(0,0,-self.baseheight),
                                        FreeCAD.Vector(0,0,1), 120.0)
        self.holderleg3=self.holderleg1.copy()
        self.holderleg3.rotate(self.origin + FreeCAD.Vector(0,0,-self.baseheight),
                                        FreeCAD.Vector(0,0,1), 240.0)
        self.basetripod=self.basetripod.fuse(self.holderleg1)
        self.basetripod=self.basetripod.fuse(self.holderleg2)
        self.basetripod=self.basetripod.fuse(self.holderleg3)
        self.shape=self.basetripod
        return self.shape

    def draw(self, baseholdermat):
        if self.shape == None: self.MakeBasetripod()
        basetripodnode=Render.Render.draw(self.shape, baseholdermat)
        rootnode=pivy.coin.SoSeparator()
        rootnode.addChild(basetripodnode)
        return rootnode

class Leg:
    # Origin: center of the top axis
    origin=FreeCAD.Vector(0,0,0)
    legradius=22.25 # 1.75"
    legheight=1030
    legchamfer=12
    legflat=30
    legflatheight=40
    coneradius=10
    coneheight=30
    axisradius=8

    def __init__(self, origin):
        if origin != None: self.origin=origin

    def MakeLeg(self):
        self.basecylinder=Part.makeCylinder(self.legradius, self.legheight, self.origin + FreeCAD.Vector(0,0,(self.legradius)),
                                            FreeCAD.Vector(0,0,-1), 360)
        self.basecylinder=self.basecylinder.makeChamfer(self.legchamfer, [self.basecylinder.Edges[0]])
        self.flatbox=Part.makeBox( 2*self.legradius, self.legradius - (self.legflat/2), self.legflatheight,
                                  self.origin +FreeCAD.Vector(-self.legradius, self.legflat/2, -self.legflatheight + (self.legradius)))
        self.basecylinder=self.basecylinder.cut(self.flatbox)
        self.flatbox.translate((0,(-self.legflat/2) - self.legradius,0))
        self.basecylinder=self.basecylinder.cut(self.flatbox)
        #self.basecylinder.check()
        #self.basecylinder=self.basecylinder.makeFillet(self.legradius-5, [self.basecylinder.Edges[6]])
        #self.basecylinder.refine()
        #self.basecylinder=self.basecylinder.makeFillet(self.legradius-5, [self.basecylinder.Edges[11],self.basecylinder.Edges[1]])
        self.legaxis=Part.makeCylinder(self.axisradius, 2*self.legradius, self.origin +FreeCAD.Vector(0,-self.legradius,0),
                                       FreeCAD.Vector(0,1,0), 360)
        self.basecylinder=self.basecylinder.cut(self.legaxis)


        self.conecylinder=Part.makeCylinder(self.coneradius, self.coneheight, self.origin +FreeCAD.Vector(0,0,- (self.legheight - (self.legradius))),
                                            FreeCAD.Vector(0,0,-1), 360)
        self.conecylinder=self.conecylinder.makeFillet(self.coneradius, [self.conecylinder.Edges[0]])
        self.basecylinder=self.basecylinder.fuse(self.conecylinder)
        theta = math.acos((850 - 60 + 32 / 2) / (self.legheight - self.legradius))
        self.basecylinder.rotate(self.origin, FreeCAD.Vector(0,1,0), - math.degrees(theta))
        #print(math.degrees(theta))
        self.shape=self.basecylinder
        return self.shape

    def draw(self, legmat):
        if self.shape == None: self.MakeLeg()
        legnode=Render.Render.draw(self.shape, legmat)
        rootnode=pivy.coin.SoSeparator()
        rootnode.addChild(legnode)
        return rootnode
