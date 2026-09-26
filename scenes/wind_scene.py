import math
import pygame

from physics.body import Body
from physics.constraints import (
    AnchorConstraint,
    DistanceConstraint
)
from physics.vector import Vector2

from scenes.base_scene import Scene


class WindScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 700

        self.segment_count = 12
        self.spacing = 28
        self.segment_radius = 6

        self.wind_strength = 180.0
        self.gust_strength = 80.0
        self.gust_frequency = 1.2

        self.wind_enabled = True
        self.wind_time = 0.0

        self.max_wind_force = 250.0

        self.strips = []

        self.create_strip(
            400,
            150
        )


    def create_strip(self, start_x, start_y):

        bodies = []

        for i in range(self.segment_count):

            body = Body(
                start_x,
                start_y + i * self.spacing,
                self.segment_radius,
                color=self.random_color()
            )

            body.linear_damping = 0.4
            body.restitution = 0.0
            body.static_friction = 0.6
            body.dynamic_friction = 0.4

            bodies.append(body)
            self.world.add_body(body)

        anchor = Vector2(
            start_x,
            start_y
        )

        anchor_constraint = AnchorConstraint(
            bodies[0],
            anchor,
            0
        )

        self.world.add_constraint(
            anchor_constraint
        )

        for i in range(self.segment_count - 1):

            constraint = DistanceConstraint(
                bodies[i],
                bodies[i + 1],
                self.spacing,
                compliance=0.00002
            )

            self.world.add_constraint(
                constraint
            )

        self.strips.append(bodies)

    def apply_wind(self, dt):

        if not self.wind_enabled:
            return

        self.wind_time += dt

        for strip in self.strips:

            for body in strip:

                height_factor = max(
                    0.0,
                    min(
                        1.0,
                        (550 - body.position.y) / 500
                    )
                )

                gust = math.sin(
                    self.wind_time
                    * self.gust_frequency
                    + body.id * 0.35
                )

                wind_acceleration = (
                    self.wind_strength
                    + gust * self.gust_strength
                )

                wind_acceleration *= (
                    0.6
                    + 0.4 * height_factor
                )

                force = Vector2(
                    wind_acceleration
                    * body.mass,
                    0
                )

                force_length = force.length()

                if force_length > self.max_wind_force:

                    force = (
                        force.normalize()
                        * self.max_wind_force
                    )

                body.apply_force(force)

    def update(self, dt):

        self.apply_wind(dt)

        super().update(dt)

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                self.wind_enabled = (
                    not self.wind_enabled
                )

            elif event.key == pygame.K_z:

                self.wind_strength = max(
                    0.0,
                    self.wind_strength - 25.0
                )

            elif event.key == pygame.K_x:

                self.wind_strength = min(
                    500.0,
                    self.wind_strength + 25.0
                )

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

        status = (
            "ON"
            if self.wind_enabled
            else "OFF"
        )

        text = renderer.font.render(
            (
                f"Wind: {status}  "
                f"Strength: {self.wind_strength:.0f}"
            ),
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )

        controls = renderer.font.render(
            "SPACE: Toggle Wind  Z/X: Wind Strength",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            controls,
            (10, 135)
        )