import vtk
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
        self.InitObject()


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
        print(path)

    def TrainData(self):
        print("Train Data")
