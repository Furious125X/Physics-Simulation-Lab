from physics.vector import Vector2
import math


class Body:

    def __init__(self, x, y, radius=20, density=0.002, color=(255, 255, 255)):
        self.position = Vector2(x, y)
        self.previous_position = self.position.copy()
        self.velocity = Vector2()

        self.mass = density * math.pi * radius * radius

        self.radius = radius
        self.color = color

        self.force = Vector2()

        self.gravity = 500

        self.restitution = 0.8
        self.linear_damping = 2

        self.sleeping = False
        self.sleep_timer = 0
        self.sleep_velocity = 5
        self.sleep_time = 0.5

        self.hit_floor = False

    def integrate_forces(self, dt):

        gravity_force = Vector2(0, self.mass * self.gravity)
        self.apply_force(gravity_force)

        damping_force = -self.velocity * self.linear_damping
        self.apply_force(damping_force)

        acceleration = self.force / self.mass
        self.velocity += acceleration * dt

    def integrate_velocity(self, dt):
        self.previous_position = self.position.copy()
        self.position += self.velocity * dt

    def solve_floor(self, floor_y):

        self.hit_floor = False

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

    def apply_force(self, force):
        self.force += force

    def wake(self):
        self.sleeping = False
        self.sleep_timer = 0

    def update_sleep(self, dt):

        if self.velocity.length() < self.sleep_velocity:

            self.sleep_timer += dt

            if self.sleep_timer >= self.sleep_time:
                self.sleeping = True
                self.velocity = Vector2()

        else:
            self.wake()