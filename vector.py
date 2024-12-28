from math_functions import *


class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.values = [x, y, z]

    @property
    def x(self):
        return self.values[0]

    @property
    def y(self):
        return self.values[1]

    @property
    def z(self):
        return self.values[2]

    @x.setter
    def x(self, value):
        self.values[0] = value

    @y.setter
    def y(self, value):
        self.values[1] = value

    @z.setter
    def z(self, value):
        self.values[2] = value

    def __getitem__(self, index):
        return self.values[index]

    def __setitem__(self, index, value):
        self.values[index] = value

    def __add__(self, other):
        return Vector3(
            self.values[0] + other.values[0],
            self.values[1] + other.values[1],
            self.values[2] + other.values[2],
        )

    def __sub__(self, other):
        return Vector3(
            self.values[0] - other.values[0],
            self.values[1] - other.values[1],
            self.values[2] - other.values[2],
        )

    def __mul__(self, scalar):
        return Vector3(
            self.values[0] * scalar, self.values[1] * scalar, self.values[2] * scalar
        )

    def __rmul__(self, scalar):
        return Vector3(
            self.values[0] * scalar, self.values[1] * scalar, self.values[2] * scalar
        )

    def __truediv__(self, scalar):
        return Vector3(
            self.values[0] / scalar, self.values[1] / scalar, self.values[2] / scalar
        )

    def __repr__(self):
        return f"[{self.values[0]}, {self.values[1]}, {self.values[2]}]"
