import random
import pygame

from physics.body import Body
from physics.vector import Vector2

from scenes.base_scene import Scene


class SandScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 550

        self.source_x = 400
        self.source_y = 80
        self.source_width = 12

        self.spawn_timer = 0.0
        self.spawn_interval = 0.1

        self.max_particles = 50

        self.particle_radius = 5
        self.particle_density = 0.02

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
                random.randint(180, 230),
                random.randint(140, 190),
                random.randint(70, 120)
            )
        )

        particle.velocity = Vector2(
            random.uniform(-10, 10),
            random.uniform(0, 20)
        )

        particle.linear_damping = 0.15
        particle.restitution = 0.0
        particle.static_friction = 0.8
        particle.dynamic_friction = 0.7

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

    def update(self, dt):

        self.update_spawning(dt)

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

        text = renderer.font.render(
            f"Grains: {len(self.particles)} / {self.max_particles}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )

