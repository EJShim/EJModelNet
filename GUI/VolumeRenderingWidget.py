from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class E_VolumeRenderingWidget(QWidget):
    def __init__(self, parent = None):
        super(E_VolumeRenderingWidget, self).__init__(parent)
        self.setMaximumWidth(300)

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.m_widget = QVTKRenderWindowInteractor();
        self.m_widget.setMaximumHeight(100)
        self.m_widget.AddObserver('MouseMoveEvent', self.onMouseMove)
        self.m_widget.AddObserver('LeftButtonPressEvent', self.onLeftDown, 1.0)
        self.m_widget.AddObserver('LeftButtonReleaseEvent', self.onLeftUp, -1.0)
        self.m_bClicked = False

        self.m_view = vtk.vtkContextView()
        self.m_histogramChart  = vtk.vtkChartXY()

        self.Initialize()

    def SetManager(self, Mgr):
        self.Mgr = Mgr


        # #TEST function
        # colorFunc = self.Mgr.VolumeMgr.m_colorFunctions[0]
        # self.onChangeIndex()

    def Initialize(self):
        #CTF Controller
        self.addWidget(QLabel("Volume CTF"))

        #Add ComboBox
        self.combo = QComboBox()
        self.combo.addItem("white")
        self.combo.addItem("SKIN")
        self.combo.addItem("BONE")
        self.combo.addItem("Binary Voxel")
        self.combo.currentIndexChanged.connect( self.onChangeIndex )

        self.addWidget(self.combo)

        #OTF Controller
        self.addWidget(QLabel("Volume OTF"))


        #Initialize Histogram
        self.addWidget(self.m_widget)
        self.m_view.SetRenderWindow(self.m_widget.GetRenderWindow())
        self.m_view.GetRenderer().SetBackground(0.0, 0.0, 0.0)
        self.m_view.GetScene().AddItem(self.m_histogramChart)

        #Initialize Chart
        self.m_histogramChart.ForceAxesToBoundsOn()
        self.m_histogramChart.SetAutoAxes(False)
        self.m_histogramChart.SetAutoSize(True)
        self.m_histogramChart.SetHiddenAxisBorder(0)
        self.m_histogramChart.GetAxis(0).SetVisible(False)
        self.m_histogramChart.GetAxis(1).SetVisible(False)
        self.m_histogramChart.SetActionToButton(1, -1)



    def GetCurrentColorIndex(self):
        return self.combo.currentIndex()


    def addWidget(self, widget):
        self.mainLayout.addWidget(widget)

    def Redraw(self):
        self.m_view.Update()
        self.m_view.Render()


    def onChangeIndex(self, idx):

        #Update Preset Function
        self.Mgr.VolumeMgr.SetPresetFunctions(idx)

        #Plot CTF
        colorFunc = self.Mgr.VolumeMgr.m_colorFunction
        self.m_histogramChart.ClearPlots()
        colorPlot = vtk.vtkColorTransferFunctionItem()
        colorPlot.SetColorTransferFunction(colorFunc)
        self.m_histogramChart.AddPlot(colorPlot)

        #Plot OTF
        opacityFunc = self.Mgr.VolumeMgr.m_opacityFunction
        opacPlot = vtk.vtkPiecewiseFunctionItem()
        opacPlot.SetPiecewiseFunction(opacityFunc)
        self.m_histogramChart.AddPlot(opacPlot)

        opacityPoint = vtk.vtkPiecewiseControlPointsItem()
        opacityPoint.SetPiecewiseFunction(opacityFunc)
        opacityPoint.SetWidth(10.0)
        self.m_histogramChart.AddPlot(opacityPoint)

        #Recalculate Bounds
        sRange = self.Mgr.VolumeMgr.m_scalarRange
        self.m_histogramChart.GetAxis(vtk.vtkAxis.BOTTOM).SetRange(sRange[0], sRange[1])
        self.m_histogramChart.GetAxis(vtk.vtkAxis.BOTTOM).Update()

        #redraw Plot
        self.Redraw()
        self.Mgr.Redraw()

    def onLeftDown(self, obj, event):
        self.m_bClicked = True;

    def onLeftUp(self, obj, event):
        self.m_bClicked = False;
        self.Mgr.Redraw()

    def onMouseMove(self, obj, event):
        if self.m_bClicked == True:
            self.Mgr.Redraw()
