# particles/molecule.py

import pygame
import pymunk
import random


class Molecule:
    def __init__(self, space, radius, mass, color, position=(0, 0)):
        self.radius = radius
        self.mass = mass
        self.color = color
        self.position = position

        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = position
        self.shape = pymunk.Circle(self.body, radius)
        space.add(self.body, self.shape)

    def apply_impulse(self, impulse):
        self.body.apply_impulse_at_local_point(impulse)
