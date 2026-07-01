import pygame

from physics.body import Body
from render.renderer import Renderer
from physics.world import World

WIDTH = 800
HEIGHT = 600


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Simulation Lab")

clock = pygame.time.Clock()

renderer = Renderer(screen)

world = World(gravity=500, floor_y=HEIGHT)

ball1 = Body(0, 1000)
ball2 = Body(400, 1000)
#ball3 = Body(550, 1000)

world.add_body(ball1)
world.add_body(ball2)
#world.add_body(ball3)

ball1.velocity.x = 250
ball2.mass = 5

running = True

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    world.update(dt)

    screen.fill((20, 20, 20))

    world.draw(renderer)

    pygame.display.flip()

pygame.quit()