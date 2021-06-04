import sys
from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np
import matplotlib
matplotlib.use('QT5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.figure
import json

from crystal_math import *
from pole_plot import PolePlot

def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clearLayout(child.layout())

class TiltPointWidget(QtWidgets.QWidget):

    def __init__(self, idx=1, alpha=0, beta=0, checked=False):
        QtWidgets.QWidget.__init__(self)

        alpha = str(np.round(alpha,1))
        beta = str(np.round(beta,1))
        idx = str(idx)

        self.checkBox = QtWidgets.QCheckBox()
        self.checkBox.setMinimumWidth(25)
        if checked:
            self.checkBox.setChecked(True)

        self.lblIdx = QtWidgets.QLabel(idx)
        self.lblAlpha = QtWidgets.QLabel('\u03b1: ')
        self.lblBeta = QtWidgets.QLabel('\u03b2: ')
        self.lblAPoint = QtWidgets.QLabel(alpha)
        self.lblBPoint = QtWidgets.QLabel(beta)

        #formatting
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.lblAPoint.setFont(font)
        self.lblBPoint.setFont(font)
        self.lblAlpha.setAlignment(QtCore.Qt.AlignRight)
        self.lblBeta.setAlignment(QtCore.Qt.AlignRight)


        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.lblIdx)
        hbox.addWidget(self.checkBox)
        hbox.addWidget(self.lblAlpha)
        hbox.addWidget(self.lblAPoint)
        hbox.addSpacing(10)
        hbox.addWidget(self.lblBeta)
        hbox.addWidget(self.lblBPoint)

        self.setLayout(hbox)


class TiltPointFrame(QtWidgets.QWidget):

    def __init__(self, a0=0, b0=0, rotation=0, step_size=1, along=True,
                       alpha_max=45, beta_max=45):
        QtWidgets.QWidget.__init__(self)

        # column headers
        lblIdx = QtWidgets.QLabel('Index')
        lblChecked = QtWidgets.QLabel('Imaged')
        lblAlpha = QtWidgets.QLabel('\u03b1 Tilt')
        lblBeta = QtWidgets.QLabel('\u03b2 Tilt')

        lblAlpha.setAlignment(QtCore.Qt.AlignCenter)
        lblBeta.setAlignment(QtCore.Qt.AlignCenter)
        lblIdx.setMinimumWidth(25)
        lblChecked.setMinimumWidth(25)
        lblAlpha.setMinimumWidth(50)
        lblBeta.setMinimumWidth(75)

        headerBox = QtWidgets.QHBoxLayout()
        headerBox.addWidget(lblIdx)
        headerBox.addWidget(lblChecked)
        headerBox.addWidget(lblAlpha)
        headerBox.addWidget(lblBeta)
        headerBox.addStretch(99)


        # get coordinates
        if along:
            coordinates = along_interface_tilt_coordinates(
                a0, b0, rotation, step_size)
        else:
            coordinates = normal_to_interface_tilt_coordinates(
                a0, b0, rotation, step_size
            )
        good_coordinates = []
        for x, y in coordinates:
            if abs(x) < alpha_max and abs(y) < beta_max:
                good_coordinates.append([x,y])

        # Container Widget
        widget = QtWidgets.QWidget()
        # Layout of Container Widget
        self.layout = QtWidgets.QVBoxLayout(self)

        for i, [x,y] in enumerate(good_coordinates):
            self.layout.addWidget(TiltPointWidget(i, x, y))

        widget.setLayout(self.layout)

        # Scroll Area Properties
        scroll = QtWidgets.QScrollArea()
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(False)
        scroll.setWidget(widget)

        # Scroll Area Layer add
        vLayout = QtWidgets.QVBoxLayout(self)
        vLayout.addLayout(headerBox)
        vLayout.addWidget(scroll)
        vLayout.setStretch(1,99)
        self.setLayout(vLayout)


#  NOT USED ANYMORE.  USE poleplot.py PolePlot class instead.
class TiltSeriesPlot(FigureCanvas):

    def __init__(self, parent=None, width=4, height=4, dpi=200):
        self.fig = matplotlib.figure.Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')
        self.ax.set_aspect('equal', 'box')
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.setSizePolicy(
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        self.updateGeometry()

    def plot(self, crystal, interface_alpha=None, interface_beta=None,
             interface_rotation=None, xlim=45, ylim=45):
        ax = self.ax
        ax.cla()
        self.fig.tight_layout()
        self.ax.axis('on')

        fig = self.fig
        ax.spines['left'].set_position('zero')
        ax.spines['right'].set_color('none')
        ax.spines['bottom'].set_position('zero')
        ax.spines['top'].set_color('none')
        ax.spines['left'].set_smart_bounds(True)
        ax.spines['bottom'].set_smart_bounds(True)
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        self.ax.set_xlim(-1*xlim, xlim)
        self.ax.set_ylim(-1*ylim, ylim)

        scs = []
        colors = []
        names = []

        if crystal is not None:
            beam_direction = crystal.beam_direction

            # # set reference direction
            rotation_correction = crystal.rotation_correction
            reference_direction = crystal.reference_direction

            # convert reference and beam direction to cartesian
            zero_tilt_beam_direction = native_to_cartesian(
                beam_direction,
                crystal.a, crystal.b, crystal.c,
                crystal.alpha, crystal.beta, crystal.gamma)

            reference_direction = native_to_cartesian(reference_direction,
                                                      crystal.a, crystal.b,
                                                      crystal.c,
                                                      crystal.alpha,
                                                      crystal.beta,
                                                      crystal.gamma)
            # get family of directions
            with open('data/markers.json', 'r') as fp:
                ddict = json.load(fp)
                direction_dict = ddict[ddict['Current']]

            # print(direction_dict['111'])


            for family in direction_dict:
                # get all directions for family including negatives
                directions = []
                directions.append(string_direction_to_int(family))
                for u in (-1, 1):
                    for v in (-1, 1):
                        for w in (-1, 1):
                            i, j, k = directions[0]
                            next_direction = [u * i, v * j, w * k]
                            if next_direction not in directions:
                                directions.append(next_direction)

                this_familys_coordinates = []
                for direction in directions:
                    # print('   ', direction)
                    cartesian_direction = native_to_cartesian(direction,
                                                              crystal.a, crystal.b,
                                                              crystal.c,
                                                              crystal.alpha,
                                                              crystal.beta,
                                                              crystal.gamma)
                    next_coordinates = stage_coordinates(
                        cartesian_direction, zero_tilt_beam_direction,
                        crystal.a0, crystal.b0,
                        reference_direction, rotation_correction)

                    this_familys_coordinates.append(next_coordinates)


                this_familys_x_coordinates = [i[0] for i in
                                              this_familys_coordinates]
                this_familys_y_coordinates = [i[1] for i in
                                              this_familys_coordinates]

                color = (direction_dict[family]['color'][0] / 255,
                         direction_dict[family]['color'][1] / 255,
                         direction_dict[family]['color'][2] / 255)

                scs.append(self.ax.scatter(this_familys_x_coordinates,
                                       this_familys_y_coordinates,
                                       marker=direction_dict[family]['marker'],
                                       s=direction_dict[family]['ms'],
                                       c=np.array([color])))
                colors.append(color)
                names.append([int_direction_to_bar_string(d) for d in directions])

        if interface_alpha is not None and interface_beta is not None and interface_rotation is not None:
            x_coords = []
            y_coords = []
            for x, y in along_interface_tilt_coordinates(interface_alpha,
                                                         interface_beta,
                                                         interface_rotation,
                                                         step_size=0.1):
                x_coords.append(x)
                y_coords.append(y)
            scs.append(self.ax.scatter(x_coords, y_coords, color='blue',
                                   marker='.', s=1))
            names.append('Along Interface')
            colors.append('blue')

            x_coords = []
            y_coords = []
            for x, y in normal_to_interface_tilt_coordinates(interface_alpha,
                                                             interface_beta,
                                                             interface_rotation,
                                                             step_size=0.1):
                x_coords.append(x)
                y_coords.append(y)
            scs.append(self.ax.scatter(x_coords, y_coords, color='red',
                                   marker='.', s=1))
            names.append('Across Interface')
            colors.append('red')

        annot = ax.annotate("", xy=(0, 0), xytext=(0.3,0.1),
                            textcoords="figure fraction",
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
            try:
                text = ''.join(('<', names[i][ind["ind"][0]], '>',
                                '\nX tilt = ', str(pos[0]),
                                ', Y tilt = ', str(pos[1])))
            except:
                text = ''.join((names[i],
                                '\nX tilt = ', str(pos[0]),
                                ', Y tilt = ', str(pos[1])))
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

        self.draw_idle()

class TiltSeriesCalculator(QtWidgets.QWidget):

    def __init__(self, sample=None):
        QtWidgets.QWidget.__init__(self)

        self.sample = sample

        self.lblInterfaceOnEdge = QtWidgets.QLabel('Interface on edge:')
        self.lblRotation = QtWidgets.QLabel('Rotation:')
        self.lblATilt = QtWidgets.QLabel('\u03b1:')
        self.lblBTilt = QtWidgets.QLabel('\u03b2:')
        self.lblStep = QtWidgets.QLabel('Step size:')

        self.lblRotation.setAlignment(QtCore.Qt.AlignRight)
        self.lblATilt.setAlignment(QtCore.Qt.AlignRight)
        self.lblBTilt.setAlignment(QtCore.Qt.AlignRight)

        self.txtRotation = QtWidgets.QLineEdit()
        self.txtATilt = QtWidgets.QLineEdit()
        self.txtBTilt = QtWidgets.QLineEdit()
        self.txtStep = QtWidgets.QLineEdit()

        optionBox = QtWidgets.QGroupBox()
        self.radAlong = QtWidgets.QRadioButton('Along interface')
        self.radAcross = QtWidgets.QRadioButton('Across interface')
        self.radAlong.setChecked(True)
        self.radAlong.toggled.connect(self.update)
        optionHbox = QtWidgets.QHBoxLayout()
        optionHbox.addWidget(self.radAlong)
        optionHbox.addWidget(self.radAcross)
        optionHbox.addStretch(99)
        optionBox.setLayout(optionHbox)

        self.validator = QtGui.QDoubleValidator()
        textboxes = [self.txtATilt, self.txtBTilt,
                     self.txtRotation, self.txtStep]
        for t in textboxes:
            t.setValidator(self.validator)
            t.setMaximumWidth(50)
            t.textChanged.connect(self.update)

        self.lblRotation.setMinimumWidth(65)
        self.lblStep.setMinimumWidth(65)

        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.lblInterfaceOnEdge)
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.lblATilt)
        hbox2.addWidget(self.txtATilt)
        hbox2.addWidget(self.lblBTilt)
        hbox2.addWidget(self.txtBTilt)
        #hbox2.addStretch(99)
        hbox3 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.lblRotation)
        hbox2.addWidget(self.txtRotation)
        hbox2.addStretch(99)
        hbox4 = QtWidgets.QHBoxLayout()
        hbox4.addWidget(self.lblStep)
        hbox4.addWidget(self.txtStep)
        hbox4.addStretch(99)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(hbox1)
        self.vbox.addLayout(hbox2)
        self.vbox.addLayout(hbox3)
        self.vbox.addLayout(hbox4)
        self.vbox.addWidget(optionBox)
        #self.vbox.addStretch(2)
        #self.vbox.addLayout(hbox4)

        self.points = TiltPointFrame(180,180,0,100)
        self.points.setMinimumHeight(300)
        self.vbox.addWidget(self.points)

        # plots
        self.combo1 = QtWidgets.QComboBox(self)
        self.combo2 = QtWidgets.QComboBox(self)
        self.combo1.addItem("Don't plot crystal")
        self.combo2.addItem("Don't plot crystal")
        if sample is not None:
            for crystal in self.sample.crystals:
                self.combo1.addItem(crystal.name)
                self.combo2.addItem(crystal.name)
        self.plot1 = PolePlot(self)
        self.plot2 = PolePlot(self)
        plot1vbox = QtWidgets.QVBoxLayout()
        plot2vbox = QtWidgets.QVBoxLayout()
        plot1vbox.addWidget(self.combo1)
        plot1vbox.addWidget(self.plot1)
        plot2vbox.addWidget(self.combo2)
        plot2vbox.addWidget(self.plot2)
        self.combo1.currentIndexChanged.connect(self.update)
        self.combo2.currentIndexChanged.connect(self.update)

        self.master_hbox = QtWidgets.QHBoxLayout()
        self.master_hbox.addLayout(self.vbox)
        self.master_hbox.addLayout(plot1vbox)
        self.master_hbox.addLayout(plot2vbox)
        self.setLayout(self.master_hbox)



    def update(self):
        all_good = False
        try:
            a0 = float(self.txtATilt.text())
            b0 = float(self.txtBTilt.text())
            rot = float(self.txtRotation.text())
            step = float(self.txtStep.text())
            if step != 0:
                all_good = True
        except:
            pass

        if all_good:
            # make list
            if self.points is not None:
                self.vbox.removeWidget(self.points)
                self.points.deleteLater()
                self.points = None
            along = self.radAlong.isChecked()
            self.points = TiltPointFrame(a0, b0, rot, step, along=along)
            self.points.setMinimumHeight(300)
            self.vbox.addWidget(self.points)

            # plot
            if self.combo1.currentIndex() == 0:
                c1 = None
            else:
                c1 = self.sample.crystals[self.combo1.currentIndex()-1]
            if self.combo2.currentIndex() == 0:
                c2 = None
            else:
                c2 = self.sample.crystals[self.combo2.currentIndex()-1]
            self.plot1.plot(c1, a0, b0, rot)
            self.plot2.plot(c2, a0, b0, rot)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.setCentralWidget(TiltSeriesCalculator())
    window.move(100,100)
    window.show()
    sys.exit(app.exec_())