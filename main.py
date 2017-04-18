# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import *
from GUI.MainFrm import E_MainWindow


app = QApplication([])

window = E_MainWindow()

window.resize(1800, 900)
window.show()
sys.exit(app.exec_())
