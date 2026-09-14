import math
import pygame

from physics.body import Body
from physics.constraints import DistanceConstraint
from physics.vector import Vector2

from scenes.base_scene import Scene


class PressureScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 550

        self.ball_radius = 90
        self.particle_radius = 8
        self.outer_count = 16

        self.rest_area = 0.0
        self.pressure_strength = 3000

        self.center = Vector2(400, 180)

        self.bodies = []

        for i in range(self.outer_count):

            angle = (
                2
                * math.pi
                * i
                / self.outer_count
            )

            position = Vector2(
                self.center.x
                + math.cos(angle) * self.ball_radius,

                self.center.y
                + math.sin(angle) * self.ball_radius
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

            self.bodies.append(body)
            self.world.add_body(body)

        self.add_boundary_constraints()



    def add_boundary_constraints(self):

        for i in range(self.outer_count):

            body1 = self.bodies[i]

            body2 = self.bodies[
                (i + 1) % self.outer_count
            ]

            distance = (
                body2.position
                - body1.position
            ).length()

            constraint = DistanceConstraint(
                body1,
                body2,
                distance,
                compliance=0.0002
            )

            self.world.add_constraint(constraint)


    def calculate_area(self):

        area = 0.0

        for i in range(self.outer_count):

            body1 = self.bodies[i]

            body2 = self.bodies[
                (i + 1) % self.outer_count
            ]

            area += (
                body1.position.x * body2.position.y
                - body1.position.y * body2.position.x
            )

        return abs(area) * 0.5


    def apply_pressure(self):

        current_area = self.calculate_area()

        if current_area <= 0:
            return

        pressure = self.pressure_strength * (
            self.rest_area / current_area - 1
        )

        for i in range(self.outer_count):

            previous_body = self.bodies[
                (i - 1) % self.outer_count
            ]

            current_body = self.bodies[i]

            next_body = self.bodies[
                (i + 1) % self.outer_count
            ]

            edge = (
                next_body.position
                - previous_body.position
            )

            normal = Vector2(
                -edge.y,
                edge.x
            ).normalize()

            force = normal * pressure

            current_body.apply_force(force)


    def update(self, dt):

        self.apply_pressure()

        super().update(dt)


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

        area = self.calculate_area()

        pressure = 0.0

        if area > 0:

            pressure = self.pressure_strength * (
                self.rest_area / area - 1
            )

        text = renderer.font.render(
            f"Area: {area:.0f}  Pressure: {pressure:.1f}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )