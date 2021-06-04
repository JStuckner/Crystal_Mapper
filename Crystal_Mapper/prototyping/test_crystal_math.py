import unittest
import numpy as np

from crystal_math import *
"""Unit Test for crystal_math"""

class Test_Stage_Coordinates(unittest.TestCase):
    knownValues = ( ([1, 0, 0], [1, 0, 0], 0, 0, [0, 1, 0], 0, 0, 0),
                    ([0, 1, 0], [1, 0, 0], 0, 0, [0, 1, 0], 0, 90, 0),
                    ([0, 0, 1], [1, 0, 0], 0, 0, [0, 1, 0], 0, 0, 90),
                    ([1, 1, 0], [0, 0, 1], 0, 0, [0, 1, 0], 0, 45, -90),
                    ([1, -1, 0], [0, 0, 1], 0, 0, [0, 1, 0], 0, -45, -90),
                    ([-1, 1, 0], [0, 0, 1], 0, 0, [0, 1, 0], 0, 45, 90),
                    ([-1, -1, 0], [0, 0, 1], 0, 0, [0, 1, 0], 0, -45, 90),
                    ([0, 1, 1], [0, 0, 1], 0, 0, [0, 1, 0], 0, 45, 0),
                    ([0, -1, 1], [0, 0, 1], 0, 0, [0, 1, 0], 0, -45, 0),
                    ([1, 0, 1], [0, 0, 1], 0, 0, [0, 1, 0], 0, 0, -45),
                    ([-1, 0, 1], [0, 0, 1], 0, 0, [0, 1, 0], 0, 0, 45),
                    ([0, 1, -1], [0, 0, 1], 0, 0, [0, 1, 0], 0, 135, 0),
                    ([0, -1, -1], [0, 0, 1], 0, 0, [0, 1, 0], 0, -135, 0),
                    ([1, 0, -1], [0, 0, 1], 0, 0, [0, 1, 0], 0, 0, -135),
                    ([-1, 0, -1], [0, 0, 1], 0, 0, [0, 1, 0], 0, 0, 135),
                    ([0,0,1], [1,0,0], 0, 0, [0,0,1], 0, 90, 0),
                    ([0, 0, 1], [1, 0, 0], 0, 0, [1, 0, 1], 0, 90, 0),
                    ([0, 1, 0], [1, 1, 1], 0, 0, [0, 1, 0], 0, 54.74, 0),
                    ([0, 0, 1], [0, 0, 1], 0, 0, [0, 1, 0], 0, 0, 0),
                    ([0, 0, 1], [0, 0, -1], 0, 0, [0, 1, 0], 0, 0, 180),
                    ([0, 0, 1], [0, 0, 1], 10, 10, [0, 1, 0], 0, 10, 10),
                    ([0, 0, 1], [0, 0, 1], -10, 10, [0, 1, 0], 0, -10, 10),
                    ([0, 0, 1], [0, 0, 1], -10, -10, [1, 0, 1], 0, -10, -10),
                    ([0, 0, 1], [0, 0, 1], 10, -10, [1, 0, 1], 0, 10, -10),
                    ([0, 1, 0], [1, 1, 1], 0, 0, [0, 1, 0], 0, 54.74, 0),
                    ([1, 0, 0], [1, 1, 1], 0, 0, [0, 1, 0], 0, -24.09, -50.77),
                    ([0, 0, 1], [1, 1, 1], 0, 0, [0, 1, 0], 0, -24.09, 50.77),
                    ([0, 1, 0], [1, 1, 1], 10, 10, [0, 1, 0], 0, 64.73, 10)
                    )

    def testToKnownValues(self):
        for (direction, zone_axis, a0, b0, reference_pole, rotation,
             alpha, beta) in self.knownValues:
            result = stage_coordinates(direction, zone_axis, a0, b0,
                                       reference_pole, rotation)
            self.assertEqual((alpha,beta), result)

class Test_Zero_Tilt_Direction(unittest.TestCase):
    knownValues = ( ([0, 0, 1], 0, 0, [0, 1, 0], 0, [0,0,1], [0,1,0]),
                    ([1, 0, 0], 0, 0, [0, -1, 0], 0, [1, 0, 0], [0, -1, 0]),
                    ([1, 0, 0], 0, 0, [0, 0, 1], 0, [1, 0, 0], [0, 0, 1]),
                    ([1, 0, 0], 0, 0, [0, 0, -1], 0, [1, 0, 0], [0, 0, -1]),
                    ([1, 1, 1], 0, 0, [-1, 1, 0], 0, [1,1,1], [-1,1,0]),
                    ([1, 1, 1], 0, 0, [-1, -1, 2], 0, [1, 1, 1], [-1, -1, 2]),
                    ([1, 1, 1], 0, 0, [0, 1, 0], 0, [1,1,1], [0,1,1]),
                    ([-1, 1, 1], 0, 0, [0, 0, 1], 0, [-1, 1, 1], [0, 1, 1]),
                    ([1, 1, 1], 10, 17, [0, 1, 0], 0, [2, 1, 1], [0, 1, 1]),
                    ([-1, 1, 1], 10, 17, [0, 1, 0], 0, [-1, 1, 2], [0, 1, 1])
                    )

    def testToZeroTiltDirection(self):
        for (zone_axis, a0, b0, reference,
             rotation, normal_dir, alpha_dir) in self.knownValues:
            result = zero_tilt_direction(zone_axis, a0, b0, reference,
                                         rotation)
            np.testing.assert_almost_equal(result[0], normal_dir, 1)

    def testToAlphaTiltDirection(self):
        for (zone_axis, a0, b0, reference,
             rotation, normal_dir, alpha_dir) in self.knownValues:
            result = zero_tilt_direction(zone_axis, a0, b0, reference,
                                         rotation)
            np.testing.assert_almost_equal(result[1], alpha_dir, 1)

if __name__ == "__main__":
    unittest.main()