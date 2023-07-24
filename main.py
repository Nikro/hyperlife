import time

import pygame
import threading
from scenes.game_scene import GameScene


class Main:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.scene = GameScene()
        self.physics_thread = threading.Thread(target=self.physics_loop)
        self.running = False

        self.SLOW_UPDATE_EVENT = pygame.event.custom_type()
        pygame.time.set_timer(self.SLOW_UPDATE_EVENT, 1000)

    def start(self):
        self.running = True
        self.physics_thread.start()

    def stop(self):
        self.running = False
        self.physics_thread.join()

    def physics_loop(self):
        t1 = time.time()
        while self.running:
            t2 = time.time()
            dt = t2 - t1
            self.scene.update_physics(dt)
            t1 = t2

    def main_loop(self):
        self.start()
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == self.SLOW_UPDATE_EVENT:
                    self.scene.update_slow()
                self.scene.process_events(event)

            # Update the scene with details.
            self.scene.fps = self.clock.get_fps()
            self.scene.handle_input()

            # Update the scene.
            self.scene.update(dt)

            # Render everything.
            self.scene.render()

            pygame.display.flip()

        self.stop()
        pygame.quit()


if __name__ == "__main__":
    Main().main_loop()
