import vtk
from vtk.util.numpy_support import vtk_to_numpy
import os
import numpy as np
import random

from PyQt5.QtWidgets import QApplication

#Theano
import theano
import theano.tensor as T
import theano.sandbox.cuda.basic_ops as scuda
import lasagne

#utils
from utils import checkpoints
from Manager.InteractorStyle import E_InteractorStyle
from NetworkData import labels

v_res = 3
dim = 32

#define argument path
curPath = os.path.dirname(os.path.realpath(__file__))
rootPath = os.path.abspath(os.path.join(curPath, os.pardir))
weightPath = rootPath + "\\NetworkData\\VRN.npz"
modelPath = rootPath + "\\NetworkData\\modelnet40_rot_test.npz"

class E_Manager:
    def __init__(self, mainFrm):
        self.mainFrm = mainFrm
        self.renderer = [0, 0]

        self.bInitNetowrk = False

        #Test function
        self.predFunc = None
        self.predList = None
        self.testFunc = None


        # print(len(labels.label))

        for i in range(2):
            interactor = E_InteractorStyle(self, i)

            self.renderer[i] = vtk.vtkRenderer()
            self.renderer[i].SetBackground(0.0, 0.0, 0.0)
            self.mainFrm.m_vtkWidget[i].GetRenderWindow().AddRenderer(self.renderer[i])
            self.mainFrm.m_vtkWidget[i].GetRenderWindow().Render()
            self.mainFrm.m_vtkWidget[i].GetRenderWindow().GetInteractor().SetInteractorStyle(interactor)


        #Initialize
        self.InitTextActor()


    def InitObject(self):
        cylinder = vtk.vtkCylinderSource()
        cylinder.SetResolution(80)

        self.VoxelizeObject(cylinder)

        cylinderMapper = vtk.vtkPolyDataMapper()
        cylinderMapper.SetInputConnection(cylinder.GetOutputPort())

        cylinderActor = vtk.vtkActor()
        cylinderActor.SetMapper(cylinderMapper)
        cylinderActor.RotateX(30.0)
        cylinderActor.RotateY(-45.9)

        self.renderer[0].AddActor(cylinderActor)
        self.renderer[0].ResetCamera()

        self.Redraw();

    def InitTextActor(self):
        self.groundTruthLog = vtk.vtkTextActor()
        self.groundTruthLog.SetInput("Label")
        self.groundTruthLog.SetPosition(10, 60)
        self.groundTruthLog.GetTextProperty().SetFontSize(24)
        self.groundTruthLog.GetTextProperty().SetColor(1.0, 0.0, 0.0)


        self.predLog = vtk.vtkTextActor()
        self.predLog.SetInput("Predicted")
        self.predLog.SetPosition(10, 30)
        self.predLog.GetTextProperty().SetFontSize(24)
        self.predLog.GetTextProperty().SetColor(0.0, 1.0, 0.0)


        self.renderer[1].AddActor2D(self.groundTruthLog)
        self.renderer[1].AddActor2D(self.predLog)




    def VoxelizeObject(self, source):

        #Set Voxel Space Resolution nxnxn
        resolution = 32
        bounds = [0, 0, 0, 0, 0, 0]
        center = source.GetOutput().GetCenter()
        source.GetOutput().GetBounds(bounds)


        #Get Maximum Boundary Length
        maxB = 0.0
        for i in range(0, 6, 2):
            if abs(bounds[i] - bounds[i+1]) > maxB:
                maxB = abs(bounds[i] - bounds[i+1])

        #Calculate Spacing
        spacingVal = maxB / resolution

        print('Spacing Value : ', spacingVal)
        spacing = [spacingVal, spacingVal, spacingVal]

        bounds = [center[0] - resolution * spacing[0] / 2, center[0] + resolution * spacing[0] / 2,center[1] - resolution * spacing[1] / 2, center[1] + resolution * spacing[2] / 2, center[2] - resolution * spacing[2] / 2, center[2] + resolution * spacing[0] / 2]

        imgData = vtk.vtkImageData()
        imgData.SetSpacing(spacing)
        origin = [center[0] - resolution * spacing[0] / 2, center[1] - resolution * spacing[1] / 2, center[2] - resolution * spacing[2] / 2]
        imgData.SetOrigin(origin)

        #Dimensions
        dim = [resolution, resolution, resolution]
        imgData.SetDimensions(dim)
        imgData.SetExtent(0, dim[0]-1, 0, dim[1]-1, 0, dim[2]-1)
        imgData.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
        for i in range(imgData.GetNumberOfPoints()):
            imgData.GetPointData().GetScalars().SetTuple1(i, 1)

        pol2stenc = vtk.vtkPolyDataToImageStencil()
        pol2stenc.SetInputData(source.GetOutput())
        pol2stenc.SetOutputOrigin(origin)
        pol2stenc.SetOutputSpacing(spacing)
        pol2stenc.SetOutputWholeExtent(imgData.GetExtent())

        imgstenc = vtk.vtkImageStencil()
        imgstenc.SetInputData(imgData)
        imgstenc.SetStencilConnection(pol2stenc.GetOutputPort())
        imgstenc.ReverseStencilOff()
        imgstenc.SetBackgroundValue(0)
        imgstenc.Update()


        scalarData = vtk_to_numpy( imgstenc.GetOutput().GetPointData().GetScalars() )
        # print(scalarData)
        self.DrawVoxelArray(scalarData)

        self.PredictObject(scalarData)

        # self.AddVolumeData(imgstenc.GetOutputPort())

    def AddVolumeData(self, source):
        self.ClearScene()

        # Prepare color and transparency values
        colorFunc = vtk.vtkColorTransferFunction()
        alphaChannelFunc = vtk.vtkPiecewiseFunction()
        alphaChannelFunc.AddPoint(0, 0.0)
        alphaChannelFunc.AddPoint(1, 1.0)
        # alphaChannelFunc.AddPoint(64,0.5)
        # alphaChannelFunc.AddPoint(128,0.5)
        # alphaChannelFunc.AddPoint(192,0.5)
        # alphaChannelFunc.AddPoint(255,1.0)

        colorFunc.AddRGBPoint(0, 0.0, 0.0, 0.0)
        colorFunc.AddRGBPoint(1, 0.0, 0.0, 1.0)
        colorFunc.AddRGBPoint(128,1.0,0.0,0.0)
        colorFunc.AddRGBPoint(192, 1.0,0.0,0.7)
        colorFunc.AddRGBPoint(255,0.0,0.1,0.0)

        # Prepare volume properties.
        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(colorFunc)
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
        self.renderer[1].AddVolume(volume)
        self.renderer[1].ResetCamera()
        self.Redraw()

    def Redraw(self):
        for i in range(2):
            self.mainFrm.m_vtkWidget[i].GetRenderWindow().Render()




    def ImportObject(self, path):
        self.SetLog(path)
        filename, file_extension = os.path.splitext(path)

        if file_extension == ".stl":

            #Remove All Actors
            self.ClearScene()

            reader = vtk.vtkSTLReader()
            reader.SetFileName(path)
            reader.Update()


            self.VoxelizeObject(reader)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            self.renderer[0].AddActor(actor)
            self.renderer[0].ResetCamera()
            self.Redraw()

        elif file_extension == ".obj":
            #Remove All Actors
            self.ClearScene()

            reader = vtk.vtkOBJReader()
            reader.SetFileName(path)
            reader.Update()


            self.VoxelizeObject(reader)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            self.renderer[0].AddActor(actor)
            self.renderer[0].ResetCamera()
            self.Redraw()


        else:
            self.SetLog('File Extension Not Supported')

    def InitNetwork(self):
        self.SetLog("Import Pre-trained Network..")
        import NetworkData.VRN as config_module
        # config_module = __import__('VRN', weightPath[:-3])


        self.SetLog("Import Completed.")
        self.SetLog("Load config and model files..")
        cfg = config_module.cfg
        model = config_module.get_model()


        #Compile Functions
        self.SetLog('Compiling Theano Functions..')
        self.testFunc, tvars, model, self.predFunc, self.predList = self.MakeFunctions(cfg, model)


        #Load Weights
        metadata = checkpoints.load_weights(weightPath, model['l_out'])

        #Check if previous best accuracy is in metadata form previous test_batch_slice
        best_acc = metadata['best_acc'] if 'best_acc' in metadata else 0
        log = 'best_accuracy' + str(best_acc)
        self.SetLog(log)

        self.mainFrm.trainAction.setEnabled(False)
        self.bInitNetowrk = True;

    def RandomPrediction(self):
        #Get Features and Target Data
        xt = np.asarray(np.load(modelPath)['features'], dtype=np.float32)
        yt = np.asarray(np.load(modelPath)['targets'], dtype=np.float32)


        #Get Random
        randIdx = random.randint(0, len(xt))

        #Draw Object
        self.DrawVoxelArray(xt[randIdx])


        log = labels.label[int(yt[randIdx])]

        #Predict 3D object
        self.PredictObject(xt[randIdx], log)



    def PredictObject(self, inputData, groundTruth = "unknown"):

        #Predict Object
        if self.bInitNetowrk:
            inputData = np.asarray(inputData.reshape(1, 1, 32, 32, 32), dtype=np.float32)
            inputData = 4.0 * inputData - 1.0

            pred = self.predFunc(inputData)
            pList = self.predList(inputData)

            #Show Log
            gtlog = "Label : " + groundTruth
            self.groundTruthLog.SetInput(gtlog)
            log = "Predicted : " + labels.label[int(pred)] + " -> " + str(pList[0][int(pred)] * 100.0) + "%"
            self.predLog.SetInput(log)

            self.Redraw()

        else:
            self.SetLog('Network Need to be Initialized')
            return


    def MakeDataMatrix(self, x, intensity):
        return intensity*np.repeat(np.repeat(np.repeat(x[0][0], v_res, axis=0), v_res, axis=1), v_res, axis=2)


    def MakeFunctions(self, cfg, model):
        #Input Array
        X = T.TensorType('float32', [False]*5)('X')

        #shared variable for input array
        X_shared = lasagne.utils.shared_empty(5, dtype='float32')

        #Class Vector
        y = T.TensorType('int32', [False]*1)('y')

        #Shared Variable for class vector
        y_shared = lasagne.utils.shared_empty(1, dtype='float32')

        #Output Layer
        l_out = model['l_out']

        #Batch Parameters
        batch_index = T.iscalar('batch_index')
        test_batch_slice = slice(batch_index*cfg['n_rotations'], (batch_index+1)*cfg['n_rotations'])

        #Get Output
        y_hat_deterministic = lasagne.layers.get_output(l_out, X, deterministic=True)
        softmax = T.nnet.softmax(y_hat_deterministic)

        #Average Across Rotation Examples
        pred = T.argmax(T.sum(y_hat_deterministic, axis=0))

        #Get Error Rate
        classifier_test_error_rate = T.cast(T.mean(T.neq(pred, T.mean(y,dtype='int32'))), 'float32')

        #Compile Functions
        test_error_fn = theano.function([batch_index], [classifier_test_error_rate, pred], givens={X:X_shared[test_batch_slice], y:T.cast(y_shared[test_batch_slice], 'int32')})

        pred_fn = theano.function([X], pred)
        pred_list = theano.function([X], softmax)

        tfuncs = {'test_function':test_error_fn}
        tvars = {'X':X, 'y':y, 'X_shared':X_shared, 'y_shared':y_shared}


        return tfuncs, tvars, model, pred_fn, pred_list

    def DrawVoxelArray(self, arrayBuffer):
        #reshape

        sample = arrayBuffer.reshape(1, 1, 32, 32, 32)
        dataMatrix = self.MakeDataMatrix( np.asarray(sample, dtype=np.uint8), 128)
        data_string = dataMatrix.tostring()


        dataImporter = vtk.vtkImageImport()
        dataImporter.CopyImportVoidPointer(data_string, len(data_string))
        dataImporter.SetDataScalarTypeToUnsignedChar()
        dataImporter.SetNumberOfScalarComponents(1)
        dataImporter.SetDataExtent(0, int(dim * v_res)-1, 0, int(dim * v_res)-1, 0, int(dim * v_res)-1)
        dataImporter.SetWholeExtent(0, int(dim * v_res)-1, 0, int(dim * v_res)-1, 0, int(dim * v_res)-1)

        self.AddVolumeData(dataImporter.GetOutputPort())


    def RunGenerativeMode(self):
        self.SetLog("Generative Mode")
        self.SetLog("Reset Renderer")
        self.SetLog("Set View Mode 1view")
        self.SetLog("Run Generative Mode")

    def SyncCamera(self, idx):
        # other = 1
        # if idx == 1: other = 0
        #
        # cam1 = self.renderer[idx].GetActiveCamera()
        # cam2 = self.renderer[other].GetActiveCamera()
        #
        # cam2.DeepCopy(cam1)
        #
        # self.Redraw()
        return

    def ClearScene(self):
        for i in range(2):
            self.renderer[i].RemoveAllViewProps()

            #Add Log Actors
            self.renderer[1].AddActor2D(self.groundTruthLog)
            self.renderer[1].AddActor2D(self.predLog)

    def SetLog(self, text):
        QApplication.processEvents()
        self.mainFrm.m_logWidget.appendPlainText(text)
