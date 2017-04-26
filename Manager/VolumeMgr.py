import mudicom
import vtk
from vtk.util import numpy_support

import numpy as np

class E_VolumeManager:
    def __init__(self, Mgr):
        self.Mgr = Mgr

        self.Mgr.SetLog('volume Mgr Initialized')

        self.m_colorFunctions = []
        self.InitializeColorFunctions()

    def InitializeColorFunctions(self):
        whiteColor = vtk.vtkColorTransferFunction()
        whiteColor.AddRGBPoint(0, 1.0, 1.0, 1.0)
        whiteColor.AddRGBPoint(1, 1.0, 1.0, 1.0)
        self.m_colorFunctions.append(whiteColor)


        muscleColor = vtk.vtkColorTransferFunction()
        muscleColor.AddRGBPoint(0, 0.0, 0.0, 0.0)
        muscleColor.AddRGBPoint(1, 1.0, 0.0, 0.0)
        self.m_colorFunctions.append(muscleColor)


        voxelColor = vtk.vtkColorTransferFunction()
        voxelColor.AddRGBPoint(0, 0.0, 0.0, 1.0)
        voxelColor.AddRGBPoint(255,0.0,1.0,0.0)
        self.m_colorFunctions.append(voxelColor)



    def ImportVolume(self, fileSeries):
        volumeBuffer = []

        for i in range( len(fileSeries) ):
            mu = mudicom.load(fileSeries[i])

            spacing = 1.0;
            if len(list(mu.find(0x0018, 0x0088))) > 0:
                spacing = float(list(mu.find(0x0018, 0x0088))[0].value)

            position = list(mu.find(0x0020, 0x0032))[0].value
            orientation = list(mu.find(0x0020, 0x0037))[0].value
            pixelSpacing = list(mu.find(0x0028, 0x0030))[0].value
            pixelSpacing = list(map(float, [x.strip() for x in pixelSpacing.split('\\')]))

            # print("spacing :", spacing, "(mm) // position :", position, " // orientation :", orientation, "// Pixel Spacing : ", pixelSpacing)

            img = mu.image.numpy
            volumeBuffer.append(img)

        volumeArray = np.asarray(volumeBuffer, dtype=np.uint8)

        self.AddVolume(volumeArray, spacing, pixelSpacing)

    def AddVolume(self, volumeArray, spacing = 1.0, pixel = [0.5, 0.5]):
        data_string = volumeArray.tostring()
        dim = volumeArray.shape
        # log = "Dimension : " + dim
        # self.Mgr.SetLog(log)

        dataImporter = vtk.vtkImageImport()
        dataImporter.CopyImportVoidPointer(data_string, len(data_string))
        dataImporter.SetDataScalarTypeToUnsignedChar()
        dataImporter.SetNumberOfScalarComponents(1)
        dataImporter.SetDataExtent(0, dim[1]-1, 0, dim[2]-1, 0, dim[0]-1)
        dataImporter.SetWholeExtent(0, dim[1]-1, 0, dim[2]-1, 0, dim[0]-1)
        dataImporter.SetDataSpacing(pixel[0], pixel[1], spacing)

        print(dataImporter.GetDataSpacing())


        self.AddVolumeData(dataImporter.GetOutputPort())

    def AddVolumeData(self, source):
        self.Mgr.ClearScene()

        # Prepare color and transparency values

        alphaChannelFunc = vtk.vtkPiecewiseFunction()
        alphaChannelFunc.AddPoint(0, 0.0)
        alphaChannelFunc.AddPoint(1, 1.0)
        # alphaChannelFunc.AddPoint(64,0.5)
        # alphaChannelFunc.AddPoint(128,0.5)
        # alphaChannelFunc.AddPoint(192,0.5)
        # alphaChannelFunc.AddPoint(255,1.0)


        # Prepare volume properties.
        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(self.m_colorFunctions[ self.Mgr.mainFrm.volumeWidget.GetCurrentColorIndex() ])
        volumeProperty.SetScalarOpacity(alphaChannelFunc)
        volumeProperty.ShadeOn() # Keep this on unless you want everything to look terrible
        volumeProperty.SetInterpolationTypeToNearest()


        #Mapper
        volumeMapper = vtk.vtkSmartVolumeMapper()
        volumeMapper.SetInputConnection(source)

        #Actor
        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        volume.SetProperty(volumeProperty)
        volume.SetPosition([0, 0, 0])


        #Add Actor
        self.Mgr.renderer[1].AddVolume(volume)
        self.Mgr.renderer[1].ResetCamera()
        self.Mgr.Redraw()
