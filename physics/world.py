from physics.grid import SpatialGrid


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

            # Force integration
            for body in self.bodies:
                if body.sleeping :
                    continue
                body.gravity = self.gravity
                body.integrate_forces(sub_dt)

            # Constraint solving
            for _ in range(self.constraint_iterations):

                for constraint in self.constraints:
                    constraint.solve()

                self.grid.build(self.bodies)
                self.check_collisions()

            # Position integration
            for body in self.bodies:
                if body.sleeping :
                    continue
                body.integrate_velocity(sub_dt)
                body.solve_floor(self.floor_y)
                body.update_velocity(sub_dt)
                body.clear_forces()
                body.update_sleep(sub_dt)

    def draw(self, renderer):

        for spring in self.springs:
            renderer.draw_spring(spring)

        for body in self.bodies:
            renderer.draw_body(body)

        for constraint in self.constraints:
            renderer.draw_constraint(constraint)

    def check_collisions(self):

        for (cell_x, cell_y), cell in self.grid.cells.items():

            neighbor_bodies = self.grid.get_neighbor_cells(cell_x, cell_y)

            for body1 in cell:

                for body2 in neighbor_bodies:

                    if body1 is body2:
                        continue

                    if id(body1) >= id(body2):
                        continue

                    difference = body2.position - body1.position
                    distance = difference.length()

                    radius_sum = body1.radius + body2.radius

                    if distance < radius_sum:
                        self.resolve_collision(body1, body2)

    def resolve_collision(self, body1, body2):

        difference = body2.position - body1.position
        distance = difference.length()

        if distance == 0:
            return

        radius_sum = body1.radius + body2.radius
        overlap = radius_sum - distance
        correction_percent = 0.2
        slop = 0.01
        corrected_overlap = max(overlap - slop, 0)
        
        collision_normal = difference.normalize()
        correction = collision_normal * (corrected_overlap * correction_percent / 2)

        body1.position -= correction
        body2.position += correction

        relative_velocity = body2.velocity - body1.velocity
        velocity_along_normal = relative_velocity.dot(collision_normal)

        if velocity_along_normal > 0:
            return

        e = min(body1.restitution, body2.restitution)

        j = -(1 + e) * velocity_along_normal
        j /= (1 / body1.mass) + (1 / body2.mass)

        impulse = collision_normal * j

        body1.velocity -= impulse * (1 / body1.mass)
        body2.velocity += impulse * (1 / body2.mass)
        body1.wake()
        body2.wake()
        