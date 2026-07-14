import pygame

from render.renderer import Renderer
from scenes.scenes import SpringScene, CollisionScene, NewtonCradleScene

WIDTH = 800
HEIGHT = 600
FIXED_DT = 1 / 120

pygame.init()

font = pygame.font.SysFont(None, 24)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Simulation Lab")

clock = pygame.time.Clock()

renderer = Renderer(screen)

current_scene = SpringScene()

running = True
accumulator = 0

while running:

    frame_time = clock.tick(60) / 1000
    accumulator += frame_time

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_1:
                current_scene = SpringScene()

            elif event.key == pygame.K_2:
                current_scene = CollisionScene()

            elif event.key == pygame.K_3:
                current_scene = NewtonCradleScene()
                
        current_scene.handle_event(event)

    while accumulator >= FIXED_DT:
        current_scene.update(FIXED_DT)
        accumulator -= FIXED_DT

    screen.fill((20, 20, 20))

    current_scene.draw(renderer)

    menu = font.render(
        "1: Spring Demo   2: Collision Demo  3: Newton's Cradle",
        True,
        (255, 255, 255)
    )

    screen.blit(menu, (10, 10))

    pygame.display.flip()

pygame.quit()