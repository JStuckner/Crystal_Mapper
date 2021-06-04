import math
import numpy as np
import matplotlib.pyplot as plt


def misorientation_matrix(crystal_A, crystal_B):
    matrix = np.zeros((3,3))
    directions = [[1,0,0], [0,1,0], [0,0,1]]
    for i in range(3):
        for j in range(3):
            alpha_A, beta_A = stage_coordinates(directions[i],
                                                crystal_A.beam_direction,
                                                crystal_A.a0, crystal_A.b0,
                                                crystal_A.reference_direction,
                                                crystal_A.rotation_correction)
            alpha_A = np.round(np.deg2rad(alpha_A),2)
            beta_A = np.round(np.deg2rad(beta_A),2)
            alpha_B, beta_B = stage_coordinates(directions[j],
                                                crystal_B.beam_direction,
                                                crystal_B.a0, crystal_B.b0,
                                                crystal_B.reference_direction,
                                                crystal_B.rotation_correction)
            alpha_B = np.round(np.deg2rad(alpha_B),2)
            beta_B = np.round(np.deg2rad(beta_B),2)
            matrix[i,j] = np.round((np.sin(alpha_A)*np.sin(alpha_B) +
                np.cos(alpha_A)*np.cos(alpha_B)*np.cos(beta_A-beta_B)),2)

    angle = np.rad2deg(np.arccos((matrix[0,0] + matrix[1,1] + matrix[2,2] - 1)*0.5))
    axis = [matrix[1,2] - matrix[2,1],
            matrix[2,0] - matrix[0,2],
            matrix[0, 1] - matrix[1, 0]]
    print(angle)
    print(axis)
    return matrix



def along_interface_tilt_coordinates(
        alpha, beta, rotation=0, step_size=0.1):
    """
    Give tilt coordinates to tilt in the normal direction across an interface
    that is on edge ata certain alpha and beta tilt.
    :param alpha: alpha (x) tilt amount where interface is on edge. (degrees)
    :param beta: beta (y) tilt amount where interface is on edge. (degrees)
    :param rotation: angle between alpha tilt axis and interface edge. (deg)
    :param step_size: absolute angle in degrees between returned coordinates.
    :return: list of [x,y] coordinates to tilt along interface. (degrees)
    """

    out = [] # coordinate list
    sin_alpha = np.sin(np.deg2rad(alpha))  # radians
    cos_alpha = np.cos(np.deg2rad(alpha))  # radians
    cos_phi = np.cos(np.deg2rad(rotation))  # radians, rotation
    sin_phi = np.sin(np.deg2rad(rotation))  # radians, rotation

    for theta in np.arange(-90, 90, step_size):
        sin_theta = np.sin(np.deg2rad(theta))  # radians
        cos_theta = np.cos(np.deg2rad(theta))  # radians
        tan_theta = np.tan(np.deg2rad(theta))  # radians
        x = np.round(np.rad2deg(np.arcsin(
            sin_theta * cos_phi * cos_alpha + sin_alpha * cos_theta)),2)
        y = np.round(np.rad2deg(np.arctan(
            (tan_theta * sin_phi) /
            (cos_alpha - sin_alpha * tan_theta * cos_phi))) + beta, 2)
        out.append([x,y])

    return out


def normal_to_interface_tilt_coordinates(
        alpha, beta, rotation=0, step_size=0.1):
    """
    Give tilt coordinates to tilt along an interface that is on edge at
    a certain alpha and beta tilt.
    :param alpha: alpha (x) tilt amount where interface is on edge. (degrees)
    :param beta: beta (y) tilt amount where interface is on edge. (degrees)
    :param rotation: angle between alpha tilt axis and interface edge. (deg)
    :param step_size: absolute angle in degrees between returned coordinates.
    :return: list of [x,y] coordinates to tilt along interface. (degrees)
    """

    out = [] # coordinate list
    sin_alpha = np.sin(np.deg2rad(alpha))  # radians
    cos_alpha = np.cos(np.deg2rad(alpha))  # radians
    cos_phi_90 = np.cos(np.deg2rad(rotation + 90))  # radians, rotation
    sin_phi_90 = np.sin(np.deg2rad(rotation + 90))  # radians, rotation

    for theta in np.arange(-90, 90, step_size):
        sin_theta = np.sin(np.deg2rad(theta))  # radians
        cos_theta = np.cos(np.deg2rad(theta))  # radians
        tan_theta = np.tan(np.deg2rad(theta))  # radians
        x = np.round(np.rad2deg(np.arcsin(
            sin_theta * cos_phi_90 * cos_alpha + sin_alpha * cos_theta)),2)
        y = np.round(np.rad2deg(np.arctan(
            (tan_theta * sin_phi_90) /
            (cos_alpha - sin_alpha * tan_theta * cos_phi_90))) + beta, 2)
        out.append([x,y])

    return out

def get_band_coordinates(xtilt, ytilt, rotation, step_size=0.1):
    x = []
    y = []
    sin_alpha = np.sin(np.deg2rad(xtilt))
    cos_alpha = np.cos(np.deg2rad(xtilt))
    sin_beta = np.sin(np.deg2rad(ytilt))
    cos_beta = np.cos(np.deg2rad(ytilt))
    cos_rotation = np.cos(np.deg2rad(rotation))
    sin_rotation = np.sin(np.deg2rad(rotation))

    for i in np.arange(-90,90,step_size):
        sin_i = np.sin(np.deg2rad(i))
        cos_i = np.cos(np.deg2rad(i))
        tan_i = np.tan(np.deg2rad(i))
        next_x = np.rad2deg(
            np.arcsin(sin_i*cos_rotation*cos_alpha + sin_alpha * cos_i))
        next_y = (np.rad2deg(
            np.arctan(tan_i*sin_rotation/cos_alpha - sin_alpha*tan_i*cos_rotation))
            + ytilt)
        if np.sqrt(next_x**2 + next_y**2) <= 45:
            x.append(next_x)
            y.append(next_y)
    return x,y

# region pole plot
def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in degrees between vectors 'v1' and 'v2'. """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def old_stage_coordinates(direction, zone_axis, za_alpha_tilt, za_beta_tilt,
                      reference_pole, rotation):
    """
    :param direction: direction for which tilt coordinates are returned.
    :param zone_axis: a known zone axis with known tilt coordinates
    :param za_alpha_tilt: alpha tilt of zone_axis
    :param za_beta_tilt: beta tilt of zone_axis
    :param reference_pole: pole for which the rotation angle is known.
    :param rotation: angle about the zone_axis between the projected reference
                     pole and the alpha stage pole.
    :return: alpha, beta = the tilt angles to align beam to direction
    """

    gamma = angle_between(direction, zone_axis)

    reference_pole_projected = unit_vector(np.cross(reference_pole, zone_axis))
    direction_projected = unit_vector(np.cross(direction, zone_axis))


    # if (direction_projected[0] ==  0 and direction_projected[1] == 0 and
    #         direction_projected[2] == 0):
    #     direction_projected = zone_axis

    #print(reference_pole_projected)
    #print(direction_projected)

    phi = (angle_between(
        reference_pole_projected, direction_projected) +
         np.deg2rad(rotation))

    #phi = 0 if math.isnan(phi) else phi


    # If the dot product is negative then the angle between the reference
    # and direction is negative.
    dot = np.dot(np.cross(reference_pole_projected, direction_projected),
                 np.array(zone_axis))
    if dot < -0.001:
        phi = (-1 * angle_between(
               reference_pole_projected, direction_projected) +
               np.deg2rad(rotation))
    else:
        phi = (angle_between(
               reference_pole_projected, direction_projected) +
               np.deg2rad(rotation))

    #print(np.rad2deg(phi), np.rad2deg(gamma))

    #print(gamma, phi)
    sin_gamma = round(np.sin(gamma), 3)
    cos_gamma = round(np.cos(gamma), 3)
    tan_gamma = round(np.tan(gamma), 3)
    cos_alpha0 = round(np.cos(np.deg2rad(za_alpha_tilt)),3)
    sin_alpha0 = round(np.sin(np.deg2rad(za_alpha_tilt)),3)
    cos_beta0 = round(np.cos(np.deg2rad(za_beta_tilt)),3)
    sin_beta0 = round(np.sin(np.deg2rad(za_beta_tilt)),3)
    sin_phi = round(np.sin(phi),3)
    cos_phi = round(np.cos(phi),3)

    #print(sin_gamma, cos_gamma, tan_gamma, cos_alpha0, sin_alpha0,sin_phi, cos_phi)
    #print('gamma', np.rad2deg(gamma), sin_gamma)
    #print('no calcs', sin_gamma, cos_phi, cos_alpha0)
    #print('calcs   ',sin_gamma*cos_phi*cos_alpha0, sin_alpha0*cos_gamma)
    alpha = np.rad2deg(
        np.arcsin(sin_gamma*cos_phi*cos_alpha0 + sin_alpha0*cos_gamma)
    )
    if np.rad2deg(gamma) > 90 and np.rad2deg(gamma) < 270:
        alpha = -1 * alpha
    beta = np.rad2deg(
        np.arctan((tan_gamma*sin_phi)/
                  (cos_alpha0 - sin_alpha0*tan_gamma*cos_phi))
        ) + za_beta_tilt
    alpha = np.round(alpha,1)
    beta = np.round(beta,1)

    alpha = 0 if math.isnan(alpha) else alpha
    beta = 0 if math.isnan(beta) else beta

    print(alpha, beta)
    return alpha, beta


def stage_coordinates(direction, zone_axis, a0, b0, reference_pole, rotation):
    # Returns alpha and beta tilt directions (in degrees) for specified
    # direction and crystal orientation.
    gamma = angle_between(direction, zone_axis)

    direction_projected = unit_vector(np.cross(direction, zone_axis))
    reference_projected = unit_vector(np.cross(reference_pole, zone_axis))

    ortho_to_ref = np.cross(zone_axis, reference_projected)
    dot = np.dot(ortho_to_ref, direction_projected)

    if dot < 0:
        phi = np.deg2rad(360) - angle_between(direction_projected,
                                              reference_projected)
    else:
        phi = angle_between(direction_projected, reference_projected)

    phi = phi + np.deg2rad(rotation)

    if math.isnan(phi):
        phi = 0

    sin_gamma = np.round(np.sin(gamma),4)
    cos_gamma = np.round(np.cos(gamma),4)
    tan_gamma = np.round(np.tan(gamma),4)
    sin_phi = np.round(np.sin(phi),4)
    cos_phi = np.round(np.cos(phi),4)
    tan_phi = np.round(np.tan(phi),4)
    sin_a0 = np.round(np.sin(np.deg2rad(a0)),4)
    cos_a0 = np.round(np.cos(np.deg2rad(a0)),4)
    tan_a0 = np.round(np.tan(np.deg2rad(a0)),4)

    #print(zone_axis, direction, np.rad2deg(gamma), sin_gamma)

    alpha = np.arcsin((sin_gamma * cos_phi * cos_a0 + sin_a0 * cos_gamma))
    beta = np.arctan((tan_gamma * sin_phi) / (
                cos_a0 - sin_a0 * tan_gamma * cos_phi)) + np.deg2rad(b0)

    #print(alpha, gamma)

    if np.rad2deg(gamma) > 90:
        alpha = np.round(np.deg2rad(180),4) - alpha

    if np.rad2deg(alpha) > 180.5:
        alpha = alpha - np.round(np.deg2rad(360), 4)

    if np.abs(np.rad2deg(alpha) - 180) < 0.5:
        alpha = 0
        beta = -1 * np.round(np.deg2rad(180),4) + beta

    if np.rad2deg(beta) < -180:
        beta = beta + np.round(np.deg2rad(360),4)

    #print(direction, zone_axis, np.rad2deg(gamma),
    #      np.rad2deg(alpha), np.rad2deg(beta))

    alpha = np.round(np.rad2deg(alpha), 2)
    beta = np.round(np.rad2deg(beta), 2)

    try:
        if direction[0] == 1 and direction[1] == 1 and direction[2] == 1:
            print(direction, alpha, beta)
    except:
        print('what is wrong?')

    return alpha, beta

def zero_tilt_direction(zone_axis, za_alpha_tilt, za_beta_tilt,
                        reference_pole, rotation):
    a0, b0 = stage_coordinates([1, 0, 0], zone_axis, za_alpha_tilt,
                               za_beta_tilt, reference_pole, rotation)
    a1, b1 = stage_coordinates([0, 1, 0], zone_axis, za_alpha_tilt,
                               za_beta_tilt, reference_pole, rotation)
    a2, b2 = stage_coordinates([0, 0, 1], zone_axis, za_alpha_tilt,
                               za_beta_tilt, reference_pole, rotation)

    #print(a0, b0, a1, b1, a2, b2)
    direction = [np.cos(np.deg2rad(a0)) * np.cos(np.deg2rad(b0)),
                 np.cos(np.deg2rad(a1)) * np.cos(np.deg2rad(b1)),
                 np.cos(np.deg2rad(a2)) * np.cos(np.deg2rad(b2))]

    alpha_tilt_direction = [-1*np.cos(np.deg2rad(a0)) * np.sin(np.deg2rad(b0)),
                            -1*np.cos(np.deg2rad(a1)) * np.sin(np.deg2rad(b1)),
                            -1*np.cos(np.deg2rad(a2)) * np.sin(np.deg2rad(b2))]

    direction = [round(i, 2) for i in direction]
    dmin = min(np.abs(x) for x in direction if np.abs(x) > 0.1)
    direction = [direction[0] / dmin, direction[1] / dmin, direction[2] / dmin]


    # alpha_tilt_direction = [round(i, 2) for i in alpha_tilt_direction]
    # dmin = min(np.abs(x) for x in alpha_tilt_direction if np.abs(x) > 0.1)
    # alpha_tilt_direction = [alpha_tilt_direction[0] / dmin,
    #                         alpha_tilt_direction[1] / dmin,
    #                         alpha_tilt_direction[2] / dmin]
    #
    # print(direction_given_tilt(0,-90,zone_axis,za_alpha_tilt,za_beta_tilt,
    #       reference_pole, rotation))
    # print(direction_given_tilt(0, 270, zone_axis, za_alpha_tilt, za_beta_tilt,
    #                            reference_pole, rotation))
    #
    # print(direction, alpha_tilt_direction, a0,b0,a1,b1,a2,b2)
    return direction

def direction_given_tilt(alpha, beta, zone_axis, za_alpha_tilt, za_beta_tilt,
                         reference_pole, rotation):
    a0, b0 = stage_coordinates([1, 0, 0], zone_axis, za_alpha_tilt,
                               za_beta_tilt, reference_pole, rotation)
    a1, b1 = stage_coordinates([0, 1, 0], zone_axis, za_alpha_tilt,
                               za_beta_tilt, reference_pole, rotation)
    a2, b2 = stage_coordinates([0, 0, 1], zone_axis, za_alpha_tilt,
                               za_beta_tilt, reference_pole, rotation)

    u = (np.sin(np.deg2rad(a0))*np.sin(np.deg2rad(alpha)) +
         np.cos(np.deg2rad(a0))*np.cos(np.deg2rad(alpha))*
         np.cos(np.deg2rad(beta)-np.deg2rad(b0)))
    v = (np.sin(np.deg2rad(a1)) * np.sin(np.deg2rad(alpha)) +
         np.cos(np.deg2rad(a1)) * np.cos(np.deg2rad(alpha)) *
         np.cos(np.deg2rad(beta) - np.deg2rad(b1)))
    w = (np.sin(np.deg2rad(a2)) * np.sin(np.deg2rad(alpha)) +
         np.cos(np.deg2rad(a2)) * np.cos(np.deg2rad(alpha)) *
         np.cos(np.deg2rad(beta) - np.deg2rad(b2)))

    return([u,v,w])




def _test_pole_plotting(zero_tilt_beam_direction = [1,1,0],
                        rotation_correction = 0):
    from equivalent_planes import cubic_family_of_directions

    fig, ax = plt.subplots()
    ax.spines['left'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_color('none')
    ax.spines['left'].set_smart_bounds(True)
    ax.spines['bottom'].set_smart_bounds(True)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # set reference direction
    reference_direction = [1, 0, 0]
    if zero_tilt_beam_direction == [1, 0, 0]:
        reference_direction = [0, 1, 0]

    # convert reference and beam direction to cartesian
    zero_tilt_beam_direction = native_to_cartesian(zero_tilt_beam_direction,
                                                   1,1,1,90,90,90)
    reference_direction = native_to_cartesian(reference_direction,
                                              1,1,1,90,90,90)

    # get family of directions
    directions = cubic_family_of_directions()
    scs = []
    colors = []
    for family in directions:

        #print(family)
        this_familys_coordinates = []
        for direction in directions[family]:
            #print('   ', direction)
            cartesian_direction = native_to_cartesian(direction,
                                                      1,1,1,90,90,90)
            next_coordinates = (stage_coordinates(
                cartesian_direction, zero_tilt_beam_direction,0,0,
                reference_direction, rotation_correction))
            # next_coordinates = (pole_coordinates(
            #     cartesian_direction, zero_tilt_beam_direction,
            #     reference_direction, rotation_correction))
            # need to get positive and negative coordinates
            if next_coordinates in this_familys_coordinates:
                this_familys_coordinates.append((-1*next_coordinates[0],
                                                 -1*next_coordinates[1]))
            else:
                this_familys_coordinates.append(next_coordinates)

        #for i in this_familys_coordinates:
            #print(i[0])
        this_familys_x_coordinates = [i[0] for i in this_familys_coordinates]
        this_familys_y_coordinates = [i[1] for i in this_familys_coordinates]


        if family == '111':
            scs.append(plt.scatter(this_familys_x_coordinates,
                        this_familys_y_coordinates, marker='^', s=50, color='blue'))
            colors.append('blue')

        elif family == '110':
            scs.append(plt.scatter(this_familys_x_coordinates,
                        this_familys_y_coordinates, marker='D', s=50, color='red'))
            colors.append('red')
        elif family == '100':
            scs.append(ax.scatter(this_familys_x_coordinates,
                        this_familys_y_coordinates, marker='s', s=50, color='black'))
            colors.append('black')


    plt.xlim(-180,180)
    plt.ylim(-180, 180)

    annot = ax.annotate("", xy=(0, 0), xytext=(10, 30),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"),
                        horizontalalignment='center',
                        color='white',
                        fontsize=12,
                        fontweight='bold')
    annot.set_visible(False)

    def update_annot(sc, ind, color):

        pos = sc.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        text = ''.join(('X tilt = ', str(pos[0]), ', Y tilt = ', str(pos[1])))
        annot.set_text(text)
        annot.get_bbox_patch().set_facecolor(color)
        annot.get_bbox_patch().set_alpha(0.7)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            for i, sc in enumerate(scs):
                cont, ind = sc.contains(event)
                if cont:
                    update_annot(sc, ind, colors[i])
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                    break
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.show()

# endregion


def string_direction_to_int(direction):
    out = []
    for i in range(len(direction)):
        if direction[i] == '-':
            i = i + 1
            out.append(-1*int(direction[i]))
        else:
            out.append(-1 * int(direction[i]))
    return out


def int_direction_to_bar_string(direction):
    u = direction[0]
    u = str(u) if u >= 0 else ''.join((str(-u),'\u0305'))
    v = direction[1]
    v = str(v) if v >= 0 else ''.join((str(-v), '\u0305'))
    w = direction[2]
    w = str(w) if w >= 0 else ''.join((str(-w), '\u0305'))
    return ''.join((u,v,w))


def get_V(a,b,c,alpha,beta,gamma):
    # volume
    cos_alpha = np.cos(np.radians(alpha))
    cos_beta = np.cos(np.radians(beta))
    cos_gamma = np.cos(np.radians(gamma))
    return (a * b * c *
            np.sqrt(1 - cos_alpha**2 - cos_beta**2 - cos_gamma**2 +
                    2 * cos_alpha * cos_beta * cos_gamma))


def get_M(a,b,c,alpha,beta,gamma):
    # Choice of M
    # http://www.mse.mtu.edu/~drjohn/my3200/stereo/sg4.html
    # http://www.ruppweb.org/Xray/tutorial/Coordinate%20system%20transformation.htm
    # M is the deorthogonalization matrix
    # inverse M = orthogonalization matrix
    sin_alpha = np.sin(np.radians(alpha))
    cos_alpha = np.cos(np.radians(alpha))
    sin_beta = np.sin(np.radians(beta))
    cos_beta = np.cos(np.radians(beta))
    sin_gamma = np.sin(np.radians(gamma))
    cos_gamma = np.cos(np.radians(gamma))
    cos_delta = (cos_gamma - cos_alpha * cos_beta) / (sin_alpha * sin_beta)
    sin_delta = np.sqrt(1-cos_delta**2)
    #print(sin_alpha, cos_alpha, sin_beta, cos_beta, sin_gamma, cos_gamma,
    #      sin_delta, cos_delta, sep='\n')

    M = np.zeros((3,3))
    # Ruppweb version (this is actually inverse m)
    M[0, 0] = a * sin_beta
    M[0, 1] = b * sin_alpha * cos_delta
    M[1, 1] = b * sin_alpha * sin_delta
    M[2, 0] = a * cos_beta
    M[2, 1] = b * cos_alpha
    M[2, 2] = c

    #print(M)
    # Dr. John Version
    # M[0, 0] = a * sin_beta
    # M[0, 1] = b * sin_alpha * cos_delta
    # M[1, 1] = b * sin_alpha * sin_delta
    # M[2, 0] = a * cos_beta
    # M[2, 1] = b * cos_alpha
    # M[2, 2] = c
    return M


def get_inv_M(a,b,c,alpha,beta,gamma):
    return np.linalg.inv(get_M(a,b,c,alpha,beta,gamma))


def native_to_cartesian(direction,a,b,c,alpha,beta,gamma):
    return np.matmul(get_M(a,b,c,alpha,beta,gamma), direction)


def cartesian_to_native(direction,a,b,c,alpha,beta,gamma):
    return np.matmul(get_inv_M(a, b, c, alpha, beta, gamma), direction)





class Crystal:
    """Contains all attributes to describe a crystal and it's orientation.

    """
    def __init__(self, name, system, a, b, c, alpha, beta, gamma,
                 beam_direction = [1, 1, 1], rotation_correction = 0,
                 reference_direction = [0,0,1], alpha_direction = [0,0,1],
                 a0 = 0, b0 = 0):
        self.name = name
        self.system = system
        self.a = a
        self.b = b
        self.c = c
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.beam_direction = beam_direction
        self.rotation_correction = rotation_correction
        self.knownPoles = []
        self.alpha_direction = alpha_direction
        self.reference_direction = reference_direction

        self.known_pole = beam_direction
        self.a0 = a0 #alpha tilt for known pole
        self.b0 = b0 #beta tilt for known pole

    def add_known_pole(self, u,v,w, x_tilt, y_tilt):
        self.knownPoles.append([u,v,w,x_tilt,y_tilt])

    def add_rotation_angle(self, pole1, pole2, angle_relative_to_x_tilt):
        pass

    def set_orientation(self):
        pass

class Sample:
    crystals = []
    rotation = 0
    flipped = False

    def __init__(self, json=None):
        if json is not None:
            self.load(json)
    def load(self):
        pass



def test_stage_coodinates():
    pass

def _test_matrix_rotation():
    c1 = Crystal('C1', 'cubic', 1, 1, 1, 90, 90, 90,
                 [1, 0, 1], 79, [0, 1, 0],
                [0, 1, 0], 6.3, -20.1)
    c2 = Crystal('C2', 'cubic', 1, 1, 1, 90, 90, 90,
                 [1, 0, 1], -32.4, [0, 1, 0],
                 [0, 1, 0], 6.3, -20.1)

    print(misorientation_matrix(c1,c2))

if __name__ == '__main__':
    #print(native_to_cartesian((1,1,1), 5.22, 5.27, 5.38, 90,99.46,90))
    #print(native_to_cartesian((1, 1, 1), 3.64, 3.64, 5.27, 90, 90, 90))
    #print(native_to_cartesian((1, 1, 1), 3.64, 3.64, 3.64, 90, 90, 90))
    #print(angle_between((1,0,0), (1,1,0)))
    #x,y = get_band_coordinates(5,5,5,5)
    #print(angle_between([1,0,0],[1,1,1]))
    #_test_pole_plotting()
    #for a, b in zip(x,y):
        #print(a,b)
    #get_beam_direction([1,1,1,20,20], [0,1,0], 0)
    #get_beam_direction([1, 1, 2, 19.0, 0], [0, 1, 0], 0)
    #print(zero_tilt_direction([1,1,1],0,0,[0,0,1],0))
    #print(np.rad2deg(angle_between([1,1,1],[-1,1,0])))
    #c = Crystal('hi','cubic',1,1,1,90,90,90,[1,1,1],0,[0,1,0],[0,1,0],10,10)
    #print(stage_coordinates([1,0,0],[1,1,1],0,0,[0,0,1],0))
    #print(stage_coordinates([1,1,1],c.beam_direction,c.a0, c.b0,
    #                        c.reference_direction,c.rotation_correction))
    _test_matrix_rotation()
