import random
import pygame

from physics.vector import Vector2
from physics.world import World


class Scene:

    def __init__(self):
        self.selected_body = None
        self.mouse_stiffness = 40
        self.setup()

    def setup(self):
        self.world = World(
            gravity=500,
            floor_y=600
        )

    def reset(self):
        self.setup()
        self.selected_body = None
        pass

    def update(self, dt):
        if self.selected_body is not None:

            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_position = Vector2(
                mouse_x,
                mouse_y
            )

            difference = (
                mouse_position
                - self.selected_body.position
            )

            force = difference * self.mouse_stiffness

            drag = (
                self.selected_body.velocity
                * -8
            )

            self.selected_body.wake()
            self.selected_body.apply_force(force)
            self.selected_body.apply_force(drag)

        self.world.update(dt)

    def draw(self, renderer):
        self.world.draw(renderer)

    def handle_event(self, event):
        pass

    def find_body_at_position(self, position):

        for body in self.world.bodies:

            difference = (
                position
                - body.position
            )

            if (
                difference.length_squared()
                <= body.radius ** 2
            ):
                return body

        return None

    @staticmethod
    def random_color():
        return (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )