import random
import pygame

from physics.body import Body
from physics.vector import Vector2

from scenes.base_scene import Scene


class WaterScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 550

        self.source_x = 400
        self.source_y = 100

        self.spawn_timer = 0.0
        self.spawn_interval = 0.1

        self.particle_lifetime = 2.0

        self.particle_radius = 5
        self.particle_density = 0.05

        self.interaction_radius = 35.0

        self.target_density = 3.5
        self.pressure_strength = 60.0
        self.cohesion_strength = 5.0
        self.viscosity = 2.5

        self.max_fluid_force = 100.0
        self.max_particle_speed = 600.0

        self.particles = []

        self.densities = {}
        self.pressures = {}

        self.average_density = 0.0

    def spawn_particle(self):

        particle = Body(
            self.source_x + random.uniform(-12, 12),
            self.source_y + random.uniform(-4, 4),
            self.particle_radius,
            density=self.particle_density,
            color=(70, 160, 255)
        )

        particle.is_fluid = True

        particle.velocity = Vector2(
            random.uniform(-20, 20),
            random.uniform(20, 50)
        )

        particle.linear_damping = 0.05
        particle.restitution = 0.0
        particle.static_friction = 0.3
        particle.dynamic_friction = 0.2

        particle.lifetime = 0.0

        self.particles.append(particle)
        self.world.add_body(particle)

    def update_spawning(self, dt):

        self.spawn_timer += dt

        while self.spawn_timer >= self.spawn_interval:

            self.spawn_particle()

            self.spawn_timer -= self.spawn_interval

    def update_particles(self, dt):

        for particle in self.particles:
            particle.lifetime += dt

    def get_neighbors(self, particle):

        cell_x = int(
            particle.position.x
            // self.world.grid.cell_size
        )

        cell_y = int(
            particle.position.y
            // self.world.grid.cell_size
        )

        neighbors = []

        for other in self.world.grid.get_neighbor_cells(
            cell_x,
            cell_y
        ):

            if other is particle:
                continue

            if not getattr(other, "is_fluid", False):
                continue

            difference = (
                particle.position
                - other.position
            )

            distance_squared = (
                difference.length_squared()
            )

            if (
                distance_squared
                < self.interaction_radius
                * self.interaction_radius
            ):
                neighbors.append(other)

        return neighbors

    def calculate_density(
        self,
        particle,
        neighbors
    ):

        density = 0.0

        for neighbor in neighbors:

            difference = (
                particle.position
                - neighbor.position
            )

            distance = difference.length()

            if distance >= self.interaction_radius:
                continue

            influence = (
                1.0
                - distance / self.interaction_radius
            )

            density += influence * influence

        return density

    def calculate_fluid_state(self):

        self.densities = {}
        self.pressures = {}

        if not self.particles:

            self.average_density = 0.0
            return

        self.world.grid.build(
            self.particles
        )

        density_total = 0.0

        for particle in self.particles:

            neighbors = self.get_neighbors(
                particle
            )

            density = self.calculate_density(
                particle,
                neighbors
            )

            self.densities[particle] = density

            pressure = (
                self.pressure_strength
                * max(
                    density - self.target_density,
                    0.0
                )
            )

            self.pressures[particle] = pressure

            density_total += density

        self.average_density = (
            density_total
            / len(self.particles)
        )

    def apply_fluid_forces(self):

        if not self.particles:
            return

        force_scale = self.world.substeps

        for particle in self.particles:

            neighbors = self.get_neighbors(
                particle
            )

            pressure = self.pressures[particle]

            force = Vector2()

            for neighbor in neighbors:

                difference = (
                    particle.position
                    - neighbor.position
                )

                distance_squared = (
                    difference.length_squared()
                )

                if distance_squared == 0:
                    continue

                distance = (
                    distance_squared ** 0.5
                )

                direction = (
                    difference
                    / distance
                )

                influence = (
                    1.0
                    - distance / self.interaction_radius
                )

                neighbor_pressure = (
                    self.pressures[neighbor]
                )

                average_pressure = (
                    pressure
                    + neighbor_pressure
                ) * 0.5

                pressure_force = (
                    direction
                    * (
                        average_pressure
                        * influence
                        / self.target_density
                    )
                )

                force += pressure_force

                relative_velocity = (
                    neighbor.velocity
                    - particle.velocity
                )

                viscosity_force = (
                    relative_velocity
                    * (
                        self.viscosity
                        * influence
                    )
                )

                force += viscosity_force

                if distance < self.particle_radius * 2.5:

                    closeness = (
                        1.0
                        - (
                            distance
                            / (self.particle_radius * 2.5)
                        )
                    )

                    cohesion_force = (
                        direction
                        * (
                            -self.cohesion_strength
                            * closeness
                        )
                    )

                    force += cohesion_force

            force_length = force.length()

            if force_length > self.max_fluid_force:

                force = (
                    force.normalize()
                    * self.max_fluid_force
                )

            particle.apply_force(
                force * force_scale
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

            self.particles.remove(
                particle
            )

            self.world.bodies.remove(
                particle
            )

    def update(self, dt):

        self.update_spawning(dt)
        self.update_particles(dt)

        self.calculate_fluid_state()
        self.apply_fluid_forces()

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
            (
                f"Particles: {len(self.particles)}  "
                f"Density: {self.average_density:.2f}"
            ),
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )