import math
import pygame

from physics.body import Body
from physics.constraints import (
    AnchorConstraint,
    DistanceConstraint
)
from physics.vector import Vector2

from scenes.base_scene import Scene

class TrussScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 700

        self.world.constraint_iterations = 15
        self.world.substeps = 4


        self.sections = 6
        self.spacing = 40
        self.height = 90

        self.start_x = 180
        self.bottom_y = 400

        self.top_nodes = []
        self.bottom_nodes = []


        for i in range(self.sections + 1):

            body = Body(
                self.start_x + i * self.spacing,
                self.bottom_y,
                12,
                color=self.random_color()
            )

            body.linear_damping = 0.2
            body.restitution = 0.0

            body.static_friction = 0.6
            body.dynamic_friction = 0.4

            self.bottom_nodes.append(body)

            self.world.add_body(body)


        for i in range(self.sections + 1):

            body = Body(
                self.start_x + i * self.spacing,
                self.bottom_y - self.height,
                12,
                color=self.random_color()
            )

            body.linear_damping = 0.2
            body.restitution = 0.0

            body.static_friction = 0.6
            body.dynamic_friction = 0.4

            self.top_nodes.append(body)

            self.world.add_body(body)


        self.nodes = (
            self.top_nodes
            + self.bottom_nodes
        )

        left_anchor = Vector2(
            self.start_x,
            self.bottom_y
        )

        left_constraint = AnchorConstraint(
            self.bottom_nodes[0],
            left_anchor,
            0
        )

        self.world.add_constraint(
            left_constraint
        )

        right_anchor = Vector2(
            self.start_x
            + self.sections * self.spacing,
            self.bottom_y
        )

        right_constraint = AnchorConstraint(
            self.bottom_nodes[-1],
            right_anchor,
            0
        )

        self.world.add_constraint(
            right_constraint
        )


        for i in range(self.sections):

            constraint = DistanceConstraint(
                self.top_nodes[i],
                self.top_nodes[i + 1],
                self.spacing,
                compliance=0.000001
            )

            self.world.add_constraint(
                constraint
            )


        for i in range(self.sections):

            constraint = DistanceConstraint(
                self.bottom_nodes[i],
                self.bottom_nodes[i + 1],
                self.spacing,
                compliance=0.000001
            )

            self.world.add_constraint(
                constraint
            )

        for i in range(self.sections + 1):

            constraint = DistanceConstraint(
                self.top_nodes[i],
                self.bottom_nodes[i],
                self.height,
                compliance=0.000001
            )

            self.world.add_constraint(
                constraint
            )

        diagonal_length = math.sqrt(
            self.spacing ** 2
            + self.height ** 2
        )

        for i in range(self.sections):

            diagonal_1 = DistanceConstraint(
                self.top_nodes[i],
                self.bottom_nodes[i + 1],
                diagonal_length,
                compliance=0.000001
            )

            diagonal_2 = DistanceConstraint(
                self.bottom_nodes[i],
                self.top_nodes[i + 1],
                diagonal_length,
                compliance=0.000001
            )

            self.world.add_constraint(
                diagonal_1
            )

            self.world.add_constraint(
                diagonal_2
            )


        self.loads = []

        load_positions = [
            self.start_x + 2 * self.spacing,
            self.start_x + 3 * self.spacing,
            self.start_x + 4 * self.spacing
        ]

        for x in load_positions:

            load = Body(
                x,
                self.bottom_y - self.height - 60,
                15,
                density=0.01,
                color=self.random_color()
            )

            load.linear_damping = 0.2
            load.restitution = 0.0
            load.static_friction = 0.6
            load.dynamic_friction = 0.4

            self.loads.append(load)

            self.world.add_body(load)


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

            load = Body(
                mouse_x,
                mouse_y,
                15,
                density=0.01,
                color=self.random_color()
            )

            load.linear_damping = 0.2
            load.restitution = 0.0

            self.loads.append(load)

            self.world.add_body(load)


    def draw(self, renderer):

        self.world.draw(renderer)

        text = renderer.font.render(
            f"Loads: {len(self.loads)}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )