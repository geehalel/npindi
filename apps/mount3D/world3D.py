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

from PyQt5.QtGui import QColor, QVector3D, QImage, QFont, QQuaternion, QMatrix3x3
from PyQt5.QtCore import QSize, QUrl, QByteArray, QTimer

from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DExtras import QPlaneMesh, QSphereMesh, QCylinderMesh, QDiffuseSpecularMaterial, QTextureMaterial, QText2DEntity, QExtrudedTextMesh
from PyQt5.Qt3DRender import QGeometry, QGeometryRenderer,QAttribute, QBuffer, QTexture2D, QTextureLoader, QMaterial, QEffect, QTechnique, QRenderPass, QShaderProgram, QPointSize, QGraphicsApiFilter, QFilterKey
from PyQt5.QtSvg import QSvgRenderer

import math
import struct
from catalogs import load_bright_star_5
from indi.client.qt.indicommon import getJD, getGAST
FLOAT_SIZE = 4

class DPolynom:
    def __init__(self):
        self.coeffs = None
    def setCoeffs(self, lcoeffs):
        self.coeffs = lcoeffs
    def eval(self, x):
        v = 0.0
        for ic in range(len(self.coeffs) - 1, -1, -1):
            v = x * v + self.coeffs[ic]
        return v
    def derive(self):
        d = DPolynom()
        dc = [i * self.coeffs[i] for i in range(1, len(self.coeffs))]
        d.setCoeffs(dc)
        return d
    def integrate(self):
        ip = DPolynom()
        ipc = [self.coeffs[i] / (i + 1) for i in range(len(self.coeffs))]
        ipc = [0.0] + ipc
        ip.setCoeffs(ipc)
        return ip
    def mul(self, other):
        mp = DPolynom()
        mpc = [0.0 for i in range(len(self.coeffs) + len(other.coeffs))]
        for i in range(len(self.coeffs)):
            for j in range(len(other.coeffs)):
                mpc[i+j] += self.coeffs[i] * other.coeffs[j]
        mp.setCoeffs(mpc)
        return mp
class starMaterial(QMaterial):
    def __init__(self, parent=None):
        super().__init__(parent)
        starEffect = QEffect(self)
        starTechnique = QTechnique(self)
        starRenderPass = QRenderPass(self)
        starShaderProgram = QShaderProgram(self)
        starRenderState = QPointSize(self)
        starShaderProgram.setShaderCode(QShaderProgram.Vertex, QShaderProgram.loadSource(QUrl.fromLocalFile('shaders/pointcloud.vert')))
        starShaderProgram.setShaderCode(QShaderProgram.Fragment, QShaderProgram.loadSource(QUrl.fromLocalFile('shaders/pointcloud.frag')))
        starRenderPass.setShaderProgram(starShaderProgram)
        starRenderState.setSizeMode(QPointSize.Programmable)
        starRenderPass.addRenderState(starRenderState)
        starTechnique.addRenderPass(starRenderPass)
        filterKey = QFilterKey()
        filterKey.setName('renderingStyle')
        filterKey.setValue('forward')
        starTechnique.addFilterKey(filterKey)
        starTechnique.graphicsApiFilter().setApi(QGraphicsApiFilter.OpenGL)
        starTechnique.graphicsApiFilter().setMajorVersion(3)
        starTechnique.graphicsApiFilter().setMinorVersion(3)
        starTechnique.graphicsApiFilter().setProfile(QGraphicsApiFilter.CoreProfile)
        #starTechnique.graphicsApiFilter().setProfile(QGraphicsApiFilter.NoProfile)
        starEffect.addTechnique(starTechnique)
        super().setEffect(starEffect)
class PointGeometry(QGeometry):
    def __init__(self, parent=None):
        super().__init__(parent)
        posAttribute = QAttribute(self)
        self.vertexBuffer = QBuffer(self)
        posAttribute.setName(QAttribute.defaultPositionAttributeName())
        posAttribute.setVertexBaseType(QAttribute.Float)
        posAttribute.setVertexSize(3)
        posAttribute.setAttributeType(QAttribute.VertexAttribute)
        posAttribute.setBuffer(self.vertexBuffer)
        posAttribute.setByteOffset(0)
        #posAttribute.setByteStride(0)
        posAttribute.setByteStride((3 + 1) * FLOAT_SIZE) # sizeof(float)
        #posAttribute.setDivisor(1)
        self.addAttribute(posAttribute)
        self.positionAttribute = posAttribute
        radiusAttribute = QAttribute(self)
        radiusAttribute.setName('radius')
        radiusAttribute.setVertexBaseType(QAttribute.Float)
        radiusAttribute.setVertexSize(1)
        radiusAttribute.setAttributeType(QAttribute.VertexAttribute)
        radiusAttribute.setBuffer(self.vertexBuffer)
        radiusAttribute.setByteOffset(3 * FLOAT_SIZE)
        #posAttribute.setByteStride(0)
        radiusAttribute.setByteStride((3 + 1) * FLOAT_SIZE) # sizeof(float)
        #radiusAttribute.setDivisor(1)
        self.addAttribute(radiusAttribute)
        self.radiusAttribute = radiusAttribute
class World3D():
    """
    Qt3D frame: x axis pointing North, y axis pointing Zenith/pole, z axis pointing East
    Celestial frame: x axis pointing South, y axis pointing East, Z axis pointing Zenith/pole
    """
    # raw first order
    _m_celestial_qt = QMatrix3x3([-1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0])
    # _m_celestial is its proper inverse
    _sky_radius = 50000.0
    def __init__(self, parent=None, jd=None):
        self.rootEntity = QEntity(parent)
        self.skyEntity = QEntity(self.rootEntity)
        self.skyTransform = QTransform()
        self.skyEntity.addComponent(self.skyTransform)
        self.makeHorizontalPlane()
        self.makeEquatorialGrid()
        self.makeHorizontalGrid()
        self.makeMountBasement()
        self.makeCardinals()
        if jd is None:
            jd = getJD()
        self.jd = jd
        print(self.jd)
        #self.makeStars(self.jd)
        self.makeStarsPoints(self.jd)
        self.qtime=QQuaternion()
        self.qlongitude = QQuaternion()
        self.setLatitude(90.0)
        self.setLongitude(0.0)
        self.setGAST(getGAST())
        #self.makeEcliptic()
        self.celestialintervalms = 1 * 1000
        self.celestialacceleration = 1
        self.celestialtimer = QTimer()
        self.celestialtimer.setInterval(self.celestialintervalms / self.celestialacceleration)
        self.celestialtimer.setSingleShot(False)
        self.celestialtimer.timeout.connect(self.updateCeletialTime)
        self.celestialtimer.start()
    def updateCeletialTime(self):
        gast = self.gast + (self.celestialintervalms / 1000) / (60*60)
        self.setGAST(gast)
    def getCelestialTime(self):
        return self.gast + (self.longitude / 15.0)
    def updateSkyTransform(self):
        self.skyTransform.setRotation(self.qlatitude * self.qlongitude * self.qtime)
    def setLatitude(self, latitude):
        self.latitude = latitude
        if self.latitude < 0.0:
            angle = 90.0 - abs(self.latitude)
        else:
            angle = -(90.0 - self.latitude)
        self.qlatitude = QQuaternion.fromAxisAndAngle(QVector3D(0.0, 0.0, 1.0), angle)
        self.updateSkyTransform()
    def setLongitude(self, longitude):
        self.longitude = longitude
        angle = -self.longitude
        self.qlongitude = QQuaternion.fromAxisAndAngle(QVector3D(0.0, 1.0, 0.0), angle)
        self.updateSkyTransform()
    def setGAST(self, gast):
        #print('Setting GAST', gast)
        self.gast = gast
        angle = -self.gast * 360.0 / 24.0
        self.qtime = QQuaternion.fromAxisAndAngle(QVector3D(0.0, 1.0, 0.0), angle)
        self.updateSkyTransform()
    def makeHorizontalPlane(self):
        self.horizontalPlane = QEntity()
        self.horizontalMesh = QPlaneMesh()
        self.horizontalMesh.setWidth(2 * World3D._sky_radius)
        self.horizontalMesh.setHeight(2 * World3D._sky_radius)
        self.horizontalMesh.setMeshResolution(QSize(50, 50))
        #self.horizontalMesh.setMirrored(True)
        #self.horizontalTransform = QTransform()
        #self.horizontalTransform.setMatrix(QTransform.rotateAround(QVector3D(0,0,0), 90.0, QVector3D(1.0, 0.0, 0.0)))
        #self.horizontalTransform.setTranslation(QVector3D(0.0, -10.0, 0.0))
        self.horizontalMat = QDiffuseSpecularMaterial()
        self.horizontalMat.setAmbient(QColor(0, 128, 0))
        #self.horizontalPlane.addComponent(self.horizontalTransform)
        self.horizontalPlane.addComponent(self.horizontalMat)
        self.horizontalPlane.addComponent(self.horizontalMesh)
        self.horizontalPlane.setParent(self.rootEntity)
    def makeEquatorialGrid(self):
        self.equatorialGrid = QEntity()
        self.equatorialMesh = QSphereMesh()
        self.equatorialMesh.setRadius(World3D._sky_radius)
        self.equatorialMesh.setRings(18)
        self.equatorialMesh.setSlices(24)
        self.equatorialMesh.setPrimitiveType(QGeometryRenderer.Lines)
        self.equatorialTransform = QTransform()
        #self.equatorialTransform.setRotationZ(-(90 - 49.29))
        self.equatorialMat = QDiffuseSpecularMaterial()
        self.equatorialMat.setAmbient(QColor(200,0,0))
        self.equatorialGrid.addComponent(self.equatorialTransform)
        self.equatorialGrid.addComponent(self.equatorialMat)
        self.equatorialGrid.addComponent(self.equatorialMesh)
        self.equatorialGrid.setParent(self.skyEntity)
    def makeHorizontalGrid(self):
        self.horizontalGrid = QEntity()
        self.horizontalMesh = QSphereMesh()
        self.horizontalMesh.setRadius(World3D._sky_radius)
        self.horizontalMesh.setRings(18)
        self.horizontalMesh.setSlices(36)
        self.horizontalMesh.setPrimitiveType(QGeometryRenderer.Lines)
        self.horizontalTransform = QTransform()
        self.horizontalTransform.setRotationX(0.0)
        self.horizontalMat = QDiffuseSpecularMaterial()
        self.horizontalMat.setAmbient(QColor(0,0,200))
        self.horizontalGrid.addComponent(self.horizontalTransform)
        self.horizontalGrid.addComponent(self.horizontalMat)
        self.horizontalGrid.addComponent(self.horizontalMesh)
        self.horizontalGrid.setParent(self.rootEntity)
    def makeMountBasement(self):
        # self.svgRenderer = QSvgRenderer()
        # self.svgRenderer.load('compass.svg')
        # self.compass = QImage(self.svgRenderer.defaultSize(), QImage.Format_ARGB32)
        # self.compassTexture = QTexture2D()
        # self.compassTexture.addTextureImage(self.compass)
        self.compassTexture = QTextureLoader()
        self.compassTexture.setMirrored(False)
        self.compassTexture.setSource(QUrl.fromLocalFile('compass.svg.png'))
        self.basementGrid = QEntity()
        # self.basementMesh = QCylinderMesh()
        # self.basementMesh.setRadius(1500.0)
        # self.basementMesh.setLength(10.0)
        # self.basementMesh.setSlices(360)
        self.basementMesh = QPlaneMesh()
        self.basementMesh.setWidth(1500.0)
        self.basementMesh.setHeight(1500.0)
        self.basementMesh.setMeshResolution(QSize(2, 2))
        self.basementTransform = QTransform()
        self.basementTransform.setTranslation(QVector3D(0,20.0,0))
        self.basementTransform.setRotationY(-90.0)
        self.basementMatBack = QDiffuseSpecularMaterial()
        self.basementMatBack.setAmbient(QColor(200,200,228))
        self.basementMat = QTextureMaterial()
        self.basementMat.setTexture(self.compassTexture)
        self.basementGrid.addComponent(self.basementTransform)
        self.basementGrid.addComponent(self.basementMatBack)
        self.basementGrid.addComponent(self.basementMat)
        self.basementGrid.addComponent(self.basementMesh)
        self.basementGrid.setParent(self.rootEntity)
    def makeCardinals(self):
        cardinals = [('North', QVector3D(World3D._sky_radius - 100.0, 20.0, 0.0), (0.0, -90.0, 0.0)),
        ('South', QVector3D(-(World3D._sky_radius - 100.0), 20.0, 0.0), (0.0, 90.0, 0.0)),
        ('East', QVector3D(0.0, 20.0, World3D._sky_radius - 100.0), (0.0, 180.0, 0.0)),
        ('West', QVector3D(0.0, 20.0, -(World3D._sky_radius - 100.0)), (0.0, 0.0, 0.0)),
        ('Zenith', QVector3D(0.0, World3D._sky_radius - 100.0, 0.0), (90.0, 0.0, 0.0)),
        ('Nadir', QVector3D(0.0, -(World3D._sky_radius - 100.0), 0.0), (-90.0, 0.0, 0.0)),]
        font = QFont('Helvetica', 32)
        self.textMat = QDiffuseSpecularMaterial()
        self.textMat.setAmbient(QColor(200,200,228))
        self.cardinals = QEntity()
        for cpoint in cardinals:
            e = QEntity()
            eText = QExtrudedTextMesh()
            eText.setText(cpoint[0])
            eText.setDepth(0.45)
            eText.setFont(font)
            eTransform = QTransform()
            eTransform.setTranslation(cpoint[1])
            eTransform.setRotationX(cpoint[2][0])
            eTransform.setRotationY(cpoint[2][1])
            eTransform.setRotationZ(cpoint[2][2])
            eTransform.setScale(1000.0)
            e.addComponent(self.textMat)
            e.addComponent(eTransform)
            e.addComponent(eText)
            e.setParent(self.cardinals)
        self.cardinals.setParent(self.rootEntity)
    def makeStars(self, jd):
        # star coordinates in J2000.0 equinox,no proper motion
        # transform for precession-nutation as defined by IAU2006
        # see http://www-f1.ijs.si/~ramsak/KlasMeh/razno/zemlja.pdf page 8
        # not accurate for more than +-7000 years
        self.skyJ2000 = QEntity()
        self.transformJ2000 = QTransform()
        m = self.matPrecessNut(jd)
        qPrecessNut = QQuaternion.fromRotationMatrix(m)
        qqt=QQuaternion.fromRotationMatrix(World3D._m_celestial_qt)
        self.transformJ2000.setRotation(qqt*qPrecessNut)
        self.skyJ2000.addComponent(self.transformJ2000)
        radius_mag = [150.0, 100.0, 70.0, 50, 40, 30.0]
        stars = load_bright_star_5('bsc5.dat.gz', True)
        starmat = QDiffuseSpecularMaterial()
        starmat.setAmbient(QColor(255,255,224))
        starmat.setDiffuse(QColor(255,255,224))
        for star in stars:
            e = QEntity()
            eStar = QSphereMesh()
            eradius = radius_mag[int(star['mag'] - 1)] if int(star['mag'] - 1) < 6 else 20.0
            eStar.setRadius(eradius)
            eTransform = QTransform()
            ex = (World3D._sky_radius - 150.0) * math.cos(star['ra']) * math.cos(star['de'])
            ey = (World3D._sky_radius -150.0) * math.sin(star['de'])
            ez = (World3D._sky_radius -150.0) * math.sin(star['ra']) * math.cos(star['de'])
            #print(ex, ey ,ez)
            eTransform.setTranslation(QVector3D(ex, ez, ey))
            e.addComponent(starmat)
            e.addComponent(eTransform)
            e.addComponent(eStar)
            e.setParent(self.skyJ2000)

        self.skyJ2000.setParent(self.skyEntity)
    def makeStarsPoints(self, jd):
        self.skyJ2000 = QEntity()
        self.transformJ2000 = QTransform()
        m = self.matPrecessNut(jd)
        qPrecessNut = QQuaternion.fromRotationMatrix(m)
        qqt=QQuaternion.fromRotationMatrix(World3D._m_celestial_qt)
        self.transformJ2000.setRotation(qqt*qPrecessNut)
        #self.transformJ2000.setRotation(qqt)
        self.skyJ2000.addComponent(self.transformJ2000)
        radius_mag = [150.0, 100.0, 70.0, 50, 40, 30.0]
        stars = load_bright_star_5('bsc5.dat.gz', True)
        starmat = starMaterial()
        #starmat = QDiffuseSpecularMaterial()
        #starmat.setAmbient(QColor(255,255,224))
        #starmat.setDiffuse(QColor(255,255,224))
        print('Star Effect', starmat.effect())
        print('Star Technique', starmat.effect().techniques()[0])
        self.skyJ2000.addComponent(starmat)
        #points = QByteArray(3 * FLOAT_SIZE * len(stars), 'b\x00')
        points = QByteArray()
        for star in stars:
            eradius = radius_mag[int(star['mag'] - 1)] if int(star['mag'] - 1) < 6 else 20.0
            ex = (World3D._sky_radius - 150.0) * math.cos(star['ra']) * math.cos(star['de'])
            ey = (World3D._sky_radius -150.0) * math.sin(star['de'])
            ez = (World3D._sky_radius -150.0) * math.sin(star['ra']) * math.cos(star['de'])
            points.append(struct.pack('f', ex))
            points.append(struct.pack('f', ez))
            points.append(struct.pack('f', ey))
            points.append(struct.pack('f', eradius))
        pointGeometryRenderer = QGeometryRenderer()
        pointGeometry = PointGeometry(pointGeometryRenderer)
        pointGeometry.vertexBuffer.setData(points)
        pointGeometry.positionAttribute.setCount(len(stars))
        pointGeometry.radiusAttribute.setCount(len(stars))
        pointGeometryRenderer.setPrimitiveType(QGeometryRenderer.Points)
        pointGeometryRenderer.setGeometry(pointGeometry)
        #pointGeometryRenderer.setFirstInstance(0)
        pointGeometryRenderer.setInstanceCount(1)
        #pointGeometryRenderer.setVertexCount(len(stars))
        self.skyJ2000.addComponent(pointGeometryRenderer)
        self.skyJ2000.setParent(self.skyEntity)
    def makeEcliptic(self):
        for j in range(-12, 14):
            # ecliptic pole
            skyEcliptic = QEntity()
            transformEcliptic = QTransform()
            m = self.matPrecessNut(2451545.0 + 365.25 * j * 1000)
            mcio = self.matCIOLocator(2451545.0 + 365.25 * j * 1000)
            qEcliptic = QQuaternion.fromRotationMatrix(m)
            qCIO = QQuaternion.fromRotationMatrix(mcio)
            qp=QQuaternion.fromRotationMatrix(World3D._m_celestial_qt)
            transformEcliptic.setRotation(qp*qEcliptic*qCIO)
            skyEcliptic.addComponent(transformEcliptic)
            eclmat = QDiffuseSpecularMaterial()
            eclmat.setAmbient(QColor(255,20,20))
            eclmat.setDiffuse(QColor(255,20,20))
            e = QEntity()
            ePole = QSphereMesh()
            eradius = 300.0
            ePole.setRadius(eradius)
            eTransform = QTransform()
            ex = (World3D._sky_radius - 150.0) * math.cos(math.radians(0.0)) * math.cos(math.radians(90.0))
            ey = (World3D._sky_radius -150.0) * math.sin(math.radians(90.0))
            ez = (World3D._sky_radius -150.0) * math.sin(math.radians(0.0)) * math.cos(math.radians(90.0))
            #print(ex, ey ,ez)
            eTransform.setTranslation(QVector3D(ex, ez, ey))
            e.addComponent(eclmat)
            e.addComponent(eTransform)
            e.addComponent(ePole)
            e.setParent(skyEcliptic)
            skyEcliptic.setParent(self.skyEntity)
    def matPrecessNut(self, jd):
        J2000 = 2451545.0
        t = jd - J2000
        t = t / 36525 #julian century
        x = -0.016617 + t * (2004.191898 + t * (-0.4297829 + t * (-0.19861834 + t * (0.000007578 + t * (0.0000059285)))))
        y = -0.006951 + t * (-0.025896 + t * (-22.4072747 + t * (0.00190059 + t * (0.001112526 + t * (0.0000001358)))))
        x = x * 2.0 * math.pi / (360.0 * 60.0 * 60)
        y = y * 2.0 * math.pi / (360.0 * 60.0 * 60.0)
        #print(x,y)
        #z = math.sqrt(1 - x*x - y*y)
        #b = 1 / (1 + z)
        b = 0.5 + (x*x + y*y) / 8.0
        m = QMatrix3x3([1.0 - b*x*x, -b*x*y, x, -b*x*y, 1.0 -b*y*y, y, -x, -y, 1.0 - b*(x*x+y*y)])
        return m
    def matCIOLocator(self, jd):
        J2000 = 2451545.0
        t = jd - J2000
        t = t / 36525 #julian century
        x = -0.016617 + t * (2004.191898 + t * (-0.4297829 + t * (-0.19861834 + t * (0.000007578 + t * (0.0000059285)))))
        y = -0.006951 + t * (-0.025896 + t * (-22.4072747 + t * (0.00190059 + t * (0.001112526 + t * (0.0000001358)))))
        xt = x * 2.0 * math.pi / (360.0 * 60.0 * 60)
        yt = y * 2.0 * math.pi / (360.0 * 60.0 * 60.0)
        x0 = -0.016617
        y0 = -0.006951
        xt0 = x0 * 2.0 * math.pi / (360.0 * 60.0 * 60)
        yt0 = y0 * 2.0 * math.pi / (360.0 * 60.0 * 60.0)
        xc = [-0.016617, 2004.191898, -0.4297829, -0.19861834, 0.000007578 , 0.0000059285]
        yc = [-0.006951, -0.025896, -22.4072747, 0.00190059, 0.001112526, 0.0000001358]
        px = DPolynom()
        px.setCoeffs(xc)
        py=DPolynom()
        py.setCoeffs(yc)
        dpx=px.derive()
        spx=dpx.mul(py)
        ispx = spx.integrate()
        ixt = ispx.eval(t)
        ixt0 = ispx.eval(0.0)
        ixt = ixt * 2.0 * math.pi / (360.0 * 60.0 * 60)
        ixt0 = ixt0 * 2.0 * math.pi / (360.0 * 60.0 * 60.0)
        s = - 0.5 * (xt * yt - xt0 * yt0) + (ixt - ixt0) - 0.0145606
        m = QMatrix3x3([math.cos(s), -math.sin(s), 0.0, math.sin(s), math.cos(s), 0, 0, 0, 1.0])
        return m
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QVector3D
    from PyQt5.Qt3DExtras import Qt3DWindow, QOrbitCameraController
    import sys
    app=QApplication(sys.argv)
    view = Qt3DWindow()
    view.defaultFrameGraph().setClearColor(QColor(37,37,39))
    view.show()
    world = World3D()
    camera = view.camera()
    camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 100000.0)
    #camera.lens().setOrthographicProjection(-50000,50000, 0, 50000, 0, 100000.0)
    camera.setPosition(QVector3D(0.0, 750.0, 3000.0))
    camera.setViewCenter(QVector3D(0.0, 0.0, 0.0))
    camController = QOrbitCameraController(world.rootEntity)
    camController.setLinearSpeed(500.0)
    camController.setLookSpeed(120.0)
    camController.setCamera(camera)
    view.setRootEntity(world.rootEntity)
    app.exec_()
