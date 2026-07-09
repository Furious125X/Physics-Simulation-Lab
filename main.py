import pygame

from render.renderer import Renderer
from scenes.scenes import SpringScene

WIDTH = 800
HEIGHT = 600
FIXED_DT = 1 / 120

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Simulation Lab")

clock = pygame.time.Clock()

renderer = Renderer(screen)

scene = SpringScene()

running = True
accumulator = 0 

while running:

    frame_time = clock.tick(60) / 1000
    accumulator += frame_time

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        scene.handle_event(event)

    while accumulator >= FIXED_DT:

        scene.update(FIXED_DT)
        accumulator -= FIXED_DT

    screen.fill((20, 20, 20))

    scene.draw(renderer)

    pygame.display.flip()

pygame.quit()