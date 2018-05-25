# coding: utf8
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

import sys

FREECADPATH = ['/usr/lib64/freecad/lib', '/usr/lib/freecad/lib'] # path to your FreeCAD.so or FreeCAD.dll file
sys.path.extend(FREECADPATH)

import Simulator

from pivy.sogui import SoGui, SoGuiExaminerViewer
#from pivy.coin import *


try:
    import FreeCAD
except ValueError:
    print('FreeCAD library not found. Please check the FREECADPATH variable in this script is correct')
    sys.exit(1)
s=None
s=Simulator.Simulator()
s.Build()

myWindow=SoGui.init("EQMount view")
if myWindow == None: sys.exit(1)

viewer=SoGuiExaminerViewer(myWindow)
viewer.setTitle("EQMount view")
viewer.setSceneGraph(s.scene)
#viewer.setSize((800,600))
viewer.show()
SoGui.show(myWindow)

# launch python2 -i display.py to get a python shell with the scene defined in Simulator
## Export stl files
# up is Zaxis in FReecad, it is Y axis in QT3D, model should be rotated -90.0 towards X axis in Qt3D
# rotate legs directly in QT3D around Y
# s.leg1.shape.exportStl('leg.stl')
# s.bt.shape.exportStl('basetripod.stl')
# s.bh.shape.exportStl('baseholder.stl')
# s.rh.shape.exportStl('rahousing.stl')
# s.ra.shape.exportStl('raaxis.stl')
# s.dh.shape.exportStl('dehousing.stl')
# s.da.shape.exportStl('daaxis.stl')
# s.d.shape.exportStl('dovetail.stl')
# s.r.shape.exportStl('refractor.stl')
# s.c.crayfordspacer.exportStl('crayford-spacer.stl')
# s.c.crayfordcylinder.exportStl('crayford-cylinder.stl')
# s.c.crayfordtube.exportStl('crayford-tube.stl')
## Notice centers of rotations and report them in Qt3D
# s.bh.origin
# s.rh.origin
# s.ra.origin
# s.da.origin
# s.c.origin

## write a scene to disk in OpenInventor format
#o=pivy.coin.SoOutput()
#o.openFile('refractor.iv')
#pivy.coin.SoWriteAction(o).apply(s.scene)
#o.closeFile()
