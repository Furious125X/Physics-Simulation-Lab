import math
import pygame

from physics.body import Body
from physics.constraints import AtwoodConstraint
from physics.vector import Vector2

from scenes.base_scene import Scene

class AtwoodMachineScene(Scene):

    def __init__(self):

        super().__init__()

        self.pulley = Vector2(
            400,
            120
        )

        self.rope_length = 400

        self.body_radius = 20

        self.left_body = Body(
            self.pulley.x - 100,
            self.pulley.y + 173.205,
            self.body_radius,
            density=0.002,
            color=self.random_color()
        )

        self.right_body = Body(
            self.pulley.x + 100,
            self.pulley.y + 173.205,
            self.body_radius,
            density=0.004,
            color=self.random_color()
        )

        self.left_body.linear_damping = 0.0
        self.right_body.linear_damping = 0.0

        self.left_body.static_friction = 0.0
        self.left_body.dynamic_friction = 0.0

        self.right_body.static_friction = 0.0
        self.right_body.dynamic_friction = 0.0

        self.world.floor_y = 1000

        self.world.add_body(
            self.left_body
        )

        self.world.add_body(
            self.right_body
        )

        self.rope_constraint = AtwoodConstraint(
            self.left_body,
            self.right_body,
            self.pulley,
            self.rope_length
        )

        self.world.add_constraint(
            self.rope_constraint
        )


    def draw(self, renderer):

        self.world.draw(renderer)

        pulley_position = (
            renderer.camera.world_to_screen(
                self.pulley
            )
        )

        left_position = (
            renderer.camera.world_to_screen(
                self.left_body.position
            )
        )

        right_position = (
            renderer.camera.world_to_screen(
                self.right_body.position
            )
        )

        pygame.draw.circle(
            renderer.screen,
            (180, 180, 180),
            (
                int(pulley_position.x),
                int(pulley_position.y)
            ),
            25
        )

        pygame.draw.line(
            renderer.screen,
            (220, 220, 220),
            (
                int(pulley_position.x),
                int(pulley_position.y)
            ),
            (
                int(left_position.x),
                int(left_position.y)
            ),
            3
        )

        pygame.draw.line(
            renderer.screen,
            (220, 220, 220),
            (
                int(pulley_position.x),
                int(pulley_position.y)
            ),
            (
                int(right_position.x),
                int(right_position.y)
            ),
            3
        )


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