import pygame

from physics.body import Body
from render.renderer import Renderer


WIDTH = 800
HEIGHT = 600


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Simulation Lab")

clock = pygame.time.Clock()

renderer = Renderer(screen)

ball = Body(400, 100)

running = True

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ball.update(dt, HEIGHT)

    screen.fill((20, 20, 20))

    renderer.draw_ball(ball)

    pygame.display.flip()

pygame.quit()