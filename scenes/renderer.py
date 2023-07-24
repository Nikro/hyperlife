import pygame
import pymunk


class Renderer:
    def __init__(self, game_scene):
        self.game_scene = game_scene
        self.view_port = None

    def render(self):
        self.view_port = pygame.Rect(self.game_scene.camera_x, self.game_scene.camera_y, self.game_scene.screen.get_width(), self.game_scene.screen.get_height())
        self.game_scene.world.fill((0, 0, 0))
        self.game_scene.molecule_layer.fill((0, 0, 0, 0))

        visible_layer = pygame.Surface((self.game_scene.screen.get_width(), self.game_scene.screen.get_height()), pygame.SRCALPHA)

        self.render_molecules(visible_layer)
        self.game_scene.world.blit(visible_layer, self.view_port)

        self.render_walls(self.game_scene.world)
        self.render_camera_view()
        self.game_scene.panel.render(self.game_scene.screen)

        pygame.display.flip()

    def render_molecules(self, layer):
        rect_left, rect_top, rect_width, rect_height = self.view_port
        molecules_in_viewport = self.get_molecules_in_viewport()
        for molecule in molecules_in_viewport:
            pos_x, pos_y = molecule.body.position
            screen_pos_x, screen_pos_y = (pos_x - rect_left), (pos_y - rect_top)
            pygame.draw.circle(layer, molecule.color, (screen_pos_x, screen_pos_y), molecule.radius)

    def render_walls(self, layer):
        for wall in self.game_scene.walls:
            p1, p2 = wall.a, wall.b
            pygame.draw.line(layer, wall.color, p1, p2, 5)

    def render_camera_view(self):
        self.game_scene.screen.blit(self.game_scene.world.subsurface(self.view_port), (0, 0))

    def get_molecules_in_viewport(self):
        viewport_bb = pymunk.BB(self.game_scene.camera_x, self.game_scene.camera_y,
                                self.game_scene.camera_x + self.game_scene.screen.get_width(),
                                self.game_scene.camera_y + self.game_scene.screen.get_height())
        shapes_in_viewport = self.game_scene.space.bb_query(viewport_bb, pymunk.ShapeFilter())
        molecules_in_viewport = [shape.body.molecule for shape in shapes_in_viewport if hasattr(shape.body, 'molecule')]
        return molecules_in_viewport
