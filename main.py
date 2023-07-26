import time

import pygame
import threading
import cProfile
from events import *
from scenes.game_scene import GameScene


class Main:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.scene = GameScene()
        self.physics_thread = threading.Thread(target=self.physics_loop)
        self.running = False
        self.physics_updates = 0
        self.last_time = time.time()

        pygame.time.set_timer(SLOW_UPDATE_EVENT, 1000)

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
            self.physics_updates += 1
            t1 = t2
            if t2 - self.last_time > 1:
                self.last_time = t2
                self.scene.psu = self.physics_updates
                self.physics_updates = 0

    def main_loop(self):
        self.start()
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == SLOW_UPDATE_EVENT:
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
    # cProfile.run('Main().main_loop()',  sort='tottime')
