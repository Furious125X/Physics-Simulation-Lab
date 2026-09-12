import pygame

from physics.body import Body
from physics.constraints import (
    AnchorConstraint,
    DistanceConstraint
)
from physics.vector import Vector2

from scenes.base_scene import Scene


class SoftBridgeScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 700

        self.columns = 13
        self.rows = 3
        self.spacing = 40
        self.radius = 8

        self.start_x = 140
        self.start_y = 250

        self.bodies = []
        self.grid = {}

        for y in range(self.rows):

            for x in range(self.columns):

                body = Body(
                    self.start_x + x * self.spacing,
                    self.start_y + y * self.spacing,
                    self.radius,
                    color=self.random_color()
                )

                body.linear_damping = 0.6
                body.restitution = 0.0
                body.static_friction = 0.6
                body.dynamic_friction = 0.4

                self.bodies.append(body)
                self.world.add_body(body)

                self.grid[(x, y)] = body

        self.add_structural_constraints()
        self.add_shear_constraints()
        self.add_bending_constraints()

        left_anchor = AnchorConstraint(
            self.grid[(0, 0)],
            Vector2(
                self.start_x,
                self.start_y
            ),
            0
        )

        right_anchor = AnchorConstraint(
            self.grid[(self.columns - 1, 0)],
            Vector2(
                self.start_x
                + (self.columns - 1) * self.spacing,
                self.start_y
            ),
            0
        )

        self.world.add_constraint(left_anchor)
        self.world.add_constraint(right_anchor)

        self.loads = []

        self.add_load()

    def add_constraint(
        self,
        body1,
        body2,
        length,
        compliance
    ):

        constraint = DistanceConstraint(
            body1,
            body2,
            length,
            compliance=compliance
        )

        self.world.add_constraint(constraint)

    def add_structural_constraints(self):

        for y in range(self.rows):

            for x in range(self.columns):

                current = self.grid[(x, y)]

                if x < self.columns - 1:

                    self.add_constraint(
                        current,
                        self.grid[(x + 1, y)],
                        self.spacing,
                        0.00001
                    )

                if y < self.rows - 1:

                    self.add_constraint(
                        current,
                        self.grid[(x, y + 1)],
                        self.spacing,
                        0.00001
                    )

    def add_shear_constraints(self):

        diagonal_length = self.spacing * (2 ** 0.5)

        for y in range(self.rows - 1):

            for x in range(self.columns - 1):

                top_left = self.grid[(x, y)]
                top_right = self.grid[(x + 1, y)]

                bottom_left = self.grid[(x, y + 1)]
                bottom_right = self.grid[(x + 1, y + 1)]

                self.add_constraint(
                    top_left,
                    bottom_right,
                    diagonal_length,
                    0.00003
                )

                self.add_constraint(
                    top_right,
                    bottom_left,
                    diagonal_length,
                    0.00003
                )

    def add_bending_constraints(self):

        bending_length = self.spacing * 2

        for y in range(self.rows):

            for x in range(self.columns):

                current = self.grid[(x, y)]

                if x < self.columns - 2:

                    self.add_constraint(
                        current,
                        self.grid[(x + 2, y)],
                        bending_length,
                        0.00008
                    )

                if y < self.rows - 2:

                    self.add_constraint(
                        current,
                        self.grid[(x, y + 2)],
                        bending_length,
                        0.00008
                    )

    def add_load(self):

        center_x = (
            self.start_x
            + (self.columns - 1)
            * self.spacing
            * 0.5
        )

        load = Body(
            center_x,
            self.start_y - 80,
            20,
            density=0.01,
            color=self.random_color()
        )

        load.linear_damping = 0.8
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

            self.add_load()

    def draw(self, renderer):

        self.world.draw(renderer)

        text = renderer.font.render(
            f"Bodies: {len(self.bodies)}   "
            f"Loads: {len(self.loads)}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )