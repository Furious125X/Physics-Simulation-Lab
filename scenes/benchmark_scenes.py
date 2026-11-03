import math
import pygame

from physics.body import Body
from physics.constraints import (
    AnchorConstraint,
    DistanceConstraint
)
from physics.vector import Vector2

from scenes.base_scene import Scene


class BodyBenchmarkScene(Scene):

    def __init__(self):
        super().__init__()

        self.world.gravity = 0
        self.world.floor_y = 1000

        self.columns = 20
        self.rows = 15
        self.spacing = 30
        self.radius = 7

        self.bodies = []

        for row in range(self.rows):

            for column in range(self.columns):

                body = Body(
                    95 + column * self.spacing,
                    70 + row * self.spacing,
                    radius=self.radius,
                    color=(120, 180, 230)
                )

                # Keep bodies awake throughout the benchmark.
                body.sleep_time = float("inf")

                self.bodies.append(body)
                self.world.add_body(body)

    def draw(self, renderer):

        self.world.draw(renderer)

        text = renderer.font.render(
            f"BODY BENCHMARK | Bodies: {len(self.bodies)}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )


class CollisionBenchmarkScene(Scene):

    def __init__(self):
        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 560

        self.columns = 10
        self.rows = 8
        self.spacing = 17.8
        self.radius = 9

        self.start_x = 307
        self.start_y = 260

        self.bodies = []

        vertical_spacing = (
            self.spacing * math.sqrt(3) / 2
        )

        for row in range(self.rows):

            for column in range(self.columns):

                x_offset = (
                    self.spacing / 2
                    if row % 2
                    else 0
                )

                body = Body(
                    self.start_x
                    + column * self.spacing
                    + x_offset,

                    self.start_y
                    + row * vertical_spacing,

                    radius=self.radius,
                    color=(220, 150, 100)
                )

                body.restitution = 0.05
                body.static_friction = 0.7
                body.dynamic_friction = 0.5

                # Keep the pile active after settling.
                body.sleep_time = float("inf")

                self.bodies.append(body)
                self.world.add_body(body)

    def draw(self, renderer):

        self.world.draw(renderer)

        text = renderer.font.render(
            f"COLLISION BENCHMARK | Bodies: {len(self.bodies)}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )


class ConstraintBenchmarkScene(Scene):

    def __init__(self):
        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 700

        self.columns = 15
        self.rows = 5
        self.spacing = 24
        self.radius = 5

        self.start_x = 232
        self.start_y = 170

        self.bodies = []
        self.body_grid = {}

        self.create_bodies()
        self.add_structural_constraints()
        self.add_shear_constraints()
        self.add_bending_constraints()
        self.add_anchors()

    def create_bodies(self):

        for y in range(self.rows):

            for x in range(self.columns):

                body = Body(
                    self.start_x + x * self.spacing,
                    self.start_y + y * self.spacing,
                    radius=self.radius,
                    color=(140, 200, 150)
                )

                body.restitution = 0
                body.linear_damping = 0.6

                # Keep the constraint workload active.
                body.sleep_time = float("inf")

                self.bodies.append(body)
                self.world.add_body(body)

                self.body_grid[(x, y)] = body

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

                current = self.body_grid[(x, y)]

                if x < self.columns - 1:

                    self.add_constraint(
                        current,
                        self.body_grid[(x + 1, y)],
                        self.spacing,
                        0.00001
                    )

                if y < self.rows - 1:

                    self.add_constraint(
                        current,
                        self.body_grid[(x, y + 1)],
                        self.spacing,
                        0.00001
                    )

    def add_shear_constraints(self):

        diagonal_length = (
            self.spacing * math.sqrt(2)
        )

        for y in range(self.rows - 1):

            for x in range(self.columns - 1):

                top_left = self.body_grid[(x, y)]
                top_right = self.body_grid[(x + 1, y)]

                bottom_left = self.body_grid[(x, y + 1)]
                bottom_right = self.body_grid[(x + 1, y + 1)]

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

                current = self.body_grid[(x, y)]

                if x < self.columns - 2:

                    self.add_constraint(
                        current,
                        self.body_grid[(x + 2, y)],
                        bending_length,
                        0.00008
                    )

                if y < self.rows - 2:

                    self.add_constraint(
                        current,
                        self.body_grid[(x, y + 2)],
                        bending_length,
                        0.00008
                    )

    def add_anchors(self):

        left_anchor = AnchorConstraint(
            self.body_grid[(0, 0)],
            Vector2(
                self.start_x,
                self.start_y
            ),
            0
        )

        right_anchor = AnchorConstraint(
            self.body_grid[(self.columns - 1, 0)],
            Vector2(
                self.start_x
                + (self.columns - 1) * self.spacing,
                self.start_y
            ),
            0
        )

        self.world.add_constraint(left_anchor)
        self.world.add_constraint(right_anchor)

    def draw(self, renderer):

        self.world.draw(renderer)

        text = renderer.font.render(
            f"CONSTRAINT BENCHMARK | "
            f"Bodies: {len(self.bodies)} | "
            f"Constraints: {len(self.world.constraints)}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )