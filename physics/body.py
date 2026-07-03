import pygame
from physics.vector import Vector2
import math

class Body:
    def __init__(self, x, y, radius=20, density=0.002, color=(255,255,255)):
        self.position = Vector2(x, y)
        self.velocity = Vector2()
        self.mass = density * math.pi * radius * radius
        self.radius = radius
        self.color = color

        self.gravity = 500
        self.restitution = 0.8  # bounce energy loss

    def update(self, dt, floor_y):
        # 1. Apply gravity
        self.velocity.y += self.gravity * dt

       # 2. Move
        self.position += self.velocity * dt

        # 3. Collision with floor
        if self.position.y + self.radius > floor_y:
            self.position.y = floor_y - self.radius  # reset position

            self.velocity.y = -self.velocity.y * self.restitution  # bounce

            # stop tiny jittering
            if abs(self.velocity.y) < 10:
                self.velocity.y = 0
        
        