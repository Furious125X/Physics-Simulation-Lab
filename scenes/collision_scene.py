import random
import pygame

from physics.body import Body

from scenes.base_scene import Scene
from physics.vector import Vector2

class CollisionScene(Scene):

    def __init__(self):

        super().__init__()

        for _ in range(30):

            body = Body(
                random.randint(50, 750),
                random.randint(50, 550),
                random.randint(8, 30),
                color=self.random_color()
            )

            body.velocity.x = random.randint(-200, 200)
            body.velocity.y = random.randint(-100, 100)

            self.world.add_body(body)

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_position = Vector2(mouse_x, mouse_y)

            self.selected_body = self.find_body_at_position(mouse_position)

        elif event.type == pygame.MOUSEBUTTONUP:

            self.selected_body = None

        elif event.type == pygame.MOUSEWHEEL:

            mouse_x, mouse_y = pygame.mouse.get_pos()

            body = Body(
                mouse_x,
                mouse_y,
                random.randint(10, 40),
                color=self.random_color()
            )

            self.world.add_body(body)
