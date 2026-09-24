import math
import random
import pygame

from physics.body import Body
from physics.vector import Vector2

from scenes.base_scene import Scene


class SmokeScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 550

        self.source_x = 400
        self.source_y = 500
        self.source_width = 24

        self.spawn_timer = 0.0
        self.spawn_interval = 0.06

        self.particle_lifetime = 5.0
        self.max_particles = 100

        self.particle_radius = 7
        self.particle_density = 0.01

        self.buoyancy = 650.0
        self.turbulence_strength = 45.0
        self.turbulence_frequency = 1.5

        self.max_particle_speed = 350.0

        self.particles = []

    def spawn_particle(self):

        if len(self.particles) >= self.max_particles:
            return

        particle = Body(
            self.source_x
            + random.uniform(
                -self.source_width / 2,
                self.source_width / 2
            ),
            self.source_y
            + random.uniform(
                -3,
                3
            ),
            self.particle_radius,
            density=self.particle_density,
            color=(
                random.randint(170, 200),
                random.randint(170, 200),
                random.randint(170, 200)
            )
        )

        particle.is_fluid = True
        particle.lifetime = 0.0
        particle.smoke_phase = random.uniform(
            0,
            2 * math.pi
        )

        particle.velocity = Vector2(
            random.uniform(-15, 15),
            random.uniform(-20, 10)
        )

        particle.linear_damping = 0.25
        particle.restitution = 0.0
        particle.static_friction = 0.0
        particle.dynamic_friction = 0.0

        self.particles.append(particle)
        self.world.add_body(particle)

    def update_spawning(self, dt):

        if len(self.particles) >= self.max_particles:
            return

        self.spawn_timer += dt

        while self.spawn_timer >= self.spawn_interval:

            self.spawn_particle()

            self.spawn_timer -= self.spawn_interval

            if len(self.particles) >= self.max_particles:
                break

    def update_particles(self, dt):

        for particle in self.particles:

            particle.lifetime += dt

            age_ratio = (
                particle.lifetime
                / self.particle_lifetime
            )

            turbulence = math.sin(
                particle.lifetime
                * self.turbulence_frequency
                + particle.smoke_phase
            )

            buoyancy_force = Vector2(
                0,
                -particle.mass * self.buoyancy
            )

            turbulence_force = Vector2(
                turbulence
                * particle.mass
                * self.turbulence_strength,
                0
            )

            force = (
                buoyancy_force
                + turbulence_force
            )

            particle.apply_force(
                force * self.world.substeps
            )

            particle.color = (
                int(190 - 120 * age_ratio),
                int(190 - 120 * age_ratio),
                int(190 - 120 * age_ratio)
            )

    def limit_particle_speed(self):

        max_speed_squared = (
            self.max_particle_speed
            * self.max_particle_speed
        )

        for particle in self.particles:

            speed_squared = (
                particle.velocity.length_squared()
            )

            if speed_squared > max_speed_squared:

                particle.velocity = (
                    particle.velocity.normalize()
                    * self.max_particle_speed
                )

    def remove_expired_particles(self):

        expired_particles = []

        for particle in self.particles:

            if particle.lifetime >= self.particle_lifetime:
                expired_particles.append(particle)

        for particle in expired_particles:

            if self.selected_body is particle:
                self.selected_body = None

            self.particles.remove(particle)
            self.world.bodies.remove(particle)

    def update(self, dt):

        self.update_spawning(dt)
        self.update_particles(dt)

        super().update(dt)

        self.limit_particle_speed()
        self.remove_expired_particles()

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
            f"Smoke: {len(self.particles)} / {self.max_particles}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )