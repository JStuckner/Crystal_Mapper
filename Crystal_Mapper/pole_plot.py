import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import matplotlib
matplotlib.use('QT5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import json
from crystal_math import *


class PolePlot(FigureCanvas):

    def __init__(self, parent=None, width=4, height=4, dpi=200):
        self.fig = matplotlib.figure.Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')
        self.ax.set_aspect('equal', 'box')

        # color
        self.ax.set_facecolor((0,0,0))
        self.fig.patch.set_facecolor((0,0,0))
        self.ax.spines['bottom'].set_color('w')
        self.ax.spines['top'].set_color('w')
        self.ax.spines['right'].set_color('w')
        self.ax.spines['left'].set_color('w')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')


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

        self.ax.set_xlim(-1 * xlim, xlim)
        self.ax.set_ylim(-1 * ylim, ylim)

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

        annot = ax.annotate("", xy=(0, 0), xytext=(0.3, 0.1),
                            textcoords="figure fraction",
                            bbox=dict(boxstyle="round", fc="w", color='w'),
                            arrowprops=dict(arrowstyle="->", color='w'),
                            horizontalalignment='center',
                            color='black',
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

class PolePlotOld(FigureCanvas):

    def __init__(self, parent=None, width=4, height=4, dpi=200):
        self.fig, self.ax = plt.subplots()
        plt.axis('off')
        self.ax.set_aspect('equal', 'box')

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self, crystal, direction = None, alpha_direction = None,
             plot_lines = True):
        plt.cla()
        ax = self.ax
        plt.tight_layout()
        plt.axis('on')

        fig = self.fig
        ax.spines['left'].set_position('zero')
        ax.spines['right'].set_color('none')
        ax.spines['bottom'].set_position('zero')
        ax.spines['top'].set_color('none')
        ax.spines['left'].set_smart_bounds(True)
        ax.spines['bottom'].set_smart_bounds(True)
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        if direction is None:
            beam_direction = crystal.beam_direction
        else:
            beam_direction = direction

        # # set reference direction
        # if alpha_direction is None:
        #     alpha_direction = crystal.alpha_direction
        rotation_correction = crystal.rotation_correction
        reference_direction = crystal.reference_direction

        # convert reference and beam direction to cartesian
        zero_tilt_beam_direction = native_to_cartesian(
            beam_direction,
            crystal.a, crystal.b, crystal.c,
            crystal.alpha, crystal.beta, crystal.gamma)

        reference_direction = native_to_cartesian(reference_direction,
            crystal.a, crystal.b, crystal.c,
            crystal.alpha, crystal.beta, crystal.gamma)
        # get family of directions
        with open('data/markers.json', 'r') as fp:
            ddict = json.load(fp)
            direction_dict = ddict[ddict['Current']]


        #print(direction_dict['111'])
        scs = []
        colors = []
        names = []

        for family in direction_dict:
            # get all directions for family including negatives
            #print(family)
            directions = []
            directions.append(string_direction_to_int(family))
            for u in (-1, 1):
                for v in (-1, 1):
                    for w in (-1,1):
                        i,j,k = directions[0]
                        next_direction = [u*i, v*j, w*k]
                        if next_direction not in directions:
                            directions.append(next_direction)


            this_familys_coordinates = []
            for direction in directions:
                #print('   ', direction)
                cartesian_direction = native_to_cartesian(direction,
                    crystal.a, crystal.b, crystal.c,
                    crystal.alpha, crystal.beta, crystal.gamma)
                next_coordinates = stage_coordinates(
                    cartesian_direction, zero_tilt_beam_direction,
                    crystal.a0, crystal.b0,
                    reference_direction, rotation_correction)
                # # need to get positive and negative coordinates
                # rounded = [[round(tfc[0], 2), round(tfc[1],2)] for tfc in this_familys_coordinates]
                # if [round(next_coordinates[0], 2),
                #     round(next_coordinates[1], 2)] in rounded:
                #     next_coordinates = (pole_coordinates(
                #         cartesian_direction, beam_direction,
                #         reference_direction, rotation_correction))

                # Only plot poles on top hemisphere.
                # Referencing 0-tilt direction as "north pole".
                next_angle = angle_between(cartesian_direction,
                                           zero_tilt_beam_direction)
                next_angle = np.rad2deg(next_angle)
                #print(direction)
                #if next_angle < 90:
                this_familys_coordinates.append(next_coordinates)
                #else:
                    #print(direction, next_angle)
                    #pass

            this_familys_x_coordinates = [i[0] for i in
                                          this_familys_coordinates]
            this_familys_y_coordinates = [i[1] for i in
                                          this_familys_coordinates]

            color = (direction_dict[family]['color'][0] / 255,
                     direction_dict[family]['color'][1] / 255,
                     direction_dict[family]['color'][2] / 255)

            scs.append(plt.scatter(this_familys_x_coordinates,
                                   this_familys_y_coordinates,
                                   marker=direction_dict[family]['marker'],
                                   s=direction_dict[family]['ms'],
                                   c=np.array([color])))
            colors.append(color)
            names.append([int_direction_to_bar_string(d) for d in directions])


        plt.xlim(-100, 100)
        plt.ylim(-100, 100)


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
            text = ''.join(('<', names[i][ind["ind"][0]], '>',
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

        self.draw()

    # def resizeEvent(self, event):
    #     # Create a square base size of 10x10 and scale it to the new size
    #     # maintaining aspect ratio.
    #     new_size = QtCore.QSize(10, 10)
    #     new_size.scale(event.size(), QtCore.Qt.KeepAspectRatio)
    #     self.resize(new_size)
