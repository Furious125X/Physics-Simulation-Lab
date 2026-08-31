import math
import pygame

from physics.body import Body
from physics.vector import Vector2

from scenes.base_scene import Scene


class OrbitalMechanicsScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 0
        self.world.floor_y = 10000
        self.world.substeps = 1

        self.gravitational_constant = 1500

        self.pulley = None

        self.central_position = Vector2(
            400,
            300
        )

        self.central_radius = 45

        self.central_mass = 100.0

        self.orbit_radius = 180

        self.central_body = Body(
            self.central_position.x,
            self.central_position.y,
            self.central_radius,
            density=0.05,
            color=(220, 180, 80),
            is_static=True
        )

        self.orbiting_body = Body(
            self.central_position.x,
            self.central_position.y - self.orbit_radius,
            12,
            density=0.002,
            color=self.random_color()
        )

        self.orbiting_body.linear_damping = 0.0

        self.world.add_body(
            self.central_body
        )

        self.world.add_body(
            self.orbiting_body
        )

        orbital_speed = math.sqrt(
            self.gravitational_constant
            * self.central_mass
            / self.orbit_radius
        )

        self.orbiting_body.velocity = Vector2(
            orbital_speed,
            0
        )

    def apply_gravity(self):

        difference = (
            self.central_body.position
            - self.orbiting_body.position
        )

        distance_squared = (
            difference.length_squared()
        )

        if distance_squared <= 0:
            return

        distance = math.sqrt(
            distance_squared
        )

        direction = (
            difference / distance
        )

        force_magnitude = (
            self.gravitational_constant
            * self.central_mass
            * self.orbiting_body.mass
            / distance_squared
        )

        force = (
            direction
            * force_magnitude
        )

        self.orbiting_body.apply_force(
            force
        )

    def update(self, dt):

        self.apply_gravity()

        self.world.update(dt)

    def draw(self, renderer):

        self.world.draw(renderer)

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