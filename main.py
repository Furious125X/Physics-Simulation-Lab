import pygame

from render.renderer import Renderer
from scenes.scenes import SpringScene

WIDTH = 800
HEIGHT = 600

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Simulation Lab")

clock = pygame.time.Clock()

renderer = Renderer(screen)

scene = SpringScene()

running = True

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        scene.handle_event(event)

    scene.update(dt)

    screen.fill((20, 20, 20))

    scene.draw(renderer)

    pygame.display.flip()

pygame.quit()