import random

import pygame
import pymunk
from pymunk import ShapeFilter

from GUI.gui import Panel
from particles.molecule import Molecule


class GameScene:
    def __init__(self):
        self.view_port = None
        self.move_down = None
        self.move_up = None
        self.move_right = None
        self.move_left = None
        self.fps = None
        self.game_speed = 1
        self.screen = pygame.display.set_mode((1200, 800))
        self.world_width = 3000
        self.world_height = 3000

        self.molecule_layer = pygame.Surface((self.world_width, self.world_height), pygame.SRCALPHA)
        self.space = pymunk.Space()

        # Load the texture and icons and what not.
        self.icon = pygame.image.load('assets/images/icon.png')

        # Draw the texture onto the world
        self.camera_x, self.camera_y = 0, 0

        # Create a panel
        self.panel = Panel(self.screen.get_width(), self.screen.get_height(), self)

        # Add world and walls
        self.world = pygame.Surface((self.world_width + self.panel.width, self.world_height))
        self.walls = self.add_walls()

        # Init molecules.
        self.molecules = []
        self.init_molecules()

        # Set the window icon
        pygame.display.set_icon(self.icon)
        # Set the window caption
        pygame.display.set_caption("HyperLife 1.0 - Sandbox")

    def handle_input(self):
        # handle user input here
        # handle user input here
        keys = pygame.key.get_pressed()
        self.move_left = keys[pygame.K_LEFT]
        self.move_right = keys[pygame.K_RIGHT]
        self.move_up = keys[pygame.K_UP]
        self.move_down = keys[pygame.K_DOWN]

        # Handle panel inputs
        for event in pygame.event.get():
            self.panel.process_events(event)

    def init_molecules(self):
        padding = 100  # Padding from walls
        radius = 2  # Radius of molecule
        gap = 10  # Gap between molecules
        distance = 2 * radius + gap  # Distance between each molecule's center

        horizontal_molecule_count = (self.world_height - 2 * padding) // distance
        vertical_molecule_count = (self.world_width - 2 * padding) // distance

        for i in range(horizontal_molecule_count):
            for j in range(vertical_molecule_count):
                # Calculate the position of this molecule, add padding and half of the distance
                # to place the molecule in the center of each cell and maintain padding from walls
                position = (padding + distance * i + distance // 2, padding + distance * j + distance // 2)

                # Create the molecule
                mass = random.randint(1, 10)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                molecule = Molecule(self.space, radius, mass, color, position)

                # Apply a random impulse
                impulse = pymunk.Vec2d(random.uniform(-100, 100), random.uniform(-100, 100))
                molecule.apply_impulse(impulse)

                self.molecules.append(molecule)

    def update(self, dt):
        self.update_camera(dt)
        self.update_rest(dt)

    def update_physics(self, dt):
        for _ in range(int(self.game_speed)):
            self.space.step(dt)

    def update_slow(self):
        self.panel.set_molecules_count(len(self.molecules))

    def update_rest(self, dt):
        if self.fps < 10:
            # Decrease, but don't go below 1.
            self.game_speed = max(1, self.game_speed - 1)
            self.panel.speed_slider.set_current_value(int(self.game_speed))

        self.panel.set_fps(int(self.fps))
        self.panel.set_game_speed(int(self.game_speed))
        self.panel.update(dt)

    def update_camera(self, dt):
        camera_movement_speed = 500  # pixels per second

        if self.move_left:
            self.camera_x = max(self.camera_x - camera_movement_speed * dt, 0)
        if self.move_right:
            self.camera_x = min(self.camera_x + camera_movement_speed * dt,
                                self.world_height - self.screen.get_width() + self.panel.width)
        if self.move_up:
            self.camera_y = max(self.camera_y - camera_movement_speed * dt, 0)
        if self.move_down:
            self.camera_y = min(self.camera_y + camera_movement_speed * dt,
                                self.world_width - self.screen.get_height())

    def process_events(self, event):
        self.panel.process_events(event)

    def render(self):
        # Handle rendering here
        self.view_port = pygame.Rect(self.camera_x, self.camera_y, self.screen.get_width(), self.screen.get_height())
        self.world.fill((0, 0, 0))

        # Fill the entire molecule layer with transparent.
        self.molecule_layer.fill((0, 0, 0, 0))

        # Create a new surface for the visible layer.
        visible_layer = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)

        # Render molecules only within the visible region onto the visible layer.
        self.render_molecules(visible_layer)

        # Blit the visible layer onto the world surface.
        self.world.blit(visible_layer, self.view_port)

        self.render_walls(self.world)

        # Render the overall camera view (screen).
        self.render_camera_view()

        # Render the panel
        self.panel.render(self.screen)

        # Apply the changes to the screen
        pygame.display.flip()

    def get_molecules_in_viewport(self):
        viewport_bb = pymunk.BB(self.camera_x, self.camera_y,
                                self.camera_x + self.screen.get_width(),
                                self.camera_y + self.screen.get_height())
        shapes_in_viewport = self.space.bb_query(viewport_bb, pymunk.ShapeFilter())
        molecules_in_viewport = [shape.body.molecule for shape in shapes_in_viewport if hasattr(shape.body, 'molecule')]
        return molecules_in_viewport

    def render_molecules(self, layer):
        rect_left, rect_top, rect_width, rect_height = self.view_port
        molecules_in_viewport = self.get_molecules_in_viewport()
        for molecule in molecules_in_viewport:
            pos_x, pos_y = molecule.body.position
            screen_pos_x, screen_pos_y = (pos_x - rect_left), (pos_y - rect_top)
            pygame.draw.circle(layer, molecule.color, (screen_pos_x, screen_pos_y), molecule.radius)

    def render_camera_view(self):
        self.screen.blit(self.world.subsurface(self.view_port), (0, 0))

    def add_walls(self):
        thickness = 5
        color = 'grey'  # Dark gray

        # Define the positions of the walls
        top = 0
        bottom = self.world_height
        left = 0
        right = self.world_width

        # Create walls
        walls = [pymunk.Segment(self.space.static_body, (left, top), (right, top), thickness),
                 pymunk.Segment(self.space.static_body, (right, top), (right, bottom), thickness),
                 pymunk.Segment(self.space.static_body, (right, bottom), (left, bottom), thickness),
                 pymunk.Segment(self.space.static_body, (left, bottom), (left, top), thickness)]

        # Set the color for the walls
        for wall in walls:
            wall.color = pygame.color.THECOLORS[color]

        # Add walls to the space
        self.space.add(*walls)
        return walls

    def render_walls(self, layer):
        # Draw the walls
        for wall in self.walls:
            p1, p2 = wall.a, wall.b
            pygame.draw.line(layer, wall.color, p1, p2, 5)
