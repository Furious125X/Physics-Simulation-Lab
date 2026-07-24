from physics.grid import SpatialGrid
import random


class World:

    def __init__(self, gravity=500, floor_y=600):
        self.gravity = gravity
        self.floor_y = floor_y

        self.bodies = []
        self.springs = []
        self.constraints = []

        self.grid = SpatialGrid(100)

        self.constraint_iterations = 10
        self.substeps = 4
        self.reverse_solver = False

        # Lets cloth/other scenes disable expensive body-body collisions
        self.enable_collisions = True

    def add_body(self, body):
        self.bodies.append(body)

    def add_spring(self, spring):
        self.springs.append(spring)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def update(self, dt):
        sub_dt = dt / self.substeps

        for _ in range(self.substeps):

            # Spring forces
            for spring in self.springs:
                spring.update()

            # Force integration + predicted positions
            for body in self.bodies:
                if body.sleeping or body.is_static:
                    continue
                body.gravity = self.gravity
                body.integrate_forces(sub_dt)
                body.integrate_velocity(sub_dt)

            # Constraint solving
            for _ in range(self.constraint_iterations):
                if len(self.constraints) > 1:
                    random.shuffle(self.constraints)

                for constraint in self.constraints:
                    constraint.solve()

                for body in self.bodies:
                    if body.sleeping or body.is_static:
                        continue
                    body.solve_floor(self.floor_y)

            # Body-body collisions only when enabled
            if self.enable_collisions:
                self.grid.build(self.bodies)
                self.check_collisions()

                # Floor again after collisions so objects don't get pushed through it
                for body in self.bodies:
                    if body.sleeping or body.is_static:
                        continue
                    body.solve_floor(self.floor_y)

            # Reconstruct velocity / cleanup
            for body in self.bodies:
                if body.sleeping or body.is_static:
                    continue
                body.update_velocity(sub_dt)
                body.clear_forces()
                body.update_sleep(sub_dt)

            self.reverse_solver = not self.reverse_solver

    def draw(self, renderer):
        for spring in self.springs:
            renderer.draw_spring(spring)

        for body in self.bodies:
            renderer.draw_body(body)

        for constraint in self.constraints:
            renderer.draw_constraint(constraint)

    def check_collisions(self):
        cells = list(self.grid.cells.items())

        if self.reverse_solver:
            cells.reverse()

        for (cell_x, cell_y), cell in cells:
            neighbor_bodies = self.grid.get_neighbor_cells(cell_x, cell_y)

            for body1 in cell:
                for body2 in neighbor_bodies:
                    if body1 is body2:
                        continue

                    if body1.sleeping and body2.sleeping:
                        continue

                    if id(body1) >= id(body2):
                        continue

                    difference = body2.position - body1.position
                    distance = difference.length()
                    radius_sum = body1.radius + body2.radius

                    if distance < radius_sum:
                        self.resolve_collision(body1, body2)

    def resolve_collision(self, body1, body2):
        if body1.is_static and body2.is_static:
            return

        difference = body2.position - body1.position
        distance = difference.length()
        radius_sum = body1.radius + body2.radius

        relative_velocity = body2.velocity - body1.velocity

        if distance == 0:
            if relative_velocity.length_squared() == 0:
                return
            collision_normal = relative_velocity.normalize()
        else:
            collision_normal = difference / distance

        overlap = radius_sum - distance
        correction_percent = 0.2
        slop = 0.01
        corrected_overlap = max(overlap - slop, 0)

        total_inverse_mass = body1.inverse_mass + body2.inverse_mass
        if total_inverse_mass == 0:
            return

        correction = collision_normal * (corrected_overlap * correction_percent)

        body1.position -= correction * (body1.inverse_mass / total_inverse_mass)
        body2.position += correction * (body2.inverse_mass / total_inverse_mass)

        relative_velocity = body2.velocity - body1.velocity
        velocity_along_normal = relative_velocity.dot(collision_normal)

        if velocity_along_normal > 0:
            return

        e = min(body1.restitution, body2.restitution)

        j = -(1 + e) * velocity_along_normal
        j /= total_inverse_mass

        impulse = collision_normal * j

        body1.velocity -= impulse * body1.inverse_mass
        body2.velocity += impulse * body2.inverse_mass

        body1.wake()
        body2.wake()