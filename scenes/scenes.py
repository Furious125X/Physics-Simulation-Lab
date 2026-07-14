import random
import pygame

from physics.body import Body
from physics.spring import Spring
from physics.world import World
from physics.constraints import DistanceConstraint
from physics.vector import Vector2


class Scene:

    def __init__(self):
        self.world = World(gravity=500, floor_y=600)
        self.selected_body = None
        self.mouse_stiffness = 40

    def update(self, dt):
        if self.selected_body is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_position = Vector2(mouse_x, mouse_y)

            difference = mouse_position - self.selected_body.position
            force = difference * self.mouse_stiffness
            drag = self.selected_body.velocity * -8

            self.selected_body.apply_force(force)
            self.selected_body.apply_force(drag)

        self.world.update(dt)

    def draw(self, renderer):
        self.world.draw(renderer)

    def handle_event(self, event):
        pass

    def find_body_at_position(self, position):
        for body in self.world.bodies:
            difference = position - body.position

            if difference.length_squared() <= body.radius ** 2:
                return body

        return None

    @staticmethod
    def random_color():
        return (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )


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

        ball3 = Body(
            500,
            150,
            20,
            color=self.random_color()
        )

        ball3anchor = Vector2(400, 150)

        ball3constraint = DistanceConstraint(
            ball3,
            ball3anchor,
            100
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
        self.world.add_body(ball3)

        self.world.add_spring(spring)
        self.world.add_constraint(ball3constraint)

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_position = Vector2(mouse_x, mouse_y)

            self.selected_body = self.find_body_at_position(mouse_position)

        elif event.type == pygame.MOUSEBUTTONUP:

            self.selected_body = None

        elif event.type == pygame.MOUSEWHEEL:

            mouse_x, mouse_y = pygame.mouse.get_pos()

            body = Body(
                mouse_x,
                mouse_y,
                random.randint(10, 40),
                color=self.random_color()
            )

            self.world.add_body(body)


class CollisionScene(Scene):

    def __init__(self):

        super().__init__()

        for _ in range(30):

            body = Body(
                random.randint(50, 750),
                random.randint(50, 550),
                random.randint(8, 30),
                color=self.random_color()
            )

            body.velocity.x = random.randint(-200, 200)
            body.velocity.y = random.randint(-100, 100)

            self.world.add_body(body)

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_position = Vector2(mouse_x, mouse_y)

            self.selected_body = self.find_body_at_position(mouse_position)

        elif event.type == pygame.MOUSEBUTTONUP:

            self.selected_body = None

        elif event.type == pygame.MOUSEWHEEL:

            mouse_x, mouse_y = pygame.mouse.get_pos()

            body = Body(
                mouse_x,
                mouse_y,
                random.randint(10, 40),
                color=self.random_color()
            )

            self.world.add_body(body)


class NewtonCradleScene(Scene):

    def __init__(self):

        super().__init__()

        ball_count = 5
        radius = 18
        spacing = radius * 2
        rope_length = 150

        start_x = 300
        anchor_y = 100

        self.first_ball = None

        for i in range(ball_count):

            anchor = Vector2(
                start_x + i * spacing,
                anchor_y
            )

            ball = Body(
                anchor.x,
                anchor.y + rope_length,
                radius,
                color=self.random_color()
            )

            constraint = DistanceConstraint(
                ball,
                anchor,
                rope_length
            )

            self.world.add_body(ball)
            self.world.add_constraint(constraint)

            if i == 0:
                self.first_ball = ball

        # Pull the first ball back so it starts swinging
        self.first_ball.position.x -= 120