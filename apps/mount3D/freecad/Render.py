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

import pivy.sogui
import pivy.coin
# bug setBuffer const void *, use a temp file
import tempfile

class Render:

    def __init__(self):
        self.defaultmaterial=pivy.coin.SoBaseColor()
        self.defaultmaterial.rgb=(1,1,1)
        self.defaulttextcolor=pivy.coin.SoBaseColor()
        self.defaulttextcolor.rgb=(1,1,1)

    @staticmethod
    def draw(shape, mat):
        input=pivy.coin.SoInput()
        shapeinventor=shape.writeInventor()
        # bug setBuffer const void *, use a temp file
        tf=tempfile.NamedTemporaryFile()
        tf.write(shapeinventor)
        tf.flush()
        #input.setFilePointer(tf)
        input.openFile(tf.name)
        #input.setBuffer(shapeinventor, len(shapeinventor))

        # SoNode is abstract, so what to use ?
        #rootnode=SoNode()
        #SoDB.read(input, rootnode)
        rootnode=pivy.coin.SoSeparator()
        objnode=pivy.coin.SoSeparator()
        objnode=pivy.coin.SoDB.readAll(input)
        rootnode.addChild(mat)
        rootnode.addChild(objnode)
        input.closeFile()
        return rootnode

    @staticmethod
    def drawdefault(shape):
        return self.draw(obj, Render.defaultmaterial)

    @staticmethod
    def drawtext(self, text, posx, posy, posz, color):
        textnode=SoText2()
        textnode.string="Focus: 89.612 mm"
        texttr=SoTranslation()
        texttr.translation.setValue(posx, posy, posz)
        roottext=SoSeparator()
        roottext.addChild(color)
        roottext.addChild(texttr)
        roottext.addChild(textnode)
        return roottext

    @staticmethod
    def drawtextdefault(self, text, posx, posy, posz):
        return self.drawtext(text, posx, posy, posz, self.defaulttextcolor)
