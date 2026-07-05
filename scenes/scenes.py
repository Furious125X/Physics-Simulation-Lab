import random
import pygame

from physics.body import Body
from physics.spring import Spring
from physics.world import World


class Scene:

    def __init__(self):

        self.world = World(
            gravity=500,
            floor_y=600
        )

    def update(self, dt):
        self.world.update(dt)

    def draw(self, renderer):
        self.world.draw(renderer)

    def handle_event(self, event):
        pass


class SpringScene(Scene):

    def __init__(self):

        super().__init__()

        ball1 = Body(
            500,
            100,
            20,
            color=self.random_color()
        )

        ball2 = Body(
            650,
            100,
            35,
            color=self.random_color()
        )

        spring = Spring(
            ball1,
            ball2,
            rest_length=150,
            stiffness=5
        )

        ball1.velocity.x = 250

        self.world.add_body(ball1)
        self.world.add_body(ball2)
        self.world.add_spring(spring)

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = pygame.mouse.get_pos()

            body = Body(
                mouse_x,
                mouse_y,
                random.randint(10, 40),
                color=self.random_color()
            )

            self.world.add_body(body)

    @staticmethod
    def random_color():
        return (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )