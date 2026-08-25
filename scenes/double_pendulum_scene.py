import pygame

from physics.body import Body
from physics.constraints import (
    AnchorConstraint,
    DistanceConstraint
)
from physics.vector import Vector2

from scenes.base_scene import Scene


class DoublePendulumScene(Scene):

    def __init__(self):

        super().__init__()

        anchor = Vector2(400, 100)

        length_1 = 180
        length_2 = 180

        radius = 18

        bob1 = Body(
            anchor.x + 108,
            anchor.y + 144,
            radius,
            color=self.random_color()
        )

        bob2 = Body(
            bob1.position.x + 108,
            bob1.position.y + 144,
            radius,
            color=self.random_color()
        )

        constraint_1 = AnchorConstraint(
            bob1,
            anchor,
            length_1
        )

        constraint_2 = DistanceConstraint(
            bob1,
            bob2,
            length_2
        )

        bob2.velocity = Vector2(
            120,
            0
        )

        self.world.add_body(bob1)
        self.world.add_body(bob2)

        self.world.add_constraint(constraint_1)
        self.world.add_constraint(constraint_2)


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

    