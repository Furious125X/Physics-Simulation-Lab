import math
import pygame

from physics.body import Body
from physics.vector import Vector2

from scenes.base_scene import Scene


class InclinedPlaneScene(Scene):

    def __init__(self):

        super().__init__()

        self.angle = math.radians(25)

        self.start = Vector2(
            150,
            250
        )

        self.length = 500

        self.end = Vector2(
            self.start.x
            + math.cos(self.angle) * self.length,
            self.start.y
            + math.sin(self.angle) * self.length
        )

        self.direction = (
            self.end - self.start
        ).normalize()

        self.normal = Vector2(
            self.direction.y,
            -self.direction.x
        )

        self.friction_coefficient = 0.15
        self.static_friction_coefficient = 0.3

        self.body = Body(
            0,
            0,
            20,
            color=self.random_color()
        )

        self.body.linear_damping = 0.0

        plane_position = (
            self.start
            + self.direction * 180
        )

        self.body.position = (
            plane_position
            + self.normal * self.body.radius
        )

        self.world.add_body(
            self.body
        )

    def resolve_plane_contact(self):

        position_from_start = (
            self.body.position
            - self.start
        )

        distance_along_plane = (
            position_from_start.dot(
                self.direction
            )
        )

        distance_along_plane = max(
            0.0,
            min(
                distance_along_plane,
                self.length
            )
        )

        closest_point = (
            self.start
            + self.direction * distance_along_plane
        )

        distance_from_plane = (
            (
                self.body.position
                - closest_point
            ).dot(self.normal)
        )

        penetration = (
            self.body.radius
            - distance_from_plane
        )

        if penetration <= 0:
            return

        self.body.position += (
            self.normal * penetration
        )

        velocity_into_plane = (
            self.body.velocity.dot(self.normal)
        )

        if velocity_into_plane < 0:

            self.body.velocity -= (
                self.normal
                * velocity_into_plane
            )

    def update(self, dt):

        gravity_force = Vector2(
            0,
            self.body.mass * self.world.gravity
        )

        downhill_magnitude = (
            gravity_force.dot(
                self.direction
            )
        )

        normal_gravity_magnitude = (
            gravity_force.dot(
                self.normal
            )
        )

        normal_force_magnitude = abs(
            normal_gravity_magnitude
        )

        speed_along_plane = (
            self.body.velocity.dot(
                self.direction
            )
        )

        max_static_friction = (
            self.static_friction_coefficient
            * normal_force_magnitude
        )

        if (
            abs(speed_along_plane) < 0.01
            and abs(downhill_magnitude)
            <= max_static_friction
        ):

            downhill_force = Vector2()

        else:

            downhill_force = (
                self.direction
                * downhill_magnitude
            )

            friction_magnitude = (
                self.friction_coefficient
                * normal_force_magnitude
            )

            if abs(speed_along_plane) > 0.01:

                friction_direction = -math.copysign(
                    1,
                    speed_along_plane
                )

            else:

                friction_direction = -math.copysign(
                    1,
                    downhill_magnitude
                )

            friction_force = (
                self.direction
                * friction_magnitude
                * friction_direction
            )

            downhill_force += friction_force

        self.body.apply_force(
            downhill_force
        )

        normal_force = (
            self.normal
            * -normal_gravity_magnitude
        )

        self.body.apply_force(
            normal_force
        )

        self.world.update(dt)

        self.resolve_plane_contact()

    def draw(self, renderer):

        self.world.draw(renderer)

        start = renderer.camera.world_to_screen(
            self.start
        )

        end = renderer.camera.world_to_screen(
            self.end
        )

        pygame.draw.line(
            renderer.screen,
            (220, 220, 220),
            (int(start.x), int(start.y)),
            (int(end.x), int(end.y)),
            5
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