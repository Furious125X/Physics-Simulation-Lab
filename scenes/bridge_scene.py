import pygame

from physics.body import Body
from physics.constraints import (
    AnchorConstraint,
    DistanceConstraint
)
from physics.vector import Vector2

from scenes.base_scene import Scene


class BridgeScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 700

        self.segment_count = 15
        self.segment_spacing = 35
        self.segment_radius = 8

        self.start_x = 150
        self.bridge_y = 300

        self.world.constraint_iterations = 15
        self.world.substeps = 4

        self.bridge_bodies = []

        for i in range(self.segment_count):

            body = Body(
                self.start_x + i * self.segment_spacing,
                self.bridge_y,
                self.segment_radius,
                color=self.random_color()
            )

            body.linear_damping = 0.2
            body.restitution = 0.0
            body.static_friction = 0.6
            body.dynamic_friction = 0.4

            self.bridge_bodies.append(body)

            self.world.add_body(body)

        left_anchor = Vector2(
            self.start_x,
            self.bridge_y
        )

        left_constraint = AnchorConstraint(
            self.bridge_bodies[0],
            left_anchor,
            0
        )

        self.world.add_constraint(
            left_constraint
        )

        right_anchor = Vector2(
            self.start_x
            + (self.segment_count - 1)
            * self.segment_spacing,
            self.bridge_y
        )

        right_constraint = AnchorConstraint(
            self.bridge_bodies[-1],
            right_anchor,
            0
        )

        self.world.add_constraint(
            right_constraint
        )

        for i in range(
            self.segment_count - 1
        ):

            constraint = DistanceConstraint(
                self.bridge_bodies[i],
                self.bridge_bodies[i + 1],
                self.segment_spacing,
                compliance=0.000001
            )

            self.world.add_constraint(
                constraint
            )

        for i in range(
            self.segment_count - 2
        ):

            constraint = DistanceConstraint(
                self.bridge_bodies[i],
                self.bridge_bodies[i + 2],
                self.segment_spacing * 2,
                compliance=0.00001
            )

            self.world.add_constraint(
                constraint
            )

        self.loads = []

        load_positions = [
            self.start_x + 210,
            self.start_x + 245,
            self.start_x + 280
        ]

        for x in load_positions:

            load = Body(
                x,
                self.bridge_y - 60,
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
            load.static_friction = 0.6
            load.dynamic_friction = 0.4

            self.loads.append(load)

            self.world.add_body(load)

    def draw(self, renderer):

        self.world.draw(renderer)

        left = renderer.camera.world_to_screen(
            Vector2(
                self.start_x,
                self.bridge_y
            )
        )

        right = renderer.camera.world_to_screen(
            Vector2(
                self.start_x
                + (self.segment_count - 1)
                * self.segment_spacing,
                self.bridge_y
            )
        )

        pygame.draw.polygon(
            renderer.screen,
            (180, 180, 180),
            [
                (
                    int(left.x - 20),
                    int(left.y + 25)
                ),
                (
                    int(left.x + 20),
                    int(left.y + 25)
                ),
                (
                    int(left.x),
                    int(left.y)
                )
            ]
        )

        pygame.draw.polygon(
            renderer.screen,
            (180, 180, 180),
            [
                (
                    int(right.x - 20),
                    int(right.y + 25)
                ),
                (
                    int(right.x + 20),
                    int(right.y + 25)
                ),
                (
                    int(right.x),
                    int(right.y)
                )
            ]
        )

        text = renderer.font.render(
            f"Loads: {len(self.loads)}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )