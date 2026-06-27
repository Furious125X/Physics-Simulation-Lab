import pygame


class Body:
    def __init__(self, x, y, radius=20):
        self.x = x
        self.y = y

        self.vx = 0
        self.vy = 0

        self.radius = radius

        self.gravity = 500
        self.restitution = 0.8  # bounce energy loss

    def update(self, dt, floor_y):
        # 1. Apply gravity
        self.vy += self.gravity * dt

        # 2. Move
        self.x += self.vx * dt
        self.y += self.vy * dt

        # 3. Collision with floor
        if self.y + self.radius > floor_y:
            self.y = floor_y - self.radius  # reset position

            self.vy = -self.vy * self.restitution  # bounce

            # stop tiny jittering
            if abs(self.vy) < 10:
                self.vy = 0