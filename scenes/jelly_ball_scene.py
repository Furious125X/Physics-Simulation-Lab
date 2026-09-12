import math
import pygame

from physics.body import Body
from physics.constraints import DistanceConstraint
from physics.vector import Vector2

from scenes.base_scene import Scene


class JellyBallScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 550

        self.ball_radius = 90
        self.particle_radius = 8
        self.outer_count = 16

        self.center = Vector2(400, 180)

        self.center_body = Body(
            self.center.x,
            self.center.y,
            self.particle_radius,
            color=self.random_color()
        )

        self.center_body.linear_damping = 0.5
        self.center_body.restitution = 0.0
        self.center_body.static_friction = 0.6
        self.center_body.dynamic_friction = 0.4

        self.world.add_body(self.center_body)

        self.outer_bodies = []

        for i in range(self.outer_count):

            angle = (
                2
                * math.pi
                * i
                / self.outer_count
            )

            position = Vector2(
                self.center.x
                + math.cos(angle)
                * self.ball_radius,

                self.center.y
                + math.sin(angle)
                * self.ball_radius
            )

            body = Body(
                position.x,
                position.y,
                self.particle_radius,
                color=self.random_color()
            )

            body.linear_damping = 0.5
            body.restitution = 0.0
            body.static_friction = 0.6
            body.dynamic_friction = 0.4

            self.outer_bodies.append(body)
            self.world.add_body(body)

        self.add_radial_constraints()
        self.add_ring_constraints()
        self.add_bending_constraints()

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

    def add_radial_constraints(self):

        for body in self.outer_bodies:

            distance = (
                body.position
                - self.center_body.position
            ).length()

            self.add_constraint(
                self.center_body,
                body,
                distance,
                0.0004
            )

    def add_ring_constraints(self):

        for i in range(self.outer_count):

            body1 = self.outer_bodies[i]

            body2 = self.outer_bodies[
                (i + 1) % self.outer_count
            ]

            distance = (
                body2.position
                - body1.position
            ).length()

            self.add_constraint(
                body1,
                body2,
                distance,
                0.0002
            )

    def add_bending_constraints(self):

        for i in range(self.outer_count):

            body1 = self.outer_bodies[i]

            body2 = self.outer_bodies[
                (i + 2) % self.outer_count
            ]

            distance = (
                body2.position
                - body1.position
            ).length()

            self.add_constraint(
                body1,
                body2,
                distance,
                0.001
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

    def draw(self, renderer):

        self.world.draw(renderer)

        text = renderer.font.render(
            f"Particles: {len(self.outer_bodies) + 1}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )