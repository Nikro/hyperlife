# particles/molecule.py
import uuid

import pygame
import pymunk
import random


class Molecule:
    def __init__(self, space, radius, mass, color=None, position=(0, 0)):
        self.id = uuid.uuid4()

        self.radius = radius
        self.mass = mass
        self.space = space
        self.density = self.calculate_density()
        self.color = color if color is not None else self.adjust_color_based_on_density()
        self.position = position

        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = position
        self.body.molecule = self
        self.body.mass = mass

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = 0.001
        self.shape.elasticity = 0.9

        space.add(self.body, self.shape)
        self.to_merge = set()

    def apply_impulse(self, impulse):
        self.body.apply_impulse_at_local_point(impulse)

    def update_physics(self, dt):
        pass
        # if self.body.is_sleeping:
        #     print("Sleeping")
        #     nearby_molecules = self.get_nearby_molecules(250)
        #     similar_molecules = [m for m in nearby_molecules if self.is_similar(m)]
        #     print(len(similar_molecules))
        #     for m in similar_molecules:
        #         if m is not self:
        #             self.to_merge.add((self, m))  # Store the pair of molecules as a tuple

    def calculate_density(self):
        # Simplified density calculation
        density = self.mass / self.radius
        return density

    def adjust_color_based_on_density(self):
        density = self.density
        max_density = 5.0
        density_ratio = min(density / max_density, 1)  # Cap the density ratio at 1.

        # Interpolate between the start and end values for each color channel.
        red_channel = int(50 + density_ratio * (255 - 50))
        green_channel = int(50 + density_ratio * (255 - 50))
        blue_channel = int(50 + density_ratio * (255 - 50))

        return red_channel, green_channel, blue_channel

    def get_nearby_molecules(self, max_distance):
        # max_distance should be set to the maximum distance at which you consider molecules to be "nearby"
        # This function will return a list of molecules that are within max_distance of this molecule
        nearby_molecules = []

        # We'll use the space's point_query_nearest method to find nearby molecules
        for shape_info in self.space.point_query(self.body.position, max_distance, pymunk.ShapeFilter()):
            if hasattr(shape_info.shape.body, 'molecule'):
                nearby_molecule = shape_info.shape.body.molecule
                nearby_molecules.append(nearby_molecule)

        return nearby_molecules
