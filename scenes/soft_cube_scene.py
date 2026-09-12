import pygame

from physics.body import Body
from physics.constraints import DistanceConstraint
from physics.vector import Vector2

from scenes.base_scene import Scene


class SoftCubeScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 550

        self.grid_size = 5
        self.spacing = 35
        self.radius = 8

        self.start_x = 320
        self.start_y = 120

        self.bodies = []
        self.grid = {}

        for y in range(self.grid_size):

            for x in range(self.grid_size):

                body = Body(
                    self.start_x + x * self.spacing,
                    self.start_y + y * self.spacing,
                    self.radius,
                    color=self.random_color()
                )

                body.linear_damping = 0.5
                body.restitution = 0.0
                body.static_friction = 0.6
                body.dynamic_friction = 0.4

                self.bodies.append(body)
                self.world.add_body(body)

                self.grid[(x, y)] = body

        self.add_structural_constraints()
        self.add_shear_constraints()
        self.add_bending_constraints()

    def add_constraint(
        self,
        body1,
        body2,
        length,
        compliance
    ):

        constraint = DistanceConstraint(
            body1,
            body2,
            length,
            compliance=compliance
        )

        self.world.add_constraint(constraint)

    def add_structural_constraints(self):

        for y in range(self.grid_size):

            for x in range(self.grid_size):

                current = self.grid[(x, y)]

                if x < self.grid_size - 1:

                    right = self.grid[(x + 1, y)]

                    self.add_constraint(
                        current,
                        right,
                        self.spacing,
                        0.00001
                    )

                if y < self.grid_size - 1:

                    below = self.grid[(x, y + 1)]

                    self.add_constraint(
                        current,
                        below,
                        self.spacing,
                        0.00001
                    )

    def add_shear_constraints(self):

        diagonal_length = self.spacing * (2 ** 0.5)

        for y in range(self.grid_size - 1):

            for x in range(self.grid_size - 1):

                top_left = self.grid[(x, y)]
                top_right = self.grid[(x + 1, y)]
                bottom_left = self.grid[(x, y + 1)]
                bottom_right = self.grid[(x + 1, y + 1)]

                self.add_constraint(
                    top_left,
                    bottom_right,
                    diagonal_length,
                    0.00003
                )

                self.add_constraint(
                    top_right,
                    bottom_left,
                    diagonal_length,
                    0.00003
                )

    def add_bending_constraints(self):

        bending_length = self.spacing * 2

        for y in range(self.grid_size):

            for x in range(self.grid_size):

                current = self.grid[(x, y)]

                if x < self.grid_size - 2:

                    next_body = self.grid[(x + 2, y)]

                    self.add_constraint(
                        current,
                        next_body,
                        bending_length,
                        0.0001
                    )

                if y < self.grid_size - 2:

                    next_body = self.grid[(x, y + 2)]

                    self.add_constraint(
                        current,
                        next_body,
                        bending_length,
                        0.0001
                    )

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = pygame.mouse.get_pos()

            mouse_position = Vector2(
                mouse_x,
                mouse_y
            )

            self.selected_body = (
                self.find_body_at_position(
                    mouse_position
                )
            )

        elif event.type == pygame.MOUSEBUTTONUP:

            self.selected_body = None

    def draw(self, renderer):

        self.world.draw(renderer)

        text = renderer.font.render(
            f"Bodies: {len(self.bodies)}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )