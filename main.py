import pygame
from scenes.game_scene import GameScene


def main():
    pygame.init()
    clock = pygame.time.Clock()
    scene = GameScene()

    running = True
    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene.process_events(event)

        # Update the scene with details.
        scene.fps = clock.get_fps()
        scene.handle_input()

        # Update the scene.
        scene.update(dt)

        # Render everything.
        scene.render()
    pygame.quit()


if __name__ == "__main__":
    main()
