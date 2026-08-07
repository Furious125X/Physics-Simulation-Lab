from physics.grid import SpatialGrid
from physics.vector import Vector2
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

        self.enable_collisions = True

        self.resting_velocity_threshold = 5.0

        self.collision_iterations = 4

    def add_body(self, body):
        self.bodies.append(body)

    def add_spring(self, spring):
        self.springs.append(spring)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def update(self, dt):
        sub_dt = dt / self.substeps

        for _ in range(self.substeps):

            for body in self.bodies:
                body.hit_floor = False
                body.impulse_velocity_delta = Vector2()

            for spring in self.springs:
                spring.update()

            for body in self.bodies:
                if body.sleeping or body.is_static:
                    continue
                body.gravity = self.gravity
                body.integrate_forces(sub_dt)
                body.integrate_velocity(sub_dt)
                self.sweep_floor_contact(body)

            for constraint in self.constraints:
                constraint.begin_substep()

            for _ in range(self.constraint_iterations):
                if len(self.constraints) > 1:
                    random.shuffle(self.constraints)

                for constraint in self.constraints:
                    constraint.solve(sub_dt)

                for body in self.bodies:
                    if body.sleeping or body.is_static:
                        continue
                    self.resolve_floor_contact(body)

            self.grid.build(self.bodies)
            contacts = self.check_collisions()

            for _ in range(self.collision_iterations):
                for body1, body2 in contacts:
                    self.resolve_collision(body1, body2)

                for body in self.bodies:
                    if body.sleeping or body.is_static:
                        continue
                    self.resolve_floor_contact(body)


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
        contacts = []

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
                        contacts.append((body1, body2))

        return contacts

    def resolve_collision(self, body1, body2):
        if body1.is_static and body2.is_static:
            return

        difference = body2.position - body1.position
        distance = difference.length()
        radius_sum = body1.radius + body2.radius

        if distance == 0:
            relative_velocity = body2.velocity - body1.velocity
            if relative_velocity.length_squared() == 0:
                collision_normal = Vector2(1, 0)
            else:
                collision_normal = relative_velocity.normalize()
        else:
            collision_normal = difference / distance

        overlap = radius_sum - distance
        if overlap <= 0:
            return

        inv_mass1 = body1.inverse_mass
        inv_mass2 = body2.inverse_mass
        total_inverse_mass = inv_mass1 + inv_mass2
        if total_inverse_mass == 0:
            return

        correction_percent = 0.2
        slop = 0.01
        corrected_overlap = max(overlap - slop, 0)

        correction = collision_normal * (corrected_overlap * correction_percent)

        body1.position -= correction * (inv_mass1 / total_inverse_mass)
        body2.position += correction * (inv_mass2 / total_inverse_mass)

        ra = collision_normal * body1.radius
        rb = -collision_normal * body2.radius

        velocity_a = body1.get_contact_velocity(ra)
        velocity_b = body2.get_contact_velocity(rb)
        relative_velocity = velocity_b - velocity_a

        velocity_along_normal = relative_velocity.dot(collision_normal)
        if velocity_along_normal > 0:
            return

        ra_cross_n = body1.cross_2d(ra, collision_normal)
        rb_cross_n = body2.cross_2d(rb, collision_normal)

        normal_denominator = (
            inv_mass1
            + inv_mass2
            + (ra_cross_n * ra_cross_n) * body1.inverse_inertia
            + (rb_cross_n * rb_cross_n) * body2.inverse_inertia
        )

        if normal_denominator == 0:
            return

        if abs(velocity_along_normal) < self.resting_velocity_threshold:
            e = 0.0
        else:
            e = min(body1.restitution, body2.restitution)

        j = -(1 + e) * velocity_along_normal
        j /= normal_denominator

        impulse = collision_normal * j
        body1.apply_impulse(-impulse, ra)
        body2.apply_impulse(impulse, rb)

        velocity_a = body1.get_contact_velocity(ra)
        velocity_b = body2.get_contact_velocity(rb)
        relative_velocity = velocity_b - velocity_a

        tangent = relative_velocity - collision_normal * relative_velocity.dot(collision_normal)
        if tangent.length_squared() < 1e-8:
            body1.wake()
            body2.wake()
            return

        tangent = tangent.normalize()

        ra_cross_t = body1.cross_2d(ra, tangent)
        rb_cross_t = body2.cross_2d(rb, tangent)

        friction_denominator = (
            inv_mass1
            + inv_mass2
            + (ra_cross_t * ra_cross_t) * body1.inverse_inertia
            + (rb_cross_t * rb_cross_t) * body2.inverse_inertia
        )

        if friction_denominator == 0:
            body1.wake()
            body2.wake()
            return

        jt = -relative_velocity.dot(tangent)
        jt /= friction_denominator

        mu_static = (body1.static_friction + body2.static_friction) / 2
        mu_dynamic = (body1.dynamic_friction + body2.dynamic_friction) / 2

        if abs(jt) < j * mu_static:
            friction_impulse = tangent * jt
        else:
            friction_impulse = tangent * (-j * mu_dynamic)

        body1.apply_impulse(-friction_impulse, ra)
        body2.apply_impulse(friction_impulse, rb)

        body1.wake()
        body2.wake()

    def resolve_floor_contact(self, body, assume_contact=False):
        penetration = (body.position.y + body.radius) - self.floor_y

        if not assume_contact and penetration <= 0:
            return
        
        if penetration <= 0:
            return

        body.hit_floor = True
        body.position.y -= penetration

        normal = Vector2(0, -1)
        ra = Vector2(0, body.radius)

        contact_velocity = body.get_contact_velocity(ra)
        velocity_along_normal = contact_velocity.dot(normal)

        if velocity_along_normal > 0:
            return

        ra_cross_n = body.cross_2d(ra, normal)
        normal_denominator = body.inverse_mass + (ra_cross_n * ra_cross_n) * body.inverse_inertia
        if normal_denominator == 0:
            return

        if abs(velocity_along_normal) < self.resting_velocity_threshold:
            restitution = 0.0
        else:
            restitution = body.restitution

        j = -(1 + restitution) * velocity_along_normal
        j /= normal_denominator

        impulse = normal * j
        body.apply_impulse(impulse, ra)

        if abs(body.velocity.y) < 0.1:
            body.velocity.y = 0.0

        contact_velocity = body.get_contact_velocity(ra)
        tangent = contact_velocity - normal * contact_velocity.dot(normal)

        if tangent.length_squared() < 1e-8:
            return

        tangent = tangent.normalize()

        ra_cross_t = body.cross_2d(ra, tangent)
        friction_denominator = body.inverse_mass + (ra_cross_t * ra_cross_t) * body.inverse_inertia
        if friction_denominator == 0:
            return

        jt = -contact_velocity.dot(tangent)
        jt /= friction_denominator

        if abs(jt) < j * body.static_friction:
            friction_impulse = tangent * jt
        else:
            friction_impulse = tangent * (-j * body.dynamic_friction)

        body.apply_impulse(friction_impulse, ra)

    def sweep_floor_contact(self, body):
        previous_bottom = body.previous_position.y + body.radius
        current_bottom = body.position.y + body.radius

        if previous_bottom < self.floor_y and current_bottom >= self.floor_y:
            delta_bottom = current_bottom - previous_bottom

            if delta_bottom == 0:
                return

            t = (self.floor_y - previous_bottom) / delta_bottom

            if t < 0.0 or t > 1.0:
                return

            move = body.position - body.previous_position
            body.position = body.previous_position + move * t

            body.position.y = self.floor_y - body.radius

            body.hit_floor = True

            self.resolve_floor_contact(body, assume_contact=True)


    