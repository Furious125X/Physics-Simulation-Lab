import random
import pygame

from physics.body import Body
from physics.spring import Spring
from physics.constraints import AnchorConstraint
from physics.vector import Vector2

from scenes.base_scene import Scene


class SpringScene(Scene):

    def __init__(self):

        super().__init__()

        ball1 = Body(
            500,
            100,
            20,
            color=self.random_color()
        )

        ball2 = Body(
            650,
            100,
            35,
            color=self.random_color()
        )

        ball3 = Body(
            500,
            150,
            20,
            color=self.random_color()
        )

        ball3anchor = Vector2(400, 150)

        ball3constraint = AnchorConstraint(
            ball3,
            ball3anchor,
            100
        )

        spring = Spring(
            ball1,
            ball2,
            rest_length=150,
            stiffness=5
        )

        ball1.velocity.x = 250

        self.world.add_body(ball1)
        self.world.add_body(ball2)
        self.world.add_body(ball3)

        self.world.add_spring(spring)
        self.world.add_constraint(ball3constraint)

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = pygame.mouse.get_pos()

            mouse_position = Vector2(
                mouse_x,
                mouse_y
            )

            self.selected_body = (
                self.find_body_at_position(
                    mouse_position
                )
            )

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