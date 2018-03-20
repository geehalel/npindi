from indi.client.qt.indistd import *


class CCD(ISD.DeviceDecorator):
    def __init__(self, iPtr):
        super().__init__(iPtr)
        self.dType = DeviceFamily.KSTARS_CCD
