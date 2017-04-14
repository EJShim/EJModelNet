import vtk
import os
# from InteractorStyle import E_InteractorStyle

class E_Manager:
    def __init__(self, mainFrm):
        self.mainFrm = mainFrm

        self.renderer = [0, 0]

        for i in range(2):
            interactor = vtk.vtkInteractorStyleSwitch()
            interactor.SetCurrentStyleToTrackballCamera()

            self.renderer[i] = vtk.vtkRenderer()
            self.renderer[i].SetBackground(0.0, 0.0, 0.0)
            self.mainFrm.m_vtkWidget[i].GetRenderWindow().AddRenderer(self.renderer[i])
            self.mainFrm.m_vtkWidget[i].GetRenderWindow().Render()
            self.mainFrm.m_vtkWidget[i].GetRenderWindow().GetInteractor().SetInteractorStyle(interactor)


        #Initialize
        #self.InitObject()


    def InitObject(self):
        cylinder = vtk.vtkCylinderSource()
        cylinder.SetResolution(8)

        cylinderMapper = vtk.vtkPolyDataMapper()
        cylinderMapper.SetInputConnection(cylinder.GetOutputPort())

        cylinderActor = vtk.vtkActor()
        cylinderActor.SetMapper(cylinderMapper)
        cylinderActor.RotateX(30.0)
        cylinderActor.RotateY(-45.9)

        self.renderer[0].AddActor(cylinderActor)
        self.renderer[0].ResetCamera()

        self.Redraw();

    def Redraw(self):
        for i in range(2):
            self.mainFrm.m_vtkWidget[i].GetRenderWindow().Render()


    def ImportObject(self, path):
        self.SetLog(path)

        filename, file_extension = os.path.splitext(path)

        if file_extension == ".stl":

            #Remove All Actors
            self.renderer[0].RemoveAllViewProps()

            reader = vtk.vtkSTLReader()
            reader.SetFileName(path)
            reader.Update()

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            self.renderer[0].AddActor(actor)
            self.renderer[0].ResetCamera()
            self.Redraw()

        else:
            self.SetLog('NNONO')

    def TrainData(self):
        print("Train Data")

    def SetLog(self, text):
        self.mainFrm.m_logWidget.appendPlainText(text)
