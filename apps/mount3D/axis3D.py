from PyQt5.QtGui import QColor, QVector3D, QFont, QQuaternion, QMatrix3x3
from PyQt5.QtCore import QByteArray

from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DExtras import QDiffuseSpecularMaterial, QTextureMaterial, QText2DEntity, QExtrudedTextMesh
from PyQt5.Qt3DRender import QGeometry, QGeometryRenderer,QAttribute, QBuffer

import math
import struct
FLOAT_SIZE = 4

class Line(QEntity):
    def __init__(self, parent=None, start=QVector3D(0.0, 0.0, 0.0), end = QVector3D(1.0, 0.0, 0.0), color=QColor(255,255,255)):
        super().__init__(parent)
        self.start = start
        self.end = end
        self.color = color
        self.g = QGeometry(self)
        posAttribute = QAttribute(self.g)
        self.vertexBuffer = QBuffer(self.g)
        posAttribute.setName(QAttribute.defaultPositionAttributeName())
        posAttribute.setVertexBaseType(QAttribute.Float)
        posAttribute.setVertexSize(3)
        posAttribute.setAttributeType(QAttribute.VertexAttribute)
        posAttribute.setBuffer(self.vertexBuffer)
        posAttribute.setByteOffset(0)
        #posAttribute.setByteStride(0)
        posAttribute.setByteStride((3) * FLOAT_SIZE) # sizeof(float)
        #posAttribute.setDivisor(1)
        self.g.addAttribute(posAttribute)
        self.g.positionAttribute = posAttribute
        points = QByteArray()
        points.append(struct.pack('f', start.x()))
        points.append(struct.pack('f', start.y()))
        points.append(struct.pack('f', start.z()))
        points.append(struct.pack('f', end.x()))
        points.append(struct.pack('f', end.y()))
        points.append(struct.pack('f', end.z()))
        self.vertexBuffer.setData(points)
        self.g.positionAttribute.setCount(2)
        self.gr = QGeometryRenderer()
        self.gr.setPrimitiveType(QGeometryRenderer.Lines)
        self.gr.setGeometry(self.g)
        self.m = QDiffuseSpecularMaterial()
        self.m.setAmbient(color)
        self.addComponent(self.m)
        self.addComponent(self.gr)

class Axis(QEntity):
    # We may put colors directly in vertex attributes
    # see https://forum.qt.io/topic/72478/qt3d-drawing-simple-geometric-shapes-lines-circles-and-so-on/4
    def __init__(self, parent=None, origin=QVector3D(0.0, 0.0, 0.0), segment = 1.0, colors=(QColor(255,0,0), QColor(0,255,0), QColor(0,0,255))):
        super().__init__(parent)
        self.origin = origin
        self.len = segment
        self.colors = colors
        self.entities = []
        self.entities.append(Line(parent=self, start=origin, end=QVector3D(origin.x()+segment, origin.y(), origin.z()), color=colors[0]))
        self.entities.append(Line(parent=self, start=origin, end=QVector3D(origin.x(), origin.y()+segment, origin.z()), color=colors[1]))
        self.entities.append(Line(parent=self, start=origin, end=QVector3D(origin.x(), origin.y(), origin.z()+segment), color=colors[2]))
        self.transform=QTransform(parent=self)
        self.addComponent(self.transform)
