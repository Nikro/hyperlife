import random
import pygame
import pymunk

from GUI.gui import Panel
from particles.molecule import Molecule
from particles.wave import Wave
from scenes.renderer import Renderer
from scenes.constants import *
from events import *


class GameScene:
    def __init__(self):
        self.refresh_waves = False
        self.move_down = None
        self.move_up = None
        self.move_right = None
        self.move_left = None
        self.view_port = None
        self.fps = 60
        self.psu = 60
        self.game_speed = 1
        self.screen = None
        self.world_width = 5000
        self.world_height = 5000
        self.molecule_layer = None
        self.molecules_count = 40000
        self.space = None
        self.camera_x = 0
        self.camera_y = 0
        self.panel = None
        self.world = None
        self.walls = None
        self.molecules = {}
        self.visible_molecules = []
        self.renderer = Renderer(self)
        self.physics_slow_steps = 0

        # Init everything.
        self.init_game()
        self.init_world()
        # Fill the world.
        self.setup_collisions()
        self.init_molecules()

        self.waves_active = []
        pygame.time.set_timer(WAVE_INIT_EVENT, 5000)

    def init_game(self):
        self.game_speed = 1
        self.screen = pygame.display.set_mode((1200, 800))
        icon = pygame.image.load('assets/images/icon.png')

        # Set an icon in the center of the screen while the game is loading
        self.screen.fill((0, 0, 0))
        self.screen.blit(icon, (self.screen.get_width() / 2 - icon.get_width() / 2,
                                self.screen.get_height() / 2 - icon.get_height() / 2))
        pygame.display.flip()

        # Create a panel
        self.panel = Panel(self.screen.get_width(), self.screen.get_height(), self)

        # Set the window icon
        pygame.display.set_icon(icon)

        # Set the window caption
        pygame.display.set_caption("HyperLife 1.0 - Sandbox")

    def init_world(self):
        self.molecule_layer = pygame.Surface((self.world_width, self.world_height), pygame.SRCALPHA)
        self.space = pymunk.Space(threaded=True)
        self.space.threads = 6
        self.space.use_spatial_hash(10, 400000)
        self.space.damping = 0.95
        self.space.sleep_time_threshold = 0.1
        self.space.idle_speed_threshold = 0.01

        # Add world and walls
        self.world = pygame.Surface((self.world_width + self.panel.width, self.world_height))
        self.walls = self.add_walls()

    def init_molecules(self):
        padding = 100  # Padding from walls
        radius = 2  # Radius of molecule

        # Calculate the area of the simulation space
        width = self.world_width - 2 * padding
        height = self.world_height - 2 * padding

        # Compute the number of molecules in one dimension
        molecule_count_one_dim = int((self.molecules_count ** 0.5))

        # Calculate the gap and distance between molecules
        gap = min(width, height) / molecule_count_one_dim - 2 * radius
        distance = 2 * radius + gap

        # Adjust the molecule count in one dimension based on the actual gap
        horizontal_molecule_count = int(width // distance)
        vertical_molecule_count = int(height // distance)

        # The actual number of molecules may be less than the requested due to rounding down
        self.molecules_count = horizontal_molecule_count * vertical_molecule_count

        for i in range(horizontal_molecule_count):
            for j in range(vertical_molecule_count):
                position = (padding + distance * i + distance // 2, padding + distance * j + distance // 2)

                mass = random.randint(1, 10)
                molecule_radius = random.randint(2, 5)
                molecule = Molecule(self.space, molecule_radius, mass, None, position)
                impulse = pymunk.Vec2d(random.uniform(-100, 100), random.uniform(-100, 100))
                molecule.apply_impulse(impulse)

                self.molecules[molecule.id] = molecule

    def init_waves(self):
        # Reduce just to 1 wave at a time.
        radius = random.randint(500, 1000)  # Adjust this range as needed
        impulse_strength = random.randint(50, 150)  # Adjust this range as needed
        position = (random.randint(0, self.world_width), random.randint(0, self.world_height))
        # position = (500, 500)
        velocity = pymunk.Vec2d(random.randint(0, 0), random.randint(100, 100))
        wave = Wave(self, self.space, radius, impulse_strength, velocity, position)
        self.waves_active.append(wave)

    def setup_collisions(self):
        wave_collision_handler = self.space.add_collision_handler(WAVE_COLLISION, MOLECULE_COLLISION)
        Wave.setup_wave_collision(wave_collision_handler)

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

            for molecule in self.molecules.values():
                molecule.update_physics(dt)

            # Create waves.
            if self.refresh_waves:
                self.refresh_waves = False
                self.init_waves()

            # Clean up waves.
            for wave in self.waves_active:
                wave.update_physics(dt)

            # For slow physics updates.
            # self.physics_slow_steps += 1
            # if self.physics_slow_steps % 100 == 0:
            # self.update_physics_slow()
            # self.physics_slow_steps = 1

        # This is independent of physics updates, but relies on physics updates.
        self.visible_molecules = self.get_molecules_in_viewport()

        # for molecule in self.molecules.values():
        #     molecule.update_physics(dt)
        # self.space.step(0)
        # for molecule in self.molecules.values():
        #     molecule.handle_mergers()

    def update_slow(self):
        self.panel.set_molecules_count(len(self.molecules))
        self.panel.set_waves_count(len(self.waves_active))

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

        self.panel.set_fps_psu(int(self.fps), int(self.psu))
        self.panel.set_game_speed(int(self.game_speed))
        self.panel.update(dt)

    def process_events(self, event):
        self.panel.process_events(event)

        if event.type == WAVE_INIT_EVENT:
            if len(self.waves_active) == 0:
                self.refresh_waves = True

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

    def get_molecules_in_viewport(self):
        # Define the amount you want to extend the viewport by
        extension = 200

        # Compute the extended viewport bounds, ensuring they don't exceed the world bounds
        extended_left = max(0, self.camera_x - extension)
        extended_bottom = max(0, self.camera_y - extension)
        extended_right = min(self.world_width, self.camera_x + self.screen.get_width() + extension)
        extended_top = min(self.world_height, self.camera_y + self.screen.get_height() + extension)

        # Create the extended viewport bounding box
        extended_viewport_bb = pymunk.BB(extended_left, extended_bottom, extended_right, extended_top)
        shapes_in_viewport = self.space.bb_query(extended_viewport_bb, pymunk.ShapeFilter())
        molecules_in_viewport = [shape.body.molecule for shape in shapes_in_viewport if hasattr(shape.body, 'molecule')]
        return molecules_in_viewport
