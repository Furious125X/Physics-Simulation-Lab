import pygame

from physics.body import Body
from physics.constraints import AnchorConstraint
from physics.vector import Vector2

from scenes.base_scene import Scene

class PendulumScene(Scene):

    def __init__(self):

        super().__init__()

        anchor = Vector2(400, 100)

        length = 250

        radius = 20

        bob = Body(
            anchor.x + 150,
            anchor.y + 200,
            radius,
            color=self.random_color()
        )

        bob.velocity = Vector2(
            120,
            0
        )

        constraint = AnchorConstraint(
            bob,
            anchor,
            length
        )

        self.world.add_body(bob)
        self.world.add_constraint(constraint)

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