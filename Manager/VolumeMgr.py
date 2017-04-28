import mudicom
import vtk
from vtk.util import numpy_support

import numpy as np

import matplotlib.pyplot as plt

class E_VolumeManager:
    def __init__(self, Mgr):
        self.Mgr = Mgr

        #Selected Volume CFGS
        self.m_colorFunction = vtk.vtkColorTransferFunction()
        self.m_opacityFunction = vtk.vtkPiecewiseFunction()
        self.m_scalarRange = [0.0, 1.0]
        self.m_volumeProperty = vtk.vtkVolumeProperty()

        self.m_volumeMapper = vtk.vtkSmartVolumeMapper()
        self.m_volume = vtk.vtkActor()



        #Initialize
        self.SetPresetFunctions(self.Mgr.mainFrm.volumeWidget.GetCurrentColorIndex())
        # self.InitializeRenderFunctions()

    def SetPresetFunctions(self, idx, update = False):

        #Housefield unit : -1024 ~ 3072
        if update == False:
            self.m_colorFunction.RemoveAllPoints()
            self.m_opacityFunction.RemoveAllPoints()

        housefiledRange = 3072 + 1024
        sRange = self.m_scalarRange[1] - self.m_scalarRange[0]
        rangeFactor = sRange / housefiledRange

        if idx == 0: #MIP
            self.m_colorFunction.AddRGBPoint(self.m_scalarRange[0], 1.0, 1.0, 1.0)
            self.m_colorFunction.AddRGBPoint(self.m_scalarRange[1], 1.0, 1.0, 1.0)

            self.m_opacityFunction.AddPoint(self.m_scalarRange[0], 0.0)
            self.m_opacityFunction.AddPoint(self.m_scalarRange[1], 1.0)

            self.m_volumeProperty.ShadeOff()
            self.m_volumeProperty.SetInterpolationTypeToLinear()

            self.m_volumeMapper.SetBlendModeToMaximumIntensity()

        elif idx == 1: #CT_SKIN
            self.m_colorFunction.AddRGBPoint(self.m_scalarRange[0], 0.0, 0.0, 0.0, 0.5, 0.0)
            self.m_colorFunction.AddRGBPoint((-1000 + 1024) / rangeFactor , 0.62, 0.36, 0.18, 0.5, 0.0)
            self.m_colorFunction.AddRGBPoint((-500 + 1024) / rangeFactor , 0.88, 0.60, 0.29, 0.33, 0.45)
            self.m_colorFunction.AddRGBPoint(self.m_scalarRange[1], 0.83, 0.66, 1.0, 0.5, 0.0)

            self.m_opacityFunction.AddPoint(self.m_scalarRange[0],0.0, 0.5, 0.0)
            self.m_opacityFunction.AddPoint((-1000 + 1024) / rangeFactor, 0.0, 0.5, 0.0)
            self.m_opacityFunction.AddPoint((-500 + 1024) / rangeFactor, 1.0, 0.33, 0.45)
            self.m_opacityFunction.AddPoint(self.m_scalarRange[1], 1.0, 0.5, 0.0)

            self.m_volumeProperty.ShadeOn()
            self.m_volumeProperty.SetInterpolationTypeToLinear()

            self.m_volumeMapper.SetBlendModeToComposite()


        elif idx == 2: #CT_BONE
            self.m_colorFunction.AddRGBPoint(self.m_scalarRange[0], 0.0, 0.0, 0.0, 0.5, 0.0)
            self.m_colorFunction.AddRGBPoint((-16 + 1024) / rangeFactor , 0.73, 0.25, 0.30, 0.49, 0.0)
            self.m_colorFunction.AddRGBPoint((641 + 1024) / rangeFactor , 0.90, 0.82, 0.56, 0.5, 0.0)
            self.m_colorFunction.AddRGBPoint(self.m_scalarRange[1], 1.0, 1.0, 1.0, 0.5, 0.0)

            self.m_opacityFunction.AddPoint(self.m_scalarRange[0],0.0, 0.5, 0.0)
            self.m_opacityFunction.AddPoint((-16 + 1024) / rangeFactor, 0.0, 0.49, 0.61)
            self.m_opacityFunction.AddPoint((-641 + 1024) / rangeFactor, 0.72, 0.5, 0.0)
            self.m_opacityFunction.AddPoint(self.m_scalarRange[1], 0.71, 0.5, 0.0)

            self.m_volumeProperty.ShadeOn()
            self.m_volumeProperty.SetInterpolationTypeToLinear()

            self.m_volumeMapper.SetBlendModeToComposite()

        elif idx == 3: #Voxel
            self.m_colorFunction.AddRGBPoint(self.m_scalarRange[0], 0.0, 0.0, 1.0)
            self.m_colorFunction.AddRGBPoint((self.m_scalarRange[0] + self.m_scalarRange[1])/2.0, 0.0, 1.0, 0.0)
            self.m_colorFunction.AddRGBPoint(self.m_scalarRange[1], 1.0, 0.0, 0.0)

            self.m_opacityFunction.AddPoint(self.m_scalarRange[0], 0.0)
            self.m_opacityFunction.AddPoint(self.m_scalarRange[1], 1.0)

            self.m_volumeProperty.ShadeOff()
            self.m_volumeProperty.SetInterpolationTypeToLinear()

            self.m_volumeMapper.SetBlendModeToMaximumIntensity()


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
            shape = img.shape
            img = img.reshape(shape[1], shape[0])
            img = np.rot90(img)

            volumeBuffer.append(img)



        #Volume ARray
        volumeArray = np.asarray(volumeBuffer, dtype=np.uint16)
        #
        #
        # plt.imshow(volumeArray[0], cmap="gray")
        # plt.show()


        self.AddVolume(volumeArray, spacing, pixelSpacing)

    def AddVolume(self, volumeArray, spacing = 1.0, pixel = [0.5, 0.5]):
        data_string = volumeArray.tostring()
        dim = volumeArray.shape

        imgData = vtk.vtkImageData()
        imgData.SetDimensions(dim[1], dim[2], dim[0])
        imgData.AllocateScalars(vtk.VTK_UNSIGNED_INT, 1);
        imgData.SetSpacing(pixel[0], pixel[1], spacing)

        #
        # for i in range(volumeArray.size):
        #
        #     y = i % dim[2]
        #     x = int(i / dim[2]) % dim[1]
        #     z = int(i / (dim[1] * dim[2]))
        #
        #     # print(z, ", ", x , ",", y)
        #     imgData.SetScalarComponentFromDouble(x, y, z, 0, volumeArray[z][x][y])

        for i in range(dim[0]):
            for j in range(dim[2]):
                for k in range(dim[1]):
                    imgData.SetScalarComponentFromDouble(k, j, i, 0, volumeArray[i][k][j])

        self.m_scalarRange = imgData.GetScalarRange()
        #update Preset OTF
        self.SetPresetFunctions(self.Mgr.mainFrm.volumeWidget.GetCurrentColorIndex(), True)


        self.AddVolumeData(imgData, True)

    def AddVolumeData(self, source, type=False):
        self.Mgr.ClearScene()

        # Prepare volume properties.
        self.m_volumeProperty.SetColor(self.m_colorFunction)
        self.m_volumeProperty.SetScalarOpacity(self.m_opacityFunction)


        #Mapper
        if type:
            self.m_volumeMapper.SetInputData(source)
        else:
            self.m_volumeMapper.SetInputConnection(source)


        #Actor
        self.m_volume = vtk.vtkVolume()
        self.m_volume.SetMapper(self.m_volumeMapper)
        self.m_volume.SetProperty(self.m_volumeProperty)
        self.m_volume.SetPosition([0, 0, 0])

        #Add Actor
        self.Mgr.renderer[1].AddVolume(self.m_volume)
        self.Mgr.renderer[1].ResetCamera()
        self.Mgr.Redraw()
