import mudicom
import vtk
from vtk.util import numpy_support

import numpy as np

class E_VolumeManager:
    def __init__(self, Mgr):
        self.Mgr = Mgr

        self.Mgr.SetLog('volume Mgr Initialized')

    def ImportVolume(self, fileSeries):
        volumeBuffer = []

        for i in range( len(fileSeries) ):
            mu = mudicom.load(fileSeries[i])

            img = mu.image.numpy
            volumeBuffer.append(img)

        volumeArray = np.asarray(volumeBuffer)


        self.AddVolume(volumeArray)

    def AddVolume(self, volumeArray):

        foo = numpy_support.numpy_to_vtk(volumeArray)
        print(foo)

        # np.set_printoptions(threshold=np.inf)
        # np.set_printoptions(suppress=True)
        # np.set_printoptions(precision=4)
        #
        # dataImporter = vtk.vtkImageImport()
        # dataImporter.CopyImportVoidPointer(volumeArray, len(volumeArray))
        # dataImporter.SetDataScalarTypeToUnsignedChar()
        # dataImporter.SetNumberOfScalarComponents(1)
        # dataImporter.SetDataExtent(0, int(dim * v_res)-1, 0, int(dim * v_res)-1, 0, int(dim * v_res)-1)
        # dataImporter.SetWholeExtent(0, int(dim * v_res)-1, 0, int(dim * v_res)-1, 0, int(dim * v_res)-1)
        # 
        # print(volumeArray)
