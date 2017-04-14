from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

import sys, os
sys.path.insert(0, os.getcwd() + "/../")
from Manager.Mgr import E_Manager


iconPath = "D:/Projects/EJModelNet/icons"

class E_MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(E_MainWindow, self).__init__(parent)

        self.setWindowTitle("EJ ModelNet Project")

        #Central Widget
        self.m_centralWidget = QWidget()
        self.setCentralWidget(self.m_centralWidget)

        #vtk Renderer Widget
        self.m_vtkWidget = [0, 0]
        for i in range(2):
            self.m_vtkWidget[i] = QVTKRenderWindowInteractor();


        #Initialize
        self.InitToolbar()
        self.InitCentralWidget()
        self.InitManager()

    def InitToolbar(self):
        #ToolBar
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(58, 58))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        #Add Toolbar to the MainWindow
        self.addToolBar(toolbar)

        #Import Object Action
        importAction = QAction(QIcon(iconPath + "/051-cmyk.png"), "Import Object", self)
        importAction.triggered.connect(self.onImportObject)
        toolbar.addAction(importAction)

        trainAction = QAction(QIcon(iconPath + "/051-pantone-2.png"), "Train Data", self)
        trainAction.triggered.connect(self.onTrainData)
        toolbar.addAction(trainAction)


    def InitCentralWidget(self):


        MainLayout = QHBoxLayout()
        self.m_centralWidget.setLayout(MainLayout)


        for i in range(2):
            MainLayout.addWidget(self.m_vtkWidget[i])


    def InitManager(self):
        self.Mgr = E_Manager(self)


    def onImportObject(self):
        path = QFileDialog.getOpenFileName(self, "Import 3D Objects", "./", "Object Files(*.stl)")

        self.Mgr.ImportObject(path[0])

    def onTrainData(self):
        self.Mgr.TrainData();
