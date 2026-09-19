import random
import pygame

from physics.body import Body
from physics.vector import Vector2

from scenes.base_scene import Scene


class ParticleFountainScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 550

        self.fountain_x = 400
        self.fountain_y = 500
        self.spawn_offset = 10
        self.offset_positive = True

        self.spawn_timer = 0.0
        self.spawn_interval = 0.2

        self.particles = []

        self.particle_lifetime = 2.0

    def spawn_particle(self):
        offset = self.spawn_offset if self.offset_positive else -self.spawn_offset
        self.offset_positive = not self.offset_positive
        
        particle = Body(
            self.fountain_x + offset,
            self.fountain_y,
            20,
            density=0.001,
            color=self.random_color()
        )

        particle.velocity = Vector2(
            random.uniform(-80, 80),
            random.uniform(-650, -550)
        )

        particle.linear_damping = 0.0
        particle.restitution = 0.4
        particle.static_friction = 0.2
        particle.dynamic_friction = 0.1
        particle.lifetime = 0.0

        self.particles.append(particle)

        self.world.add_body(particle)


    def update_particles(self, dt):

        for particle in self.particles:
            particle.lifetime += dt

    def update_spawning(self, dt):

        self.spawn_timer += dt

        while self.spawn_timer >= self.spawn_interval:

            self.spawn_particle()

            self.spawn_timer -= self.spawn_interval


    def update(self, dt):

        self.update_spawning(dt)
        self.update_particles(dt)

        super().update(dt)

        self.remove_expired_particles()


    def remove_expired_particles(self):

        expired_particles = []

        for particle in self.particles:

            if particle.lifetime >= self.particle_lifetime:
                expired_particles.append(particle)

        for particle in expired_particles:

            self.particles.remove(particle)
            self.world.bodies.remove(particle)


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
            f"Particles: {len(self.particles)}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
    )