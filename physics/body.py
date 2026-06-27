import pygame


class Body:
    def __init__(self, x, y, radius=20):
        self.x = x
        self.y = y

        self.vx = 0
        self.vy = 0

        self.radius = radius

    def update(self, dt):
        gravity = 500

        self.vy += gravity * dt

        self.x += self.vx * dt
        self.y += self.vy * dt