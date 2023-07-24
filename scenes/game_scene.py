import random

import pygame
import pymunk
from pymunk import ShapeFilter

from GUI.gui import Panel
from particles.molecule import Molecule
from scenes.renderer import Renderer


class GameScene:
    def __init__(self):
        self.move_down = None
        self.move_up = None
        self.move_right = None
        self.move_left = None
        self.view_port = None
        self.fps = 60
        self.game_speed = 1
        self.screen = None
        self.world_width = None
        self.world_height = None
        self.molecule_layer = None
        self.space = None
        self.camera_x = None
        self.camera_y = None
        self.panel = None
        self.world = None
        self.walls = None
        self.molecules = []
        self.renderer = Renderer(self)

        # Init everything.
        self.init_game()
        self.init_world()
        self.init_molecules()

    def init_game(self):
        self.game_speed = 1
        self.screen = pygame.display.set_mode((1200, 800))
        icon = pygame.image.load('assets/images/icon.png')

        # Set an icon in the center of the screen while the game is loading
        self.screen.fill((0, 0, 0))
        self.screen.blit(icon, (self.screen.get_width() / 2 - icon.get_width() / 2,
                                self.screen.get_height() / 2 - icon.get_height() / 2))
        pygame.display.flip()

        # Draw the texture onto the world
        self.camera_x, self.camera_y = 0, 0

        # Create a panel
        self.panel = Panel(self.screen.get_width(), self.screen.get_height(), self)

        # Set the window icon
        pygame.display.set_icon(icon)

        # Set the window caption
        pygame.display.set_caption("HyperLife 1.0 - Sandbox")

    def init_world(self):
        self.world_width = 3000
        self.world_height = 3000
        self.molecule_layer = pygame.Surface((self.world_width, self.world_height), pygame.SRCALPHA)
        self.space = pymunk.Space()

        # Add world and walls
        self.world = pygame.Surface((self.world_width + self.panel.width, self.world_height))
        self.walls = self.add_walls()

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

    def handle_input(self):
        # handle user input here
        keys = pygame.key.get_pressed()
        self.move_left = keys[pygame.K_LEFT]
        self.move_right = keys[pygame.K_RIGHT]
        self.move_up = keys[pygame.K_UP]
        self.move_down = keys[pygame.K_DOWN]

        # Handle panel inputs
        for event in pygame.event.get():
            self.panel.process_events(event)

    ############################
    # UPDATES, there are 3 types:
    # 1. Physics updates
    # 2. Slow updates
    # 3. Normal updates (that split further)
    ############################
    def update(self, dt):
        self.update_camera(dt)
        self.update_rest(dt)

    def update_physics(self, dt):
        for _ in range(int(self.game_speed)):
            self.space.step(dt)

    def update_slow(self):
        self.panel.set_molecules_count(len(self.molecules))

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

    def update_rest(self, dt):
        if self.fps < 10:
            # Decrease, but don't go below 1.
            self.game_speed = max(1, self.game_speed - 1)
            self.panel.speed_slider.set_current_value(int(self.game_speed))

        self.panel.set_fps(int(self.fps))
        self.panel.set_game_speed(int(self.game_speed))
        self.panel.update(dt)

    def process_events(self, event):
        self.panel.process_events(event)

    def render(self):
        self.renderer.render()

    def add_walls(self):
        thickness = 5
        color = 'grey'

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

