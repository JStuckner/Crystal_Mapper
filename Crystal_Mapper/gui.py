import sys
from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np
import matplotlib
matplotlib.use('QT5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import json


from crystal_math import *
from tilt_series_calculator import TiltSeriesCalculator, TiltSeriesPlot
from pole_plot import PolePlot

class CrystalSelector(QtWidgets.QWidget):

    def __init__(self, parent=None, params=None):
        # params is list [family, a, b, c, alpha, beta, gamma]
        super(CrystalSelector, self).__init__(parent)
        self.parent = parent

        # region gui elements
        # region Combo box to select
        self.comboCrystalSystem = QtWidgets.QComboBox(self)
        self.comboCrystalSystem.addItem('Triclinic')
        self.comboCrystalSystem.addItem('Monoclinic')
        self.comboCrystalSystem.addItem('Orthorhombic')
        self.comboCrystalSystem.addItem('Tetragonal')
        self.comboCrystalSystem.addItem('Trigonal')
        self.comboCrystalSystem.addItem('Hexagonal')
        self.comboCrystalSystem.addItem('Cubic')
        self.comboCrystalSystem.currentTextChanged.connect(self.crystal_select)
        #self.comboCrystalSystem.setMaximumWidth(150)
        # endregion

        # region lattice parameters
        self.labelA = QtWidgets.QLabel('a:')
        self.labelB = QtWidgets.QLabel('b:')
        self.labelC = QtWidgets.QLabel('c:')
        self.labelAlpha = QtWidgets.QLabel('\u03b1:')
        self.labelBeta = QtWidgets.QLabel('\u03b2:')
        self.labelGamma = QtWidgets.QLabel('\u03b3:')
        self.labelA.setAlignment(QtCore.Qt.AlignRight)
        self.labelB.setAlignment(QtCore.Qt.AlignRight)
        self.labelC.setAlignment(QtCore.Qt.AlignRight)
        self.labelAlpha.setAlignment(QtCore.Qt.AlignRight)
        self.labelBeta.setAlignment(QtCore.Qt.AlignRight)
        self.labelGamma.setAlignment(QtCore.Qt.AlignRight)
        self.textA = QtWidgets.QLineEdit(self)
        self.textB = QtWidgets.QLineEdit(self)
        self.textC = QtWidgets.QLineEdit(self)
        self.textAlpha = QtWidgets.QLineEdit(self)
        self.textBeta = QtWidgets.QLineEdit(self)
        self.textGamma = QtWidgets.QLineEdit(self)
        self.validator = QtGui.QDoubleValidator()
        self.textA.setValidator(self.validator)
        self.textB.setValidator(self.validator)
        self.textC.setValidator(self.validator)
        self.textAlpha.setValidator(self.validator)
        self.textBeta.setValidator(self.validator)
        self.textGamma.setValidator(self.validator)

        [i.setMaximumWidth(50) for i in [self.textA, self.textB, self.textC,
                                          self.textAlpha, self.textBeta,
                                          self.textGamma]]
        # endregion
        # endregion

        # region layout
        grid = QtWidgets.QGridLayout()

        grid.addWidget(self.comboCrystalSystem, 0, 0, 1, -1)

        grid.addWidget(self.labelA, 1,0)
        grid.addWidget(self.textA, 1, 1)
        grid.addWidget(self.labelB, 1, 2)
        grid.addWidget(self.textB, 1, 3)
        grid.addWidget(self.labelC, 1, 4)
        grid.addWidget(self.textC, 1, 5)

        grid.addWidget(self.labelAlpha, 2, 0)
        grid.addWidget(self.textAlpha, 2, 1)
        grid.addWidget(self.labelBeta, 2, 2)
        grid.addWidget(self.textBeta, 2, 3)
        grid.addWidget(self.labelGamma, 2, 4)
        grid.addWidget(self.textGamma, 2, 5)

        self.setLayout(grid)
        # endregion

        # initialize starting parameters if any.
        if params is not None:
            self.initialize_starting_parameters(params)

    # region Change crystal system selection
    def crystal_select(self, selection):
        # region set angles
        if selection in ['Cubic', 'Tetragonal', 'Orthorhombic']:
            # All angles = 90
            self.textAlpha.setText('90')
            self.textBeta.setText('90')
            self.textGamma.setText('90')
            self.textAlpha.setEnabled(False)
            self.textBeta.setEnabled(False)
            self.textGamma.setEnabled(False)
        elif selection in ['Monoclinic']:
            self.textAlpha.setText('90')
            self.textBeta.setText('90')
            self.textAlpha.setEnabled(False)
            self.textBeta.setEnabled(False)
            self.textGamma.setEnabled(True)
        elif selection in ['Hexagonal']:
            self.textAlpha.setText('90')
            self.textBeta.setText('90')
            self.textGamma.setText('120')
            self.textAlpha.setEnabled(False)
            self.textBeta.setEnabled(False)
            self.textGamma.setEnabled(False)
        elif selection in ['Trigonal']:
            self.textBeta.setText(self.textAlpha.text())
            self.textAlpha.setEnabled(True)
            self.textBeta.setEnabled(False)
            self.textGamma.setEnabled(False)
            self.textAlpha.textChanged.connect(
                self.alpha_equals_beta_equals_gamma)
        elif selection in ['Triclinic']:
            self.textAlpha.setEnabled(True)
            self.textBeta.setEnabled(True)
            self.textGamma.setEnabled(True)
        # endregion

        # region set lengths
        if selection in ['Cubic', 'Trigonal']:
            self.textB.setText(self.textA.text())
            self.textC.setText(self.textA.text())
            self.textA.setEnabled(True)
            self.textB.setEnabled(False)
            self.textC.setEnabled(False)
            self.textA.textChanged.connect(self.a_equals_b_equals_c)
        elif selection in ['Tetragonal', 'Hexagonal']:
            self.textB.setText(self.textA.text())
            self.textA.setEnabled(True)
            self.textB.setEnabled(False)
            self.textC.setEnabled(True)
            self.textA.textChanged.connect(self.a_equals_b_not_equals_c)
        else:
            self.textA.setEnabled(True)
            self.textB.setEnabled(True)
            self.textC.setEnabled(True)
        # endregion

    def alpha_equals_beta_equals_gamma(self, text):
        self.textBeta.setText(text)
        self.textGamma.setText(text)

    def a_equals_b_equals_c(self, text):
        self.textB.setText(text)
        self.textC.setText(text)

    def a_equals_b_not_equals_c(self, text):
        self.textB.setText(text)
    # endregion

    def initialize_starting_parameters(self, params):
        self.comboCrystalSystem.setCurrentText(params[0])
        self.textA.setText(str(params[1]))
        self.textB.setText(str(params[2]))
        self.textC.setText(str(params[3]))
        self.textAlpha.setText(str(params[4]))
        self.textBeta.setText(str(params[5]))
        self.textGamma.setText(str(params[6]))
        self.crystal_select(params[0])


class CrystalSelectorDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, crystal=None, num_already_exist=None):
        super(CrystalSelectorDialog, self).__init__(parent)
        self.setModal(True)
        self.crystal = crystal

        # region GUI elements
        self.butOK = QtWidgets.QPushButton('OK')
        self.butOK.clicked.connect(self.ok_clicked)
        self.butCancel = QtWidgets.QPushButton('Cancel')
        self.butCancel.clicked.connect(self.cancel_clicked)
        self.labelName = QtWidgets.QLabel('Crystal name:')
        self.textName = QtWidgets.QLineEdit()
        # region Fill starting values
        if crystal is None:
            params = None
            if num_already_exist is not None:
                self.textName.setText(
                    ''.join(('Crystal ', str(num_already_exist+1))))
            else:
                self.textName.setText('New Crystal')
        else:
            params = [crystal.system,
                      crystal.a, crystal.b, crystal.c,
                      crystal.alpha, crystal.beta, crystal.gamma]
            self.textName.setText(crystal.name)

        # endregion
        self.crystal_selector = CrystalSelector(params=params)
        self.crystal_selector.setContentsMargins(0,0,0,0)


        # endregion

        # region layout
        nameLayout = QtWidgets.QHBoxLayout()
        nameLayout.addWidget(self.labelName, 0)
        nameLayout.addWidget(self.textName, 0)
        grid = QtWidgets.QGridLayout()
        grid.addLayout(nameLayout, 0,0,1,-1)
        grid.addWidget(self.crystal_selector, 1, 0, 1, -1)
        grid.addWidget(self.butOK, 3, 3)
        grid.addWidget(self.butCancel, 3, 2)
        self.setLayout(grid)
        # endregion

        self.show()

    def ok_clicked(self):
        all_good = True
        for i in [self.crystal_selector.textA, self.crystal_selector.textB,
                  self.crystal_selector.textC, self.crystal_selector.textAlpha,
                  self.crystal_selector.textBeta,
                  self.crystal_selector.textGamma]:
            i.setStyleSheet('QLineEdit{background-color: white;}')
            try:
                a = float(i.text())
            except:
                all_good = False
                i.setStyleSheet('QLineEdit{background-color: rgb(255,90,90);}')

        if self.crystal is not None:
            self.crystal.name = self.textName.text()
            self.crystal.system = self.crystal_selector.comboCrystalSystem.currentText()
            self.crystal.a = float(self.crystal_selector.textA.text())
            self.crystal.b = float(self.crystal_selector.textB.text())
            self.crystal.c = float(self.crystal_selector.textC.text())
            self.crystal.alpha = float(self.crystal_selector.textAlpha.text())
            self.crystal.beta = float(self.crystal_selector.textBeta.text())
            self.crystal.gamma = float(self.crystal_selector.textGamma.text())

        else:
            self.crystal = Crystal(self.textName.text(),
                                   self.crystal_selector.
                                   comboCrystalSystem.currentText(),
                                   float(self.crystal_selector.textA.text()),
                                   float(self.crystal_selector.textB.text()),
                                   float(self.crystal_selector.textC.text()),
                                   float(
                                       self.crystal_selector.textAlpha.text()),
                                   float(
                                       self.crystal_selector.textBeta.text()),
                                   float(
                                       self.crystal_selector.textGamma.text()))
        if all_good:
            self.done(1)
            return self.crystal

    def cancel_clicked(self):
        self.done(0)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent = None):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.sample = Sample

        # region GUI elements
        self.init_menubar()
        self.listWidgetCrystals = QtWidgets.QListWidget()
        self.listWidgetCrystals.selectionModel().selectionChanged.connect(
            self.update_all)
        self.butNewCrystal = QtWidgets.QPushButton('New')
        self.butNewCrystal.clicked.connect(self.butNewCrystal_clicked)
        self.butEditCrystal = QtWidgets.QPushButton('Edit')
        self.butEditCrystal.clicked.connect(self.butEditCrystal_clicked)
        self.butDeleteCrystal = QtWidgets.QPushButton('Delete')
        self.butDeleteCrystal.clicked.connect(self.butDeleteCrystal_clicked)
        self.butInterfaceCalculator = QtWidgets.QPushButton(
            'Interface Calculator')
        self.butInterfaceCalculator.clicked.connect(
            self.butInterfaceCalculator_clicked)
        self.crystalInfo = CrystalInfoWidget()
        self.plotCanvas = PolePlot()

        self.butSetParams = QtWidgets.QPushButton('Set Parameters')
        self.butSetOrientation = QtWidgets.QPushButton('Set Orientation')
        self.butSetParams.pressed.connect(self.set_params)
        self.butSetOrientation.pressed.connect(self.set_orientation)

        # endregion

        # region layout
        self.main_widget = QtWidgets.QWidget(self)
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.listWidgetCrystals, 1, 0, 1, 2)
        crystalButtonHLayout = QtWidgets.QHBoxLayout()
        grid.addLayout(crystalButtonHLayout, 0,0, 1, 2)
        crystalButtonHLayout.addWidget(self.butNewCrystal, 0)
        crystalButtonHLayout.addWidget(self.butEditCrystal, 1)
        crystalButtonHLayout.addWidget(self.butDeleteCrystal, 2)
        # grid.addWidget(self.labelInformationLabels, 2, 0)
        # grid.addWidget(self.labelInformationValues, 2, 1)
        grid.addWidget(self.crystalInfo, 2,0,1,2)
        grid.addWidget(self.plotCanvas, 0, 2, 5, 1)
        #self.docker = QtWidgets.QDockWidget("Dockable", self)
        #self.docker.setWidget(self.plotCanvas)
        #self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.docker)
        grid.addWidget(self.butSetParams, 3,0)
        grid.addWidget(self.butSetOrientation, 3,1)
        grid.addWidget(self.butInterfaceCalculator, 4,0,1,2)


        self.main_widget.setLayout(grid)
        self.setCentralWidget(self.main_widget)
        # endregion




    def init_menubar(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        optionsMenu = mainMenu.addMenu('Options')

        exitButton = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        selectPoleProfileButton = QtWidgets.QAction('Set pole profile...', self)
        selectPoleProfileButton.triggered.connect(self.select_pole_profile)
        optionsMenu.addAction(selectPoleProfileButton)

    def set_params(self):
        try:
            idx = self.listWidgetCrystals.currentRow()
            dialog = CrystalSelectorDialog(crystal=self.sample.crystals[idx])
            if dialog.exec_():
                self.sample.crystals[idx] = dialog.crystal
                self.update_crystal_widget_list(idx)
        except:
            pass

    def set_orientation(self):
        try:
            idx = self.listWidgetCrystals.currentRow()
            crystal = self.sample.crystals[idx]
            dialog = SetOrientation(crystal)
        except:
            dialog = SetOrientation()
        if dialog.exec_():
            idx = self.listWidgetCrystals.currentRow()
            self.sample.crystals[idx].beam_direction = dialog.known_dir
            self.sample.crystals[idx].reference_direction = dialog.ref_dir
            self.sample.crystals[idx].rotation_correction = dialog.angle
            self.sample.crystals[idx].a0 = dialog.a0
            self.sample.crystals[idx].b0 = dialog.b0
            self.update_all()

    def select_pole_profile(self):
        dialog = SelectPolesDialog()
        if dialog.exec_():
            self.update_all()

    def butInterfaceCalculator_clicked(self):
        window = QtWidgets.QMainWindow(self)
        window.setCentralWidget(TiltSeriesCalculator(self.sample))
        window.move(100,100)
        window.setWindowTitle("Interface Calculator")
        window.show()

    def butNewCrystal_clicked(self):
        dialog = CrystalSelectorDialog(
            num_already_exist=len(self.sample.crystals))
        if dialog.exec_():
            self.sample.crystals.append(dialog.crystal)
            self.listWidgetCrystals.addItem(self.sample.crystals[-1].name)
            self.listWidgetCrystals.setCurrentRow(
                self.listWidgetCrystals.count()-1)

    def butEditCrystal_clicked(self):
        try:
            idx = self.listWidgetCrystals.currentRow()
            dialog = CrystalSelectorDialog(crystal=self.sample.crystals[idx])
            if dialog.exec_():
                self.sample.crystals[idx] = dialog.crystal
                self.update_crystal_widget_list(idx)
        except:
            pass

    def butDeleteCrystal_clicked(self):
        try:
            idx = self.listWidgetCrystals.currentRow()
            del self.sample.crystals[idx]
            self.update_crystal_widget_list()
        except IndexError: # no crystals
            pass

    def update_crystal_info_label(self, crystal):
        self.crystalInfo.setInfo(crystal)

    def update_crystal_widget_list(self, idx=0):
        self.listWidgetCrystals.clear()
        for crystal in self.sample.crystals:
            self.listWidgetCrystals.addItem(crystal.name)
        self.listWidgetCrystals.setCurrentRow(idx)

    def update_all(self):
        try:
            self.update_crystal_info_label(
                self.sample.crystals[self.listWidgetCrystals.currentRow()])
            self.plotCanvas.plot(
                self.sample.crystals[self.listWidgetCrystals.currentRow()])
            #self.plotCanvas.crystal = self.sample.crystals[
                #self.listWidgetCrystals.currentRow()]
        except IndexError: # no crystals
            #self.labelInformationValues.setText('')
            print('update all failed')





class CrystalInfoWidget(QtWidgets.QWidget):

    def __init__(self, parent = None):
        QtWidgets.QMainWindow.__init__(self)
        self.crystal = None

        rows = 12
        cols = 2
        self.labels = [[0 for y in range(cols)] for x in range(rows)]
        hbox = []
        for x in range(rows):
            hbox.append(QtWidgets.QHBoxLayout())
            hbox[x].setSpacing(0)
            hbox[x].setContentsMargins(0,0,0,0)
            for y in range(cols):
                self.labels[x][y] = QtWidgets.QLabel()
                self.labels[x][y].setStyleSheet('background-color: rgba(0,0,0,180);'
                                                'color: white;'
                                                'border: 1px solid gray')
                self.labels[x][y].setFrameShape(QtWidgets.QFrame.Panel)
                #self.labels[x][y].setFrameShadow(QtWidgets.QFrame.Sunken)
                self.labels[x][y]

        for x in range(rows):
            for y in range(cols):
                hbox[x].addWidget(self.labels[x][y])

        vbox = QtWidgets.QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(0,0,0,0)
        for x in range (rows):
            vbox.addLayout(hbox[x])

        self.setLayout(vbox)

        #self._test_with_fake_crystal()

    def setInfo(self, crystal):
        self.crystal = crystal
        # Name
        self.labels[0][0].setText(crystal.name)
        font = QtGui.QFont("Times", 12, QtGui.QFont.Bold)
        self.labels[0][0].setFont(font)
        self.labels[0][0].setAlignment(QtCore.Qt.AlignCenter)
        self.labels[0][1].setVisible(False)

        # System
        self.labels[1][0].setText(''.join(('System: ', crystal.system)))
        font = QtGui.QFont("Times", 10, QtGui.QFont.Bold)
        self.labels[1][0].setFont(font)
        self.labels[1][1].setVisible(False)

        # Parameters
        self.labels[2][0].setText('Parameters')
        font = QtGui.QFont("Times", 10)
        self.labels[2][0].setFont(font)
        self.labels[2][1].setVisible(False)
        font = QtGui.QFont("Times", 9)
        for i in range(3,6):
            for j in range(2):
                self.labels[i][j].setFont(font)
        self.labels[3][0].setText(''.join(('a: ', str(crystal.a))))
        self.labels[4][0].setText(''.join(('b: ', str(crystal.b))))
        self.labels[5][0].setText(''.join(('c: ', str(crystal.c))))
        self.labels[3][1].setText(''.join(('\u03b1: ', str(crystal.alpha))))
        self.labels[4][1].setText(''.join(('\u03b2: ', str(crystal.beta))))
        self.labels[5][1].setText(''.join(('\u03b3: ', str(crystal.gamma))))

        # Orientation
        self.labels[6][0].setText('Known Pole')
        font = QtGui.QFont("Times", 10)
        self.labels[6][0].setFont(font)
        self.labels[6][1].setText('Reference Pole')
        self.labels[6][1].setFont(font)
        font = QtGui.QFont("Times", 9)
        for i in range(7, 12):
            for j in range(2):
                self.labels[i][j].setFont(font)
        try:
            self.labels[7][0].setText(
                ''.join(('u: ', str(crystal.beam_direction[0]))))
            self.labels[8][0].setText(
                ''.join(('v: ', str(crystal.beam_direction[1]))))
            self.labels[9][0].setText(
                ''.join(('w: ', str(crystal.beam_direction[2]))))
            self.labels[10][0].setText(
                ''.join(('\u03b10: ', str(crystal.a0))))
            self.labels[11][0].setText(
                ''.join(('\u03b20: ', str(crystal.b0))))
        except TypeError:
            self.labels[7][0].setText('u: ')
            self.labels[8][0].setText('v: ')
            self.labels[9][0].setText('w: ')
            self.labels[10][0].setText('\u03b1: ')
            self.labels[11][0].setText('\u03b2: ')
        try:
            self.labels[7][1].setText(
                ''.join(('u: ', str(crystal.reference_direction[0]))))
            self.labels[8][1].setText(
                ''.join(('v: ', str(crystal.reference_direction[1]))))
            self.labels[9][1].setText(
                ''.join(('w: ', str(crystal.reference_direction[2]))))
            self.labels[10][1].setText(
                ''.join(('angle to x: ', str(crystal.rotation_correction))))
        except TypeError:
            self.labels[7][0].setText('u: ')
            self.labels[8][0].setText('v: ')
            self.labels[9][0].setText('w: ')
            self.labels[10][0].setText('\u03b1: ')
            self.labels[11][0].setText('\u03b2: ')
        #self.labels[11][1].setVisible(False)



    def _test_with_fake_crystal(self):
        c = Crystal('Test Crystal', 'Cubic', 1, 1, 1, 90, 90, 90,
                    None, None)
        self.setInfo(c)


class EditPolesDialog(QtWidgets.QDialog):

    def __init__(self, profile_dict, parent=None):
        super(EditPolesDialog, self).__init__(parent)
        self.setWindowTitle("Edit profile")
        self.profile_dict = profile_dict
        self.temp_profile_dict = self.profile_dict.copy() # copy of dictionary
        self.change_nothing = False # use this to flag that program shouldn't edit dictionary.

        # region GUI elements
        self.labList = QtWidgets.QLabel('Pole list:')
        self.labDisplayOptions = QtWidgets.QLabel('Display options:')
        self.listPoles = QtWidgets.QListWidget()
        self.listPoles.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.butAdd = QtWidgets.QPushButton('Add...')
        self.butRemove = QtWidgets.QPushButton('Remove')
        self.labType = QtWidgets.QLabel('Marker type:')
        self.comboType = QtWidgets.QComboBox()
        self.labSize = QtWidgets.QLabel('Marker size:')
        self.comboSize = QtWidgets.QComboBox()
        self.labColor = QtWidgets.QLabel('Marker color:')
        self.butColor = QtWidgets.QPushButton("Color")
        self.butOk = QtWidgets.QPushButton('Ok')
        self.butCancel = QtWidgets.QPushButton('Cancel')

        # Connect signals
        self.butOk.clicked.connect(self.butOk_clicked)
        self.butCancel.clicked.connect(self.butCancel_clicked)
        self.butAdd.clicked.connect(self.butAdd_clicked)
        self.butRemove.clicked.connect(self.butRemove_clicked)
        self.butColor.clicked.connect(self.butColor_clicked)
        self.listPoles.selectionModel().selectionChanged.connect(self.listPoles_selectionChanged)
        self.comboSize.currentTextChanged.connect(self.comboSize_changed)
        self.comboType.currentTextChanged.connect(self.comboType_changed)

        # Poplulate lists
        self.change_nothing = True
        ms = [5, 10, 15, 20, 25, 30, 35, 40, 50, 75, 100, 125, 150]
        [self.comboSize.addItem(str(this_ms)) for this_ms in ms]
        self.marker_types = {'circle': 'o',
                             'square': 's',
                             'triangle dn': 'v',
                             'triangle up': '^',
                             'triangle lft': '<',
                             'triangle rt': '>',
                             'star': '*',
                             'pentagon': 'p',
                             'hexagon vrt': 'h',
                             'hexagon hor': 'H',
                             'plus': 'P'}
        [self.comboType.addItem(this_mt) for this_mt in self.marker_types]

        self.colors = [[238,238,238],
                       [239,154,154],
                       [244,143,177],
                       [206,147,216],
                       [179,157,219],
                       [159,168,218],
                       [144,202,249],
                       [129,212,250],
                       [128,222,234],
                       [128,203,196],
                       [165,214,167],
                       [197,225,165],
                       [230,238,156],
                       [255,245,157],
                       [255,224,130],
                       [255,204,128],
                       [255,171,145],
                       [189,189,189]]


        self.change_nothing = False

        # endregion

        # region layout
        topLayout = QtWidgets.QVBoxLayout()
        okLayout = QtWidgets.QHBoxLayout()
        upperLayout = QtWidgets.QHBoxLayout()
        listLayout = QtWidgets.QVBoxLayout()
        optionsLayout = QtWidgets.QVBoxLayout()
        addRemoveLayout = QtWidgets.QHBoxLayout()
        topLayout.addLayout(upperLayout)
        topLayout.addLayout(okLayout)
        okLayout.addWidget(self.butCancel)
        okLayout.addWidget(self.butOk)
        upperLayout.addLayout(listLayout)
        upperLayout.addLayout(optionsLayout)
        listLayout.addWidget(self.labList)
        listLayout.addWidget(self.listPoles)
        listLayout.addLayout(addRemoveLayout)
        addRemoveLayout.addWidget(self.butAdd)
        addRemoveLayout.addWidget(self.butRemove)
        optionsLayout.addWidget(self.labDisplayOptions)
        optionsLayout.addWidget(self.labType)
        optionsLayout.addWidget(self.comboType)
        optionsLayout.addWidget(self.labSize)
        optionsLayout.addWidget(self.comboSize)
        optionsLayout.addWidget(self.labColor)
        optionsLayout.addWidget(self.butColor)
        optionsLayout.addStretch()

        self.setLayout(topLayout)
        # endregion

        # populate list
        for key in profile_dict.keys():
            self.listPoles.addItem(key)

    def listPoles_selectionChanged(self):
        selection = self.listPoles.selectedItems()
        if len(selection) > 0:
            item = selection[0].text()

    def comboSize_changed(self, ms):
        if not self.change_nothing:
            selection = self.listPoles.selectedItems()
            for item in self.listPoles.selectedItems():
                self.temp_profile_dict[item.text()]['ms'] = int(ms)

    def comboType_changed(self, mt):
        if not self.change_nothing:
            selection = self.listPoles.selectedItems()
            for item in self.listPoles.selectedItems():
                self.temp_profile_dict[item.text()]['marker'] = self.marker_types[mt]

    def butColor_clicked(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            new_color = color.getRgb()[:3]
            for item in self.listPoles.selectedItems():
                self.temp_profile_dict[item.text()]['color'] = new_color

    def butOk_clicked(self):
        self.accept()

    def butCancel_clicked(self):
        if self.temp_profile_dict != self.profile_dict:
            msg = QtWidgets.QMessageBox.question(self, 'Cancel', 'Discard all changes to pole profiles?',
                                                 QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                                                 QtWidgets.QMessageBox.No)
            if msg == QtWidgets.QMessageBox.Yes:
                self.reject()
        else:
            self.reject()

    def butAdd_clicked(self):
        text, okPressed = QtWidgets.QInputDialog.getText(
            self, "Add poles", "Type poles to add. Separate with comma:", QtWidgets.QLineEdit.Normal, "")
        if okPressed and text != '':
            problems = False
            for t in text.split(','):
                if len(t) == 3:
                    try:
                        _ = int(t)
                        pole_list = [self.listPoles.item(i).text() for i in range(self.listPoles.count())]
                        if t not in pole_list:
                            self.listPoles.addItem(t)
                            self.temp_profile_dict[t] = {"color": [189,189,189],"marker": "o","ms": 15}
                    except ValueError:
                        problems = True
                else:
                    problems = True
            if problems:
                msg = QtWidgets.QMessageBox.information(self, 'Invalid pole',
                                                        'Some or all poles could not be added. Please check typos.',
                                                        QtWidgets.QMessageBox.Ok)

    def butRemove_clicked(self):
        for item in self.listPoles.selectedItems():
            self.listPoles.takeItem(self.listPoles.row(item))
            del(self.temp_profile_dict[item.text()])

class SelectPolesDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(SelectPolesDialog, self).__init__(parent)
        self.setWindowTitle("Select pole plot profile")

        with open('data/markers.json', 'r') as fp:
            self.markerdict = json.load(fp)

        self.changed = False

        # region GUI elements
        self.selectLabel = QtWidgets.QLabel('Select a profile from the list')
        self.listProfiles = QtWidgets.QListWidget()
        self.butNew = QtWidgets.QPushButton('New...')
        self.butEdit = QtWidgets.QPushButton('Edit...')
        self.butCopy = QtWidgets.QPushButton('Copy...')
        self.butDelete = QtWidgets.QPushButton('Delete')
        self.butOk = QtWidgets.QPushButton('Ok')
        self.butCancel = QtWidgets.QPushButton('Cancel')
        self.butNew.clicked.connect(self.butNew_clicked)
        self.butEdit.clicked.connect(self.butEdit_clicked)
        self.butCopy.clicked.connect(self.butCopy_clicked)
        self.butDelete.clicked.connect(self.butDelete_clicked)
        self.butOk.clicked.connect(self.butOk_clicked)
        self.butCancel.clicked.connect(self.butCancel_clicked)
        self.listProfiles.selectionModel().selectionChanged.connect(self.selection_changed)
        # endregion

        # region layout
        topLayout = QtWidgets.QVBoxLayout()
        okLayout = QtWidgets.QHBoxLayout()
        listLayout = QtWidgets.QHBoxLayout()
        newEditLayout = QtWidgets.QVBoxLayout()

        topLayout.addLayout(listLayout)
        topLayout.addLayout(okLayout)
        okLayout.addWidget(self.butCancel)
        okLayout.addWidget(self.butOk)
        listLayout.addWidget(self.listProfiles)
        listLayout.addLayout(newEditLayout)
        newEditLayout.addWidget(self.butNew)
        newEditLayout.addWidget(self.butEdit)
        newEditLayout.addWidget(self.butCopy)
        newEditLayout.addWidget(self.butDelete)

        self.setLayout(topLayout)
        # endregion

        self.fill_list()

    def butNew_clicked(self):
        name, okPressed = QtWidgets.QInputDialog.getText(self, "New", "Profile name:",
                                                         QtWidgets.QLineEdit.Normal, "")
        if name in list(self.markerdict.keys()):
            msg = QtWidgets.QMessageBox.information(self, 'Invalid name',
                'Cannot create profile. This profile name is already in use.',
                                                    QtWidgets.QMessageBox.Ok)
        else:
            if okPressed and name != '':
                self.markerdict[name] = self.markerdict['Default']
                self.fill_list(selection=name)
                self.changed = True

    def butEdit_clicked(self):
        selection = self.listProfiles.currentItem().text()

        if selection == 'Default':
            msg = QtWidgets.QMessageBox.information(self, "Can't edit",
                                                    'Cannot make changes to the default profile.',
                                                    QtWidgets.QMessageBox.Ok)
        else:
            dialog = EditPolesDialog(self.markerdict[selection])
            if dialog.exec_():
                self.markerdict[selection] = dialog.temp_profile_dict
                self.changed = True

    def butDelete_clicked(self):
        name = self.listProfiles.currentItem().text()
        buttonReply = QtWidgets.QMessageBox.question(
            self, 'Delete profile?',
            "".join(("Are you sure you wish to delete ", name, "?")),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if buttonReply == QtWidgets.QMessageBox.Yes:
            del self.markerdict[name]
            self.fill_list()
            self.changed = True

    def butCopy_clicked(self):
        copy_name = self.listProfiles.currentItem().text()
        name, okPressed = QtWidgets.QInputDialog.getText(self, "Copy",
                                                         "Profile name:",
                                                         QtWidgets.QLineEdit.Normal, "")
        if name in list(self.markerdict.keys()):
            msg = QtWidgets.QMessageBox.information(self, 'Invalid name',
                'Cannot create profile. This profile name is already in use.',
                                                    QtWidgets.QMessageBox.Ok)
        else:
            if okPressed and name != '':
                self.markerdict[name] = self.markerdict[copy_name]
                self.fill_list(selection=name)
                self.changed = True

    def butOk_clicked(self):
        selection = self.listProfiles.currentItem().text()
        self.markerdict['Current'] = selection
        with open('data/markers.json', 'w') as fp:
            json.dump(self.markerdict, fp, sort_keys=True, indent=4)
        self.accept()

    def butCancel_clicked(self):
        if self.changed:
            msg = QtWidgets.QMessageBox.question(self, 'Cancel', 'Discard all changes to pole profiles?',
                                                 QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                                                 QtWidgets.QMessageBox.No)
            if msg == QtWidgets.QMessageBox.Yes:
                self.reject()
        else:
            self.reject()

    def fill_list(self, selection=None):
        profiles = list(self.markerdict.keys())
        profiles.remove('Current')  # Current is not a profile, it tells which is the last used.
        profiles.sort()
        profiles.insert(0, profiles.pop(profiles.index("Default")))
        self.listProfiles.clear()
        for p in profiles:
            self.listProfiles.addItem(p)
        if selection is None:
            self.listProfiles.setCurrentRow(profiles.index(self.markerdict["Current"]))
        else:
            self.listProfiles.setCurrentRow(profiles.index(selection))
        self.selection_changed()

    def selection_changed(self):
        if self.listProfiles.currentRow() == 0:
            self.butDelete.setEnabled(False)
        else:
            self.butDelete.setEnabled(True)


class SetOrientation(QtWidgets.QDialog):

    def __init__(self, crystal=None, parent = None):
        super(SetOrientation, self).__init__(parent)
        self.setWindowTitle("Set crystal orientation")
        self.zero_tilt_direction = [1,0,0]
        self.angle = 0
        self.alpha_tilt_dir = [0,0,1]
        self.ref_dir = [0,0,1]
        self.a0 = 0
        self.b0 = 0
        self.known_dir = [1,1,1]

        self.setModal(True)

        self.butCancel = QtWidgets.QPushButton('Cancel')
        self.butCancel.clicked.connect(self.cancel_clicked)
        self.butOK = QtWidgets.QPushButton('OK')
        self.butOK.setDefault(True)
        self.butOK.clicked.connect(self.ok_clicked)
        but_hbox = QtWidgets.QHBoxLayout()
        but_hbox.addStretch(99)
        but_hbox.addWidget(self.butCancel)
        but_hbox.addWidget(self.butOK)

        methodBox = QtWidgets.QGroupBox()
        self.method1 = QtWidgets.QRadioButton("Method 1")
        self.method2 = QtWidgets.QRadioButton('Method 2')
        self.method1.toggled.connect(self.method1_toggle)
        option_hbox = QtWidgets.QHBoxLayout()
        option_hbox.addWidget(self.method1)
        option_hbox.addWidget(self.method2)
        option_hbox.addStretch(99)
        methodBox.setLayout(option_hbox)

        # method 1 and 2 frame setup
        self.grid_method1 = QtWidgets.QGridLayout()
        self.grid_method2 = QtWidgets.QGridLayout()
        self.frame_method1 = QtWidgets.QFrame()
        self.frame_method2 = QtWidgets.QFrame()

        self.frame_method1.setLayout(self.grid_method1)
        self.frame_method2.setLayout(self.grid_method2)

        # method 1
        self.m1LblZoneAxis = QtWidgets.QLabel('Known zone axis:')
        self.m1LblZaU = QtWidgets.QLabel('u:')
        self.m1LblZaV = QtWidgets.QLabel('v:')
        self.m1LblZaW = QtWidgets.QLabel('w:')
        self.m1LblZaAlpha = QtWidgets.QLabel('\u03b1 tilt:')
        self.m1LblZaBeta = QtWidgets.QLabel('\u03b2 tilt:')
        self.m1TxtZaU = QtWidgets.QLineEdit()
        self.m1TxtZaV = QtWidgets.QLineEdit()
        self.m1TxtZaW = QtWidgets.QLineEdit()
        self.m1TxtZaAlpha = QtWidgets.QLineEdit()
        self.m1TxtZaBeta = QtWidgets.QLineEdit()
        self.m1LblRef = QtWidgets.QLabel('Reference direction:')
        self.m1LblRefU = QtWidgets.QLabel('u:')
        self.m1LblRefV = QtWidgets.QLabel('v:')
        self.m1LblRefW = QtWidgets.QLabel('w:')
        self.m1TxtRefU = QtWidgets.QLineEdit()
        self.m1TxtRefV = QtWidgets.QLineEdit()
        self.m1TxtRefW = QtWidgets.QLineEdit()
        self.m1LblAngle = QtWidgets.QLabel(
            'Angle between reference and \u03b1 tilt:')
        self.m1TxtAngle = QtWidgets.QLineEdit()

        self.grid_method1.addWidget(self.m1LblZoneAxis, 0, 0)
        self.grid_method1.addWidget(self.m1LblZaU, 0, 1)
        self.grid_method1.addWidget(self.m1TxtZaU, 0, 2)
        self.grid_method1.addWidget(self.m1LblZaV, 0, 3)
        self.grid_method1.addWidget(self.m1TxtZaV, 0, 4)
        self.grid_method1.addWidget(self.m1LblZaW, 0, 5)
        self.grid_method1.addWidget(self.m1TxtZaW, 0, 6)
        self.grid_method1.addWidget(self.m1LblZaAlpha, 0, 7)
        self.grid_method1.addWidget(self.m1TxtZaAlpha, 0, 8)
        self.grid_method1.addWidget(self.m1LblZaBeta, 0, 9)
        self.grid_method1.addWidget(self.m1TxtZaBeta, 0, 10)
        self.grid_method1.addWidget(self.m1LblRef, 1, 0)
        self.grid_method1.addWidget(self.m1LblRefU, 1, 1)
        self.grid_method1.addWidget(self.m1TxtRefU, 1, 2)
        self.grid_method1.addWidget(self.m1LblRefV, 1, 3)
        self.grid_method1.addWidget(self.m1TxtRefV, 1, 4)
        self.grid_method1.addWidget(self.m1LblRefW, 1, 5)
        self.grid_method1.addWidget(self.m1TxtRefW, 1, 6)
        self.grid_method1.addWidget(self.m1LblAngle, 2, 0, 1, 3)
        self.grid_method1.addWidget(self.m1TxtAngle, 2, 4)


        # method 2
        lbl_method2 = QtWidgets.QLabel('Method 2')
        self.grid_method2.addWidget(lbl_method2, 0,0)

        # adjust textboxes
        self.validator = QtGui.QDoubleValidator()
        textboxes = [self.m1TxtAngle, self.m1TxtZaU, self.m1TxtZaV,
                     self.m1TxtZaW, self.m1TxtRefU, self.m1TxtRefV,
                     self.m1TxtRefW, self.m1TxtZaAlpha, self.m1TxtZaBeta]
        for i in textboxes:
            i.setMaximumWidth(50)
            i.setValidator(self.validator)

        vbox = QtWidgets.QVBoxLayout()
        #vbox.addWidget(methodBox)
        vbox.addWidget(self.frame_method1)
        #vbox.addWidget(self.frame_method2)
        vbox.addLayout(but_hbox)
        self.setLayout(vbox)

        self.method1.setChecked(True)

        if crystal is not None:
            self.m1TxtZaAlpha.setText(str(crystal.a0))
            self.m1TxtZaBeta.setText(str(crystal.b0))
            self.m1TxtAngle.setText(str(crystal.rotation_correction))
            self.m1TxtRefU.setText(str(crystal.reference_direction[0]))
            self.m1TxtRefV.setText(str(crystal.reference_direction[1]))
            self.m1TxtRefW.setText(str(crystal.reference_direction[2]))
            self.m1TxtZaU.setText(str(crystal.beam_direction[0]))
            self.m1TxtZaV.setText(str(crystal.beam_direction[1]))
            self.m1TxtZaW.setText(str(crystal.beam_direction[2]))
            #self.m1TxtRefU


    def ok_clicked(self):

        #if self.method1.isChecked():
            #try:
        known_zone_direction = [float(self.m1TxtZaU.text()),
                                float(self.m1TxtZaV.text()),
                                float(self.m1TxtZaW.text())]
        self.known_dir = known_zone_direction
        known_alpha = float(self.m1TxtZaAlpha.text())
        known_beta = float(self.m1TxtZaBeta.text())
        self.ref_dir = [float(self.m1TxtRefU.text()),
                        float(self.m1TxtRefV.text()),
                        float(self.m1TxtRefW.text())]
        self.angle = float(self.m1TxtAngle.text())

        self.a0 = float(self.m1TxtZaAlpha.text())
        self.b0 = float(self.m1TxtZaBeta.text())

        self.zero_tilt_dir = zero_tilt_direction(
            known_zone_direction,
            known_alpha,
            known_beta,
            self.ref_dir,
            self.angle)
        # self.angle = absolute_rotation(known_zone_direction,
        #                                ref_direction,
        #                                angle)
        self.done(1)
        return self.known_dir, self.ref_dir, self.angle, self.a0, self.b0
            # except:
            #     mb = QtWidgets.QMessageBox()
            #
            #     mb.setIcon(QtWidgets.QMessageBox.Information)
            #     mb.setWindowTitle('Error')
            #     mb.setText(
            #         'Fill out all values.')
            #     mb.setStandardButtons(QtWidgets.QMessageBox.Ok)
            #     mb.raise_()
            #     mb.setModal(True)
            #     mb.exec_()
            #     mb.show()


    def cancel_clicked(self):
            self.done(0)

    def method1_toggle(self, enabled):
        if enabled:
            self.frame_method1.show()
            self.frame_method2.hide()
        else:
            self.frame_method1.setVisible(False)
            self.frame_method2.setVisible(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    with open('data/style.qss', 'r') as f:
        stylesheet = f.read()
        print(stylesheet)
    app.setStyleSheet(stylesheet)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    window = MainWindow()
    window.show()
    window.setWindowTitle("NanoCartographer")
    window.setWindowIcon(QtGui.QIcon('icon.png'))
    sys.exit(app.exec_())

