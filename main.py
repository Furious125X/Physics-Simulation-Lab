import pygame

from physics.body import Body
from physics.spring import Spring
from render.renderer import Renderer
from physics.world import World

import random

WIDTH = 800
HEIGHT = 600


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Simulation Lab")

clock = pygame.time.Clock()

renderer = Renderer(screen)

world = World(gravity=500, floor_y=HEIGHT)

ball1 = Body(500, 1000,6, color = (random.randint(50,255), random.randint(50,255), random.randint(50,255)))
ball2 = Body(530, 1000,6,  color = (random.randint(50,255), random.randint(50,255), random.randint(50,255)))
spring1 = Spring(ball1, ball2, 150, 5)

world.add_body(ball1)
world.add_body(ball2)
world.add_spring(spring1)

ball1.velocity.x = 250
ball2.mass = 5

running = True

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            body3 = Body(mouse_x, mouse_y,random.randint(10,40), color = (random.randint(50,255),random.randint(50,255),random.randint(50,255)))

            world.add_body(body3)

    world.update(dt)

    screen.fill((20, 20, 20))

    world.draw(renderer)

    pygame.display.flip()

pygame.quit()