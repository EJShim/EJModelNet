import vtk

class E_InteractorStyle(vtk.vtkInteractorStyleSwitch):
    def __init__(self, Manager):
        self.Mgr = Manager;

        #Style to
        self.SetCurrentStyleToTrackballCamera()
