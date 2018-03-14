from PyQt5 import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QSpacerItem, QScrollArea, QLayout
from indi.client.qt.indiproperty import INDI_P

class INDI_G:
    def __init__(self, idv, inName):
        self.dp = idv
        self.name = inName if inName else 'Unknown'
        self.propertyContainer = QFrame(idv)
        self.propertyLayout = QVBoxLayout(self.propertyContainer)
        self.VerticalSpacer = QSpacerItem(20, 20, Qt.QSizePolicy.Minimum, Qt.QSizePolicy.Expanding)
        self.propertyLayout.addItem(self.VerticalSpacer)
        self.propertyLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.propertyContainer)
        self.scrollArea.setMinimumSize(idv.size())
        self.propList = list()
    def getContainer(self):
        return self.propertyContainer
    def getScrollArea(self):
        return self.scrollArea
    def getName(self):
        return self.name
    def getDevice(self):
        return self.dp
    def getProperties(self):
        return self.propList
    def size(self):
        return len(self.propList)
    def addProperty(self, prop):
        propName = prop.getName()
        pp = self.getProperty(propName)
        if pp:
            return False
        pp = INDI_P(self, prop)
        self.propList.append(pp)
        self.propertyLayout.removeItem(self.VerticalSpacer)
        self.propertyLayout.addLayout(pp.getContainer())
        self.propertyLayout.addItem(self.VerticalSpacer)
        return True
    def removeProperty(self, propName):
        for pp in self.propList:
            if pp.getName() == propName:
                self.propList.remove(pp)
                self.propertyLayout.removeItem(pp.getContainer())
                del(pp)
                return True
        return False
    def getProperty(self, propName):
        for  pp in self.propList:
            if pp.getName() == propName:
                return pp
        return None
