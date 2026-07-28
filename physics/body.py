from physics.vector import Vector2
import math


class Body:

    def __init__(self, x, y, radius=20, density=0.002, color=(255, 255, 255), is_static=False):
        self.position = Vector2(x, y)
        self.previous_position = self.position.copy()
        self.velocity = Vector2()

        self.is_static = is_static

        self.mass = density * math.pi * radius * radius
        if self.is_static:
            self.mass = float("inf")

        if self.mass == float("inf"):
            self.inverse_mass = 0
        else:
            self.inverse_mass = 1 / self.mass

        if self.is_static:
            self.inertia = float("inf")
            self.inverse_inertia = 0
        else:
            self.inertia = 0.5 * self.mass * radius * radius
            self.inverse_inertia = 1 / self.inertia

        self.radius = radius
        self.color = color

        self.force = Vector2()
        self.angle = 0.0
        self.angular_velocity = 0.0
        self.torque = 0.0

        self.gravity = 500

        self.restitution = 0.8
        self.static_friction = 0.6
        self.dynamic_friction = 0.4
        self.linear_damping = 2

        self.sleeping = self.is_static
        self.sleep_timer = 0
        self.sleep_velocity = 5
        self.sleep_angular_velocity = 1.0
        self.sleep_time = 0.5

        self.hit_floor = False

    def integrate_forces(self, dt):
        gravity_force = Vector2(0, self.mass * self.gravity)
        self.apply_force(gravity_force)

        damping_force = -self.velocity * self.linear_damping
        self.apply_force(damping_force)

        acceleration = self.force / self.mass
        self.velocity += acceleration * dt

        angular_acceleration = self.torque * self.inverse_inertia
        self.angular_velocity += angular_acceleration * dt

    def integrate_velocity(self, dt):
        self.previous_position = self.position.copy()
        self.position += self.velocity * dt
        self.angle += self.angular_velocity * dt

    def solve_floor(self, floor_y):
        if self.position.y + self.radius > floor_y:
            self.position.y = floor_y - self.radius
            self.velocity.y = -self.velocity.y * self.restitution
            self.hit_floor = True

            if abs(self.velocity.y) < 10:
                self.velocity.y = 0

    def update_velocity(self, dt):
        new_velocity = (self.position - self.previous_position) / dt

        self.velocity.x = new_velocity.x

        if not self.hit_floor:
            self.velocity.y = new_velocity.y

    def clear_forces(self):
        self.force = Vector2()
        self.torque = 0.0

    def apply_force(self, force):
        if force.length_squared() > 0:
            self.wake()

        self.force += force

    def apply_torque(self, torque):
        if torque != 0:
            self.wake()

        self.torque += torque

    def apply_impulse(self, impulse, contact_vector=None):
        if self.is_static:
            return

        if impulse.length_squared() > 0:
            self.wake()

        self.velocity += impulse * self.inverse_mass

        if contact_vector is not None:
            self.angular_velocity += self.cross_2d(contact_vector, impulse) * self.inverse_inertia

    @staticmethod
    def cross_2d(a, b):
        return a.x * b.y - a.y * b.x

    def get_contact_velocity(self, contact_vector):
        rotational_velocity = Vector2(
            -self.angular_velocity * contact_vector.y,
            self.angular_velocity * contact_vector.x
        )
        return self.velocity + rotational_velocity

    def wake(self):
        if self.is_static:
            return
        self.sleeping = False
        self.sleep_timer = 0

    def update_sleep(self, dt):
        if self.is_static or self.sleeping:
            return

        if self.velocity.length() < self.sleep_velocity and abs(self.angular_velocity) < self.sleep_angular_velocity:
            self.sleep_timer += dt

            if self.sleep_timer >= self.sleep_time:
                self.sleeping = True
                self.velocity = Vector2()
                self.angular_velocity = 0.0
        else:
            self.wake()