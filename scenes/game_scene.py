import random

import pygame
import pymunk

from GUI.gui import Panel
from particles.molecule import Molecule


class GameScene:
    def __init__(self):
        self.move_down = None
        self.move_up = None
        self.move_right = None
        self.move_left = None
        self.fps = None
        self.game_speed = 1
        self.screen = pygame.display.set_mode((1200, 800))
        self.world = pygame.Surface((2406, 2411))
        self.molecule_layer = pygame.Surface((2406, 2411), pygame.SRCALPHA)

        self.space = pymunk.Space()

        # Load the texture and icons and what not.
        self.icon = pygame.image.load('assets/images/icon.png')

        # Draw the texture onto the world
        self.camera_x, self.camera_y = 0, 0

        # Create a panel
        self.panel = Panel(self.screen.get_width(), self.screen.get_height(), self)

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
        for _ in range(25000):
            radius = random.randint(1, 2)
            mass = random.randint(1, 10)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            position = (random.uniform(0, self.world.get_width()), random.uniform(0, self.world.get_height()))
            molecule = Molecule(self.space, radius, mass, color, position)
            impulse = pymunk.Vec2d(random.uniform(-100, 100), random.uniform(-100, 100))
            molecule.apply_impulse(impulse)
            self.molecules.append(molecule)

    def update(self, dt):
        # update game - physics, simulation, camera, rest.
        for _ in range(int(self.game_speed)):
            self.update_physics(dt)

        self.update_camera(dt)
        self.update_rest(dt)

    def update_physics(self, dt):
        self.space.step(dt)

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
        # update game state here
        if self.move_left:
            self.camera_x -= camera_movement_speed * dt
        if self.move_right:
            self.camera_x += camera_movement_speed * dt
        if self.move_up:
            self.camera_y -= camera_movement_speed * dt
        if self.move_down:
            self.camera_y += camera_movement_speed * dt

        # Prevent the camera from moving outside of the world
        if self.camera_x < 0:
            self.camera_x += self.world.get_width()
        elif self.camera_x >= self.world.get_width():
            self.camera_x -= self.world.get_width()
        if self.camera_y < 0:
            self.camera_y += self.world.get_height()
        elif self.camera_y >= self.world.get_height():
            self.camera_y -= self.world.get_height()

    def process_events(self, event):
        self.panel.process_events(event)

    def render(self):
        # Handle rendering here
        # Fill the world with black - and background.
        self.world.fill((0, 0, 0))

        # Fill the molecule layer with transparent.
        self.molecule_layer.fill((0, 0, 0, 0))
        self.render_molecules(self.molecule_layer)
        self.world.blit(self.molecule_layer, (0, 0))

        # Render the overall camera view (screen).
        self.render_camera_view()

        # Render the panel
        self.panel.render(self.screen)

        # Apply the changes to the screen
        pygame.display.flip()

    def render_molecules(self, layer):
        # Define camera bounds
        camera_left = self.camera_x
        camera_right = self.camera_x + self.screen.get_width()
        camera_top = self.camera_y
        camera_bottom = self.camera_y + self.screen.get_height()

        for molecule in self.molecules:
            position = molecule.body.position

            # Check if the molecule is within the camera view
            if camera_left <= position.x <= camera_right and camera_top <= position.y <= camera_bottom:
                pygame.draw.circle(layer, molecule.color, (int(position.x), int(position.y)), molecule.radius)

    def render_camera_view(self):
        # Calculate the width and height of the world to be displayed
        display_width = min(self.screen.get_width() - self.panel.width,
                            self.world.get_width() - self.camera_x)
        display_height = min(self.screen.get_height(),
                             self.world.get_height() - self.camera_y)

        # Draw the visible part of the world surface onto the screen
        self.screen.blit(self.world.subsurface(self.camera_x, self.camera_y, display_width, display_height),
                         (0, 0))

        # If the camera view straddles the edge of the world in the x-direction
        if display_width < self.screen.get_width() - self.panel.width:
            remaining_width = self.screen.get_width() - self.panel.width - display_width
            self.screen.blit(self.world.subsurface(0, self.camera_y, remaining_width, display_height),
                             (display_width, 0))

        # If the camera view straddles the edge of the world in the y-direction
        if display_height < self.screen.get_height():
            remaining_height = self.screen.get_height() - display_height
            self.screen.blit(self.world.subsurface(self.camera_x, 0, display_width, remaining_height),
                             (0, display_height))

        # If the camera view is at a corner of the world
        if display_width < self.screen.get_width() - self.panel.width and display_height < self.screen.get_height():
            remaining_width = self.screen.get_width() - self.panel.width - display_width
            remaining_height = self.screen.get_height() - display_height
            self.screen.blit(self.world.subsurface(0, 0, remaining_width, remaining_height),
                             (display_width, display_height))
