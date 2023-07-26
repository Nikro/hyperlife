import pygame
import pygame_gui
from events import *

class Panel:
    def __init__(self, screen_width, screen_height, game_scene):
        self.width = 150
        self.game_scene = game_scene

        self.manager = pygame_gui.UIManager((screen_width, screen_height), "GUI/theme.json")

        self.container = pygame_gui.core.UIContainer(
            relative_rect=pygame.Rect((screen_width - self.width, 0), (self.width, screen_height)),
            manager=self.manager
        )

        # Add panel
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (self.width, screen_height)),
            manager=self.manager,
            container=self.container,
            parent_element=self.container
        )

        self.fps_psu_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((5, 5), (140, 30)),
            text='FPS: 0 | PSU: 0',
            manager=self.manager,
            container=self.container,
            parent_element=self.panel
        )
        self.game_speed_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((5, 40), (140, 30)),
            text='SPEED: 0',
            manager=self.manager,
            container=self.container,
            parent_element=self.panel
        )
        self.speed_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((5, 75), (140, 30)),
            start_value=1,
            value_range=(1, 20),
            manager=self.manager,
            container=self.container,
            parent_element=self.panel
        )
        self.molecules_count_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((5, 110), (140, 30)),
            text='Molecules: 0',
            manager=self.manager,
            container=self.container,
            parent_element=self.panel
        )
        self.waves_count_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((5, 145), (140, 30)),
            text='Waves: 0',
            manager=self.manager,
            container=self.container,
            parent_element=self.panel
        )

    def process_events(self, event):
        # Make sure we don't process the custom events.
        self.manager.process_events(event)

        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.speed_slider:
                self.game_scene.game_speed = event.value


    def update(self, delta_time):
        self.manager.update(delta_time)

    def render(self, screen):
        self.manager.draw_ui(screen)

    def set_fps_psu(self, fps, psu):
        self.fps_psu_label.set_text(f"FPS: {fps} | PSU: {psu}")

    def set_game_speed(self, speed):
        self.game_speed_label.set_text(f"SPEED: {speed}x")

    def set_molecules_count(self, count):
        self.molecules_count_label.set_text(f"Molecules: {count}")

    def set_waves_count(self, count):
        self.waves_count_label.set_text(f"Waves: {count}")
