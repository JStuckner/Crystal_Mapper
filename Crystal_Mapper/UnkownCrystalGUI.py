import sys
from PyQt5 import QtCore, QtGui, QtWidgets

import matplotlib
matplotlib.use('QT5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from crystal_math import get_band_coordinates
from gui import PolePlot

class AddBandDialog(QtWidgets.QDialog):

    def __init__(self, parent=None, angle='0', major=True):
        super(AddBandDialog, self).__init__(parent)

        self.major = major
        self.angle = angle

        self.setModal(True)

        self.butCancel = QtWidgets.QPushButton('Cancel')
        self.butCancel.clicked.connect(self.cancel_clicked)
        self.butOK = QtWidgets.QPushButton('OK')
        self.butOK.setDefault(True)
        self.butOK.clicked.connect(self.ok_clicked)
        but_hbox = QtWidgets.QHBoxLayout()
        but_hbox.addWidget(self.butCancel)
        but_hbox.addWidget(self.butOK)

        self.lblAngle = QtWidgets.QLabel('Angle to x tilt:')
        self.lblType = QtWidgets.QLabel('Band type:')
        self.comboBandType = QtWidgets.QComboBox(self)
        self.comboBandType.addItem('Major')
        self.comboBandType.addItem('Minor')
        self.txtAngle = QtWidgets.QLineEdit()
        if not self.major:
            self.comboBandType.setCurrentIndex(1)
        self.txtAngle.setText(self.angle)

        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.lblAngle, 0,0)
        grid.addWidget(self.txtAngle, 0, 1)
        grid.addWidget(self.lblType, 1, 0)
        grid.addWidget(self.comboBandType, 1, 1)
        grid.addLayout(but_hbox, 2, 0, 1, 2)

        self.setLayout(grid)

        self.show()


    def ok_clicked(self):
        self.major = True if self.comboBandType.currentIndex() == 0 else False
        self.angle = self.txtAngle.text()
        try:
            _test = float(self.angle)
            self.done(1)
            return self.major, self.angle
        except:
            pass

    def cancel_clicked(self):
        self.done(0)

class PoleInterface(QtWidgets.QWidget):

    def __init__(self, parent=None, previous=0):
        QtWidgets.QWidget.__init__(self)
        self.parent = parent

        self.valid = False #set to true when ready to plot
        self.bands = [] # holds list of bands [angle, type (major = 1)

        grid = QtWidgets.QGridLayout()

        self.checkBox = QtWidgets.QCheckBox()
        self.checkBox.setChecked(True)
        self.lblPole = QtWidgets.QLabel('Pole:')
        self.lblXTilt = QtWidgets.QLabel('X tilt:')
        self.lblYTilt = QtWidgets.QLabel('Y tilt:')
        self.lblType = QtWidgets.QLabel('Type:')
        self.lblBands = QtWidgets.QLabel('Bands:')
        self.lblEditBands = QtWidgets.QLabel('Edit bands:')
        self.lblU = QtWidgets.QLabel('u:')
        self.lblV = QtWidgets.QLabel('v:')
        self.lblW = QtWidgets.QLabel('w:')

        name = ''.join(('Pole ', str(previous+1)))
        self.txtName = QtWidgets.QLineEdit(name)
        self.txtXTilt = QtWidgets.QLineEdit()
        self.txtYTilt = QtWidgets.QLineEdit()
        self.txtU = QtWidgets.QLineEdit()
        self.txtV = QtWidgets.QLineEdit()
        self.txtW = QtWidgets.QLineEdit()
        self.comboPoleType = QtWidgets.QComboBox(self)
        self.comboPoleType.addItem('Major')
        self.comboPoleType.addItem('Minor')
        self.comboBands = QtWidgets.QComboBox()

        self.butNewBand = QtWidgets.QPushButton('New')
        self.butEditBand = QtWidgets.QPushButton('Edit')
        self.butDeleteBand = QtWidgets.QPushButton('Delete')
        self.butNewBand.pressed.connect(self.add_band)
        self.butEditBand.pressed.connect(self.edit_band)
        self.butDeleteBand.pressed.connect(self.delete_band)

        grid.addWidget(self.lblPole, 0, 1)
        grid.addWidget(self.lblXTilt, 0, 2)
        grid.addWidget(self.lblYTilt, 0, 3)
        grid.addWidget(self.lblU, 0, 4)
        grid.addWidget(self.lblV, 0, 5)
        grid.addWidget(self.lblW, 0, 6)
        grid.addWidget(self.lblType, 0, 7)
        grid.addWidget(self.lblBands, 0 ,8)
        grid.addWidget(self.lblEditBands, 0, 9, 1, 3)

        grid.addWidget(self.checkBox, 1, 0)
        grid.addWidget(self.txtName, 1, 1)
        grid.addWidget(self.txtXTilt, 1, 2)
        grid.addWidget(self.txtYTilt, 1, 3)
        grid.addWidget(self.txtU, 1, 4)
        grid.addWidget(self.txtV, 1, 5)
        grid.addWidget(self.txtW, 1, 6)
        grid.addWidget(self.comboPoleType, 1, 7)
        grid.addWidget(self.comboBands, 1, 8)
        grid.addWidget(self.butNewBand, 1, 9)
        grid.addWidget(self.butEditBand, 1, 10)
        grid.addWidget(self.butDeleteBand, 1, 11)

        self.setLayout(grid)

        # region Fine tune layout
        self.comboBands.setMinimumWidth(180)
        textboxes = [self.txtName,
                     self.txtW, self.txtV, self.txtU,
                     self.txtYTilt, self.txtXTilt]
        labels = [self.lblType, self.lblEditBands, self.lblYTilt,
                  self.lblXTilt, self.lblBands, self.lblPole,
                  self.lblU, self.lblV, self.lblW]
        validator = QtGui.QDoubleValidator()
        for textbox in textboxes[1:]:
            textbox.setMaximumWidth(50)
            textbox.setValidator(validator)
        for label in labels:
            label.setAlignment(
                QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)
        for textbox in [self.txtXTilt, self.txtYTilt]:
            textbox.textChanged.connect(self.update_plot)
        # endregion

    def add_band(self):
        dialog = AddBandDialog()
        if dialog.exec():
            self.bands.append([dialog.angle, dialog.major])
            self.update_band_list(len(self.bands)-1)
            self.update_plot()

    def edit_band(self):
        idx = self.comboBands.currentIndex()
        angle, major = self.bands[idx]
        dialog = AddBandDialog(angle = angle, major = major)
        if dialog.exec():
            self.bands[idx] = [dialog.angle, dialog.major]
            self.update_band_list(idx)
            self.update_plot()

    def delete_band(self):
        try:
            idx = self.comboBands.currentIndex()
            del self.bands[idx]
            self.update_band_list(0)
            self.update_plot()
        except:
            pass

    def update_band_list(self, idx = None):
        self.comboBands.clear()
        for band in self.bands:
            type = 'Major' if band[1] else 'Minor'
            string = ''.join(('Angle: ', band[0],
                              '   Type: ', type))
            self.comboBands.addItem(string)
        if idx is not None:
            self.comboBands.setCurrentIndex(idx)

    def update_plot(self):
        self.parent.update_plot()


class UnknownCrystalPlot(FigureCanvas):

    def __init__(self, parent=None, width=4, height=4, dpi=200):
        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect('equal', 'box')
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self, poles):
        plt.cla()
        ax = self.ax
        fig = self.fig
        plt.tight_layout()
        ax.spines['left'].set_position('zero')
        ax.spines['right'].set_color('none')
        ax.spines['bottom'].set_position('zero')
        ax.spines['top'].set_color('none')
        #ax.spines['left'].set_smart_bounds(True)
        #ax.spines['bottom'].set_smart_bounds(True)
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')
        plt.xlim(-45, 45)
        plt.ylim(-45, 45)

        scs = []
        colors = []
        names = []
        for pole in poles:
            if pole['checked']:
                markerSize = 100 if pole['major'] else 50
                color = 'blue' if pole['major'] else 'red'
                scs.append(plt.scatter(pole['x'], pole['y'],
                                       marker='o',
                                       s = markerSize,
                                       c = color))
                colors.append(color)
                names.append(pole['name'])

                for band in pole['bands']:
                    markerSize = 3 if band[1] else 1
                    color = (0,0,0,0.75) if band[1] else (0.5,0.5,0.5,0.5)
                    x,y = get_band_coordinates(pole['x'],pole['y'], band[0])
                    scs.append(plt.scatter(x,y,c=color, marker='.', s=markerSize))
                    names.append(''.join((pole['name'], ': Angle = ', str(band[0]))))
                    colors.append(color)

        annot = ax.annotate("", xy=(0, 0), xytext=(10, 30),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"),
                            horizontalalignment='center',
                            color='white',
                            fontsize=12,
                            fontweight='bold')
        annot.set_visible(False)

        def update_annot(sc, ind, color, i):

            pos = sc.get_offsets()[ind["ind"][0]]
            annot.xy = pos
            #print(names)
            text = ''.join((names[i],
                            '\nX tilt = ', str(round(pos[0],1)),
                            ', Y tilt = ', str(round(pos[1],1))))
            annot.set_text(text)
            annot.get_bbox_patch().set_facecolor(color)
            annot.get_bbox_patch().set_alpha(0.8)

        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                for i, sc in enumerate(scs):
                    cont, ind = sc.contains(event)
                    if cont:
                        update_annot(sc, ind, colors[i], i)
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                        break
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)

        self.draw()

class UnknownCrystalGUI(QtWidgets.QWidget):

    def __init__(self, parent = None):
        QtWidgets.QMainWindow.__init__(self)

        self.poleWidgets = [] #list of pole widgets
        self.poles = []

        self.butAddPole = QtWidgets.QPushButton('Add Pole')
        self.butDeletePole = QtWidgets.QPushButton('Plot')
        self.butAddPole.pressed.connect(self.add_pole)
        self.butDeletePole.pressed.connect(self.delete_pole)
        hboxAddDelete = QtWidgets.QHBoxLayout()
        hboxAddDelete.addWidget(self.butAddPole, 0)
        hboxAddDelete.addWidget(self.butDeletePole, 1)
        hboxAddDelete.addStretch(99)
        self.vboxPoles = QtWidgets.QVBoxLayout()
        self.plot = UnknownCrystalPlot()
        self.plot.setMinimumWidth(500)
        self.plot.setMinimumHeight(500)

        grid = QtWidgets.QGridLayout()
        grid.addLayout(hboxAddDelete, 0, 0)
        grid.addLayout(self.vboxPoles, 1, 0)
        grid.addWidget(self.plot, 0,1,3,1)
        grid.setRowStretch(2,99)

        self.add_pole()
        self.update_plot()
        self.setLayout(grid)

    def add_pole(self):
        prev = len(self.poleWidgets)
        self.poleWidgets.append(PoleInterface(self, previous=prev))
        self.vboxPoles.addWidget(self.poleWidgets[-1],
                                 self.vboxPoles.count())


    def delete_pole(self):
        self.update_plot()

    def organize_pole_data(self):
        self.poles = []
        for p in self.poleWidgets:
            this_pole = {}
            try:
                this_pole['x'] = float(p.txtXTilt.text())
                this_pole['y'] = float(p.txtYTilt.text())
            except:
                this_pole['x'] = 0
                this_pole['y'] = 0
                #print("WARNING: something wrong with pole tilt values")
            this_pole['checked'] = p.checkBox.isChecked()
            this_pole['u'] = p.txtU.text()
            this_pole['v'] = p.txtV.text()
            this_pole['w'] = p.txtW.text()
            this_pole['major'] = True if p.comboPoleType.currentIndex() == 0 else False
            this_pole['name'] = p.txtName.text()
            bands = []
            for band in p.bands:
                bands.append([float(band[0]), band[1]])
            this_pole['bands'] = bands
            self.poles.append(this_pole)
        return self.poles

    def update_plot(self):
        self.plot.plot(self.organize_pole_data())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.setCentralWidget(UnknownCrystalGUI())
    window.move(100,100)
    window.show()
    sys.exit(app.exec_())




