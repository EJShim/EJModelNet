import vtk

class E_InteractorStyle(vtk.vtkInteractorStyleSwitch):
    def __init__(self, Manager, idx):
        self.Mgr = Manager;
        self.idx = idx

        #Style to
        self.SetCurrentStyleToTrackballCamera()
        self.GetCurrentStyle().AddObserver("MouseMoveEvent", self.MouseMoveEvent)
        self.GetCurrentStyle().AddObserver('MouseWheelEvent', self.MouseWheelEvent)



    def MouseMoveEvent(self, obj, event):

        if obj.GetState():
            self.Mgr.SyncCamera(self.idx)


        self.GetCurrentStyle().OnMouseMove()

    def MouseWheelEvent(self, obj, event):
        self.GetCurrentStyle().OnMouseWheel()
        print('Mouse WHeel')
