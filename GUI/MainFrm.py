from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

import sys, os
from Manager.Mgr import E_Manager
from GUI.VolumeRenderingWidget import E_VolumeRenderingWidget


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

        self.addToolBar(toolbar)


        mainTab = QTabWidget()
        toolbar.addWidget(mainTab)


        objectToolbar = QToolBar();
        objectToolbar.setIconSize(QSize(58, 58))
        objectToolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        mainTab.addTab(objectToolbar, "3D Objects")

        #Import Object Action
        importAction = QAction(QIcon(iconPath + "/051-cmyk.png"), "Import Object", self)
        importAction.triggered.connect(self.onImportObject)
        objectToolbar.addAction(importAction)

        #Import Volume addAction
        volumeAction = QAction(QIcon(iconPath + "/051-document.png"), "Import Volume", self)
        volumeAction.triggered.connect(self.onImportVolume)
        objectToolbar.addAction(volumeAction)
        objectToolbar.addSeparator()

        self.volumeWidget = E_VolumeRenderingWidget()
        objectToolbar.addWidget(self.volumeWidget)




        networkToolbar = QToolBar();
        networkToolbar.setIconSize(QSize(58, 58))
        networkToolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        mainTab.addTab(networkToolbar, "VRN")

        self.trainAction = QAction(QIcon(iconPath + "/051-pantone-2.png"), "Initialize Network", self)
        self.trainAction.triggered.connect(self.onInitNetwork)
        networkToolbar.addAction(self.trainAction)

        predAction = QAction(QIcon(iconPath + "/051-programming.png"), "Predict Random", self)
        predAction.triggered.connect(self.onRandomPred)
        networkToolbar.addAction(predAction)




    def InitCentralWidget(self):
        MainLayout = QHBoxLayout()
        self.m_centralWidget.setLayout(MainLayout)


        for i in range(2):
            MainLayout.addWidget(self.m_vtkWidget[i])

        #dock widget
        dockwidget = QDockWidget("Log Area")
        dockwidget.setFeatures(QDockWidget.DockWidgetMovable)

        font = QFont()
        font.setPointSize(16)
        self.m_logWidget = QPlainTextEdit()
        self.m_logWidget.setFont(font)
        dockwidget.setWidget(self.m_logWidget)
        self.addDockWidget(Qt.BottomDockWidgetArea, dockwidget)


    def InitManager(self):
        self.Mgr = E_Manager(self)


        self.volumeWidget.SetManager(self.Mgr)



    def onImportObject(self):
        self.Mgr.SetLog('Import 3d Object')

        path = QFileDialog.getOpenFileName(self, "Import 3D Objects", "~/", "Object Files(*.stl *.obj) ;; Object Files(*.stl) ;; Object Files(*.obj)")
        self.Mgr.ImportObject(path[0])

    def onImportVolume(self):
        self.Mgr.SetLog('import Volume')

        path = QFileDialog.getOpenFileNames(self, "Import 3D Objects", "~/", "Dicom File(*.dcm)")
        fileSeries = path[0]

        if len(fileSeries) == 0: return

        #Import Volume
        self.Mgr.VolumeMgr.ImportVolume(fileSeries)

    def onInitNetwork(self):
        self.Mgr.InitNetwork()

    def onRandomPred(self):
        self.Mgr.RandomPrediction()
